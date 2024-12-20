from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

data_array=[]
shoe_list=[]
review_list_total=[]

# Selenium WebDriver 시작
driver = webdriver.Chrome()

# 원래 URL
original_url = "https://www.nike.com/kr/w/men-jordan-shoes-37eefznik1zy7ok"
driver.get(original_url)

# 페이지 로드 대기
driver.implicitly_wait(5)

# 스크롤 내리기 (맨 아래로)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

# '//*[@id="skip-to-products"]' 하위의 div 개수 확인
try:
    skip_to_products = driver.find_element(By.XPATH, '//*[@id="skip-to-products"]')
    child_divs = skip_to_products.find_elements(By.XPATH, './div')  # 자식 div 요소들
    total_divs = len(child_divs)  # 총 개수
    print(f"총 {total_divs}개의 div 요소를 찾았습니다.")

    for n in range(1, total_divs + 1):
        print("지금 순서 : ",n)

        if n == 2:  # n=2는 제외
            print(f"n={n} 제외됨")
            continue

        # XPath 생성
        xpath = f'//*[@id="skip-to-products"]/div[{n}]/div/figure'
        print(f"현재 XPath: {xpath}")

        try:
            # 해당 요소 클릭
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            time.sleep(5)  # 페이지 전환 대기
            print(f"n={n} 요소 클릭 성공")
            
            # 페이지 소스를 가져와서 BeautifulSoup로 파싱
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 상품명 데이터 가져오기
            shoe_name = soup.find('h1', class_='nds-text css-1h3ryhm e1yhcai00 text-align-start appearance-title4 color-primary weight-regular')
            print(shoe_name.text)
            shoe_list.append(shoe_name.text)

            # 리뷰버튼(첫번째 버튼) 찾고 클릭 (리뷰 열기)
            first_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/summary'))
            )
            first_button.click()
            time.sleep(3)  # 첫 번째 버튼 클릭 후 대기
            print("첫 번째 버튼 클릭 성공")
            
            # 두 번째 버튼 클릭 (없으면 건너뛰기)
            from selenium.common.exceptions import TimeoutException

            try:
                second_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/div/div/div/button[2]'))
                )
                second_button.click()
                time.sleep(3)
                print("두 번째 버튼 클릭 성공")
            except TimeoutException:
                print("두 번째 버튼이 없거나 비활성화되어 있습니다. 건너뜁니다.")

            # 페이지 소스를 가져와서 BeautifulSoup로 파싱
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # 리뷰 데이터 가져오기
            reviews_section = soup.find_all('span', class_='tt-c-review__text-content')
            review_list = []  # 리뷰를 담을 리스트
            for index, review in enumerate(reviews_section):
                print(f"[{index}] {review.get_text()}")
                review_list.append(review.get_text())  # 각 리뷰를 리스트로 감싸서 추가

            # 리뷰 리스트를 review_list_total에 추가
            review_list_total.append(review_list)
                

        except Exception as e:
            print(f"n={n} 크롤링 중 에러 발생:", e)

        # 원래 URL로 복귀 (DOM 안정화 대기)
        driver.get(original_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-products"]'))
        )
        time.sleep(5)  # 복귀 후 대기
        print("원래 URL로 복귀 완료")

except Exception as e:
    print("하위 div 개수를 찾는 중 에러 발생:", e)

# 브라우저 종료
driver.quit()
data_array.append([shoe_list,review_list_total])
print(data_array)

import pandas as pd

# 각 제품의 이름
product_names = data_array[0][0]

# 각 제품에 대한 리뷰들
reviews_data = data_array[0][1]

# 데이터프레임으로 변환
reviews_df = pd.DataFrame(reviews_data, columns=[f'Review {i+1}' for i in range(len(reviews_data[0]))])

# 제품 이름을 인덱스로 설정
reviews_df.insert(0, 'Product', product_names)

# 결과 출력
print(reviews_df)

reviews_df.to_csv("nike_homepage(joo)/shoe_reviews.csv",encoding="cp949",index=False)