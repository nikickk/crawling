from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import pytesseract
import requests
from PIL import Image
import numpy as np
import cv2
from io import BytesIO

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Selenium 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 로그인 함수
def login_instagram(driver, username, password):
    driver.get('https://instagram.com/accounts/login/')
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button._acan._acap._acas._aj1-._ap30").click()
    time.sleep(5)
    print("Login successful.")

# 요소 대기 함수
def wait_for_element(driver, selector, timeout=10, by=By.CSS_SELECTOR):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

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

# 게시물 이미지 URL 가져오기
def get_post_image_url(driver):
    try:
        img_tag = driver.find_element(By.CSS_SELECTOR, '._aatk img')
        return img_tag.get_attribute("src") if img_tag else None
    except Exception as e:
        print(f"Error finding image URL: {e}")
        return None

# 게시물 이동
def move_next(driver):
    try:
        next_button = wait_for_element(driver, 'div._aaqg._aaqh button._abl-')
        next_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"Error moving to the next post: {e}")

# 메인 로직
def is_personal_influencer(driver):
    try:
        # 1. 게시물 이미지 가져오기
        image_url = get_post_image_url(driver)
        if not image_url:
            print("No image found, skipping post.")
            return False

        # 2. 사용자 프로필로 이동
        username_element = wait_for_element(driver, 'header div div span a', timeout=20, by=By.CSS_SELECTOR)
        user_profile_url = username_element.get_attribute('href')
        driver.execute_script(f"window.open('{user_profile_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        # 3. 팔로워 수 가져오기
        followers_element = wait_for_element(driver, 'header section ul li:nth-child(2) a span')
        followers_text = followers_element.text
        followers = calculate_followers(followers_text)
        print(f"Followers: {followers}")

        # 4. 조건 확인
        if 1000 <= followers <= 50000:
            follow_user(driver)
            print(f"Qualified account: {followers} followers.")
        else:
            print(f"Disqualified account: {followers} followers.")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return True
    except Exception as e:
        print(f"Error during influencer validation: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False

# 팔로우 함수
def follow_user(driver):
    try:
        follow_button = wait_for_element(driver, 'header section div button', timeout=10)
        if follow_button.text.lower() in ["follow", "팔로우"]:
            follow_button.click()
            print("Followed successfully.")
            time.sleep(2)
        else:
            print("Already following or button not available.")
    except Exception as e:
        print(f"Error during follow: {e}")

# 첫 게시물 선택
def select_first(driver):
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    first_post = wait_for_element(driver, "div._aagw", timeout=10)
    first_post.click()
    time.sleep(3)

# 실행
login_instagram(driver, "influ_encert", "Tkekdehd2@")
search_word = input("검색할 내용을 입력해 주세요: ")
url = f'https://www.instagram.com/explore/tags/{search_word}/'
driver.get(url)
select_first(driver)

target = 50
for i in range(target):
    try:
        if is_personal_influencer(driver):
            print("Qualified user found and followed.")
        move_next(driver)
    except Exception as e:
        print(f"Error at post {i + 1}: {e}")
        driver.get(url)
        time.sleep(5)
        select_first(driver)
