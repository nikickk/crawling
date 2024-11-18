from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Selenium WebDriver 시작
driver = webdriver.Chrome()

# 나이키 페이지로 이동
url = "https://www.nike.com/kr/t/%EC%A4%8C-%EB%B3%B4%EB%A9%94%EB%A1%9C-%EB%A1%AC-%EB%82%A8%EC%84%B1-%EC%9C%88%ED%84%B0%EB%9D%BC%EC%9D%B4%EC%A6%88%EB%93%9C-%EC%8A%88%EC%A6%88-LuhQXM8N/FV2295-001"
driver.get(url)

# 페이지 로드 대기
driver.implicitly_wait(5)

# 스크롤 내리기 (맨 아래로)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)  # 스크롤 후 대기 (데이터 로드 시간)


# 버튼 찾고 클릭
# try:
#     load_more_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CLASS_NAME, 'nds-btn mb12-sm css-2lnvjn ex41m6f0 cta-primary-dark underline btn-responsive'))
#     )
#     load_more_button.click()
#     time.sleep(3)  # 버튼 클릭 후 대기 (리뷰가 로드될 시간)
# except Exception as e:
#     print("버튼을 찾을 수 없거나 클릭할 수 없습니다.", e)

# 페이지 소스를 가져와서 BeautifulSoup로 파싱
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 리뷰 데이터 가져오기
reviews_section = soup.find_all('div', class_='content')  # 상위 div 태그 클래스
for div in reviews_section:
    # div 태그 내의 p 태그 찾기
    reviews = div.find_all('p', class_='nds-text css-qtj9g7 e1yhcai00 appearance-body1 color-primary weight-regular')
    for review in reviews:
        print(review.get_text())

# 브라우저 종료
driver.quit()
