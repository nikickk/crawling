from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Selenium WebDriver 시작
driver = webdriver.Chrome()

# 원래 URL
original_url = "https://www.nike.com/kr/w/men-running-shoes-37v7jznik1zy7ok"
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

    for n in range(9, total_divs + 1):
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

            # 리뷰버튼(첫번째 버튼) 찾고 클릭 (리뷰 열기)
            first_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/summary'))
            )
            first_button.click()
            time.sleep(3)  # 첫 번째 버튼 클릭 후 대기
            print("첫 번째 버튼 클릭 성공")
            
            # 리뷰 더보기(두번째 버튼) 클릭
            # 리뷰 없을 경우 처리 추가하기(첫번째 버튼만 눌릴 경우)
            # second_button = WebDriverWait(driver, 3).until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/div/div/div/button[2]'))
            # )

            # second_button.click()
            # time.sleep(3)  # 두 번째 버튼 클릭 후 대기
            # print("두 번째 버튼 클릭 성공")
            
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

            # 리뷰 데이터 가져오기 - 리뷰 없을 경우 처리 추가하기(첫번째 버튼만 눌릴 경우)
            reviews_section = soup.find_all('span', class_='tt-c-review__text-content')
            for index, review in enumerate(reviews_section):
                print(f"[{index}] {review.get_text()}")

        except Exception as e:
            print(f"n={n} 크롤링 중 에러 발생:", e)

        # 원래 URL로 복귀
        driver.get(original_url)
        # 추가
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-products"]'))
        )
        
        
        time.sleep(5)  # 복귀 후 대기
        print("원래 URL로 복귀 완료")

except Exception as e:
    print("하위 div 개수를 찾는 중 에러 발생:", e)

# 브라우저 종료
driver.quit()
