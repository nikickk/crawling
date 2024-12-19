from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import pytesseract
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import mediapipe as mp

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 설정 함수
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
login_id = driver.find_element(By.NAME, "username")
login_pwd = driver.find_element(By.NAME, "password")
login_id.send_keys('influ_encert')
login_pwd.send_keys('Tkekdehd2@')
login_pwd.submit()
time.sleep(5)

# 이미지 분석 함수
def contains_text(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_np = np.array(image)
    text = pytesseract.image_to_string(image_np, lang='eng')
    return len(text.strip()) > 10

def contains_person(image_url):
    try:
        # 이미지 다운로드 및 로드
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(image)

        # Mediapipe 얼굴 탐지 초기화
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        # 얼굴 탐지 수행
        results = face_detection.process(image_np)
        face_count = len(results.detections) if results.detections else 0

        print(f"Faces detected: {face_count}")
        return face_count > 0  # 얼굴이 하나라도 탐지되면 True
    except Exception as e:
        print(f"Person detection error: {e}")
        return False

def get_post_image_url(driver):
    try:
        img_tag = wait_for_element(driver, 'img.x5yr21d', timeout=10)
        image_url = img_tag.get_attribute("src")
        if image_url:
            print(f"Image URL: {image_url}")
            return image_url
        else:
            print("Image URL not found")
            return None
    except Exception as e:
        print(f"Error finding image URL: {e}")
        return None

def follow_user(driver):
    try:
        follow_button = wait_for_element(driver, "button._acan._acap._acas._aj1-")
        if follow_button.text.lower() == "follow" or follow_button.text.lower() == "팔로우":
            follow_button.click()
            print("User followed successfully.")
            time.sleep(2)
        else:
            print("Already followed or button not available.")
    except Exception as e:
        print(f"Error during follow: {e}")

def is_personal_influencer(driver):
    try:
        image_url = get_post_image_url(driver)
        if not image_url or contains_text(image_url) or not contains_person(image_url):
            print("Filtered due to image conditions.")
            return False

        username = wait_for_element(driver, 'header a.sqdOP').text
        driver.find_element(By.CSS_SELECTOR, 'header a.sqdOP').click()
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        bio = soup.find('div', {'class': '-vDIg'}).text if soup.find('div', {'class': '-vDIg'}) else ""
        followers_text = soup.find('span', {'class': '_ac2a'}).text
        followers = int(re.sub(r'[^\d]', '', followers_text))

        print(f"Checking user: {username}, Bio: {bio}, Followers: {followers}")
        if any(keyword in bio.lower() for keyword in ["official", "store", "shop", "ad"]) or not (1000 <= followers <= 50000):
            print("Filtered due to bio or follower count.")
            driver.back()
            return False

        follow_user(driver)
        driver.back()
        return True
    except Exception as e:
        print(f"Error during filtering: {e}")
        driver.back()
        return False

def select_first(driver):
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    first_post = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div._aagw"))
    )
    first_post.click()
    time.sleep(3)

def move_next(driver):
    next_button = wait_for_element(driver, 'body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div:nth-child(1) > div > div > div._aaqg._aaqh > button', timeout=10)
    next_button.click()
    time.sleep(3)

word = input("검색할 내용을 입력해 주세요: ")
url = f'https://www.instagram.com/explore/tags/{word}/'
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
