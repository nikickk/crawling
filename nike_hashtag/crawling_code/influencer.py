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
from io import BytesIO  # 누락된 경우


# Tesseract 경로 설정
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# Selenium 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_instagram(driver, username, password):
    driver.get('https://instagram.com/accounts/login/')
    time.sleep(3)
    
    # 사용자명과 비밀번호 입력
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    
    # 로그인 버튼 클릭
    driver.find_element(By.CSS_SELECTOR, "button._acan._acap._acas._aj1-._ap30").click()
    
    time.sleep(5)  # 페이지 로드 대기
    print("Login successful.")


# 공통 유틸 함수
def wait_for_element(driver, css_selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
def get_post_image_url(driver):
    try:
        img_tag = driver.find_element(By.CSS_SELECTOR, '._aatk .x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3')
        if img_tag:
            return img_tag.get_attribute("src")
        else:
            print("Image not found.")
            return None
    except Exception as e:
        print(f"Error finding image URL: {e}")
        return None


def contains_text(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_np = np.array(image)
    text = pytesseract.image_to_string(image_np, lang='eng')
    return len(text.strip()) > 10

def contains_person(image_url):
    try:
        # Haar Cascade 로드
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # 이미지 다운로드 및 전처리
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # 얼굴 탐지
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        print(f"[DEBUG] Faces detected: {len(faces)} | URL: {image_url}")

        # 디버깅을 위해 이미지 표시
        for (x, y, w, h) in faces:
            cv2.rectangle(image_bgr, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Detected Faces", image_bgr)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

        return len(faces) > 0
    except Exception as e:
        print(f"Person detection error (Haar Cascade): {e}")
        return False

def follow_user(driver):
    try:
        # 버튼 요소 찾기
        follow_button = wait_for_element(driver, '#mount_0_0_\\+A > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div:nth-child(2) > div > div.x1gryazu.xh8yej3.x10o80wk.x14k21rp.x17snn68.x6osk4m.x1porb0y.x8vgawa > section > main > div > header > section > div.x6s0dn4.x78zum5.x1q0g3np.xs83m0k.xeuugli.x1n2onr6.xxz05av.xkfe5hh > div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1n2onr6.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > div > div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1i64zmx.x1n2onr6.x1plvlek.xryxfnj.x1iyjqo2.x2lwn1j.xeuugli.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > button')
    
        # 버튼 텍스트 확인 및 클릭
        if follow_button.text.lower() in ["follow", "팔로우"]:
            follow_button.click()
            print("User followed successfully.")
            time.sleep(2)
        else:
            print("Already followed or button not available.")
    except Exception as e:
        print(f"Error during follow: {e}")



def is_personal_influencer(driver):
    try:
        # 1. 게시물 사진 URL 가져오기
        image_url = get_post_image_url(driver)
        if not image_url or contains_text(image_url) or not contains_person(image_url):
            print("Filtered due to image conditions.")
            print(image_url)
            return False

        # 2. 사용자 이름 클릭하여 계정 페이지로 이동 (새 창에서 열기)
        username_element = wait_for_element(driver, 'header > div > div > div > a')
        ActionChains(driver).key_down(Keys.COMMAND).click(username_element).key_up(Keys.COMMAND).perform()

        # 3. 새 창으로 전환
        time.sleep(2)  # 새 창 로드 대기
        driver.switch_to.window(driver.window_handles[-1])  # 새로 열린 창으로 이동

        # 4. 팔로워 수 가져오기
        followers_element = wait_for_element(driver, 'header section ul li:nth-child(2) a span')
        followers_text = followers_element.text
        print(f"[DEBUG] Followers text: {followers_text}")

        # 팔로워 수 계산
        followers = 0
        if "만" in followers_text:
            parts = followers_text.split("만")
            whole = int(parts[0]) * 10000
            decimal = int(parts[1]) * 100 if len(parts) > 1 else 0
            followers = whole + decimal
        else:
            followers = int(re.sub(r'[^\d]', '', followers_text))

        print(f"Followers count: {followers}")

        # 5. 팔로워 조건 확인
        if not (1000 <= followers <= 50000):
            print(f"Account does not meet the follower criteria. Followers: {followers}")
            driver.close()  # 새 창 닫기
            driver.switch_to.window(driver.window_handles[0])  # 원래 창으로 전환
            return False

        # 6. 팔로우 버튼 클릭
        follow_user(driver)

        # 새 창 닫기 및 원래 창으로 복귀
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return True
    except Exception as e:
        print(f"Error during influencer validation: {e}")
        # 오류 발생 시 새 창 닫기 및 원래 창 복귀
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
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
    try:
        next_button = wait_for_element(driver, 'div._aaqg._aaqh button._abl-')
        next_button.click()
        print("[DEBUG] Moved to the next post.")
        time.sleep(3)
    except Exception as e:
        print(f"Error moving to the next post: {e}")

# 실행
login_instagram(driver, "influ_encert", "Tkekdehd2@")
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