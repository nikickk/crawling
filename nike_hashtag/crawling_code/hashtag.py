from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


def wait_for_element(driver, css_selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


# 크롬 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 로그인
driver.get('https://instagram.com/accounts/login/')
time.sleep(3)

# 로그인 정보 입력
login_id = driver.find_element(By.NAME, "username")
login_pwd = driver.find_element(By.NAME, "password")
login_id.send_keys('influ_encert')
login_pwd.send_keys('Tkekdehd2@')
login_pwd.submit()
time.sleep(5)

# 로그인 성공 여부 확인
if "challenge" in driver.current_url or "login" in driver.current_url:
    print("Login failed. Check credentials or security checks.")
    driver.quit()

# 해시태그 URL 이동
word = '아디다스후기'
url = f'https://www.instagram.com/explore/tags/{word}/'
driver.get(url)

def select_first(driver):
    for attempt in range(3):  # 최대 3번 시도
        try:
            # 페이지가 로드되지 않았을 경우 스크롤
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)

            # 첫 번째 게시물 선택
            first_post = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div._aagw"))  # CSS Selector 확인 필요
            )
            first_post.click()
            print("First post clicked successfully.")
            time.sleep(3)
            return
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error selecting first post: {e}")
            time.sleep(2)  # 잠시 대기 후 재시도
    print("Failed to select first post after retries.")
"""
# 게시물 선택
def select_first(driver):
    try:
        first_post = wait_for_element(driver, "div._aagu", timeout=10)
        first_post.click()
        time.sleep(3)
    except Exception as e:
        print(f"Error selecting first post: {e}")
"""
def get_content(driver):
    # 게시물 텍스트 추출
    try:
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div.xb88tzc.xw2csxc.x1odjw0f.x5fp0pe.x1qjc9v5.xjbqb8w.x1lcm9me.x1yr5g0i.xrt01vj.x10y3i5r.xr1yuqi.xkrivgy.x4ii5y1.x1gryazu.x15h9jz8.x47corl.xh8yej3.xir0mxb.x1juhsu6 > div > article > div > div.x1qjc9v5.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x5wqa0o.xln7xf2.xk390pu.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x65f84u.x1vq45kp.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x11njtxf > div > div > div.x78zum5.xdt5ytf.x1q2y9iw.x1n2onr6.xh8yej3.x9f619.x1iyjqo2.x18l3tf1.x26u7qi.xy80clv.xexx8yu.x4uap5.x18d9i69.xkhd6sd > div.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x2lwn1j.x1odjw0f.x1n2onr6.x9ek82g.x6ikm8r.xdj266r.x11i5rnm.x4ii5y1.x1mh8g0r.xexx8yu.x1pi30zi.x18d9i69.x1swvt13 > ul > div.x1qjc9v5.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x78zum5.xdt5ytf.x2lah0s.xk390pu.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.xggy1nq.x11njtxf > li > div > div > div._a9zr'))  # 업데이트된 셀렉터 입력
        ).text
    except:
        content = ''  # 텍스트가 없는 경우 빈 문자열

    # 해시태그 추출
    tags = re.findall(r'#[^\s#,\\]+', content)


    # 결과 데이터 반환
    data = [content,  tags]
    print(f"Scraped Data: {data}")
    return data


# 다음 게시물로 이동
def move_next(driver):
    try:
        next_button = wait_for_element(driver, 'body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div:nth-child(1) > div > div > div._aaqg._aaqh > button', timeout=10)
        next_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"Error moving to next post: {e}")

import pandas as pd

# 크롤링 시작
results = []
target = 1000

select_first(driver)
# 중복 방지용 URL 저장
collected_urls = set()

# 현재 게시물 URL 저장 변수
current_url = None

# 크롤링 시작
results = []
target = 200

select_first(driver)  # 첫 게시물 선택

for i in range(target):
    try:
        # 현재 게시물 URL 저장
        current_url = driver.current_url

        # 게시물 데이터 수집
        data = get_content(driver)

        # 중복 확인
        if current_url in collected_urls:
            print(f"Duplicate post detected: {current_url}")
            continue  # 중복된 게시물은 건너뜀

        # 중복이 아니면 데이터 저장
        if data:
            collected_urls.add(current_url)  # URL 기록
            results.append(data)

        # 10번째 게시물마다 데이터 저장
        if i % 10 == 0:
            result_df = pd.DataFrame(results, columns=['content',  'tags'])
            result_df.to_csv('adidas_data_review.csv', index=False)
            print(f"Saved {len(results)} posts to 'adidas_data_review.csv'")

        # 다음 게시물로 이동
        move_next(driver)

    except Exception as e:
        # 예외 발생 시 세션 복구
        print(f"Error during scraping at post {i + 1}: {e}. Attempting to recover...")
        driver.get(current_url)  # 마지막 URL로 복구
        time.sleep(5)
        continue

# 최종 데이터 저장
result_df = pd.DataFrame(results, columns=['content', 'tags'])
result_df.to_csv('adidas_data_review.csv', index=False)
print("Final data saved to 'instagram_data_review.csv'")

