import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# JSON 파일 경로
json_file_path = r'/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/following.json'  # JSON 파일 경로 수정

# JSON 파일 읽기
with open(json_file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# JSON 데이터에서 href 및 value 추출
records = []
for entry in json_data.get('relationships_following', []):
    for string_list_data in entry.get('string_list_data', []):
        records.append({
            'href': string_list_data.get('href', ''),
            'value': string_list_data.get('value', '')
        })

# pandas DataFrame 생성
df = pd.DataFrame(records)

# Selenium 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 팔로워 수 계산 함수
def calculate_followers(followers_text):
    if "만" in followers_text:
        parts = followers_text.split("만")
        whole, decimal = 0, 0
        if '.' in parts[0]:
            decimal_parts = parts[0].split('.')
            whole = int(decimal_parts[0]) * 10000 if decimal_parts[0].strip() else 0
            decimal = int(decimal_parts[1]) * (10 ** (4 - len(decimal_parts[1]))) if len(decimal_parts) > 1 and decimal_parts[1].strip() else 0
        else:
            whole = int(parts[0]) * 10000 if parts[0].strip() else 0
        return whole + decimal
    return int(re.sub(r'[^\d]', '', followers_text))

# 팔로워 수 가져오는 함수
def get_followers_count(driver, profile_url):
    try:
        driver.get(profile_url)
        time.sleep(3)
        followers_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'header section ul li:nth-child(2) a span'))
        )
        followers_text = followers_element.text
        return calculate_followers(followers_text)
    except Exception as e:
        print(f"Error fetching followers for {profile_url}: {e}")
        return None

# Instagram 로그인 함수
def login_instagram(driver, username, password):
    driver.get('https://instagram.com/accounts/login/')
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button._acan._acap._acas._aj1-._ap30").click()
    time.sleep(5)
    print("Login successful.")

# Instagram 로그인
login_instagram(driver, "influ_encert", "Tkekdehd2@")  # 로그인 정보 수정

# 각 프로필의 팔로워 수 가져오기
followers_list = []
for index, row in df.iterrows():
    profile_url = row['href']
    print(f"Fetching followers for: {profile_url}")
    followers_count = get_followers_count(driver, profile_url)
    followers_list.append(followers_count)
    print(f"Followers: {followers_count}")

# DataFrame에 팔로워 수 추가
df['followers'] = followers_list

# 결과를 CSV로 저장
csv_file_path = r'/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/influencer_following_with_followers.csv'  # 저장할 CSV 파일 경로
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"CSV 파일이 생성되었습니다: {csv_file_path}")