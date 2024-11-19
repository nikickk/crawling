from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 로그인 URL로 이동
driver.get('https://instagram.com/accounts/login/')
time.sleep(3)

# 로그인
login_id = driver.find_element(By.NAME, "username")
login_pwd = driver.find_element(By.NAME, "password")
login_id.send_keys('influ_encert')  # 아이디 입력
login_pwd.send_keys('Tkekdehd2@')  # 비밀번호 입력
login_pwd.submit()
time.sleep(5)

# 로그인 성공 여부 확인
current_url = driver.current_url
if "challenge" in current_url or "login" in current_url:
    print("Login failed. Check credentials or security checks.")
    driver.quit()

# 해시태그 검색 URL로 이동
word = '나이키'
url = f'https://www.instagram.com/explore/tags/{word}/'
driver.get(url)

# 페이지 로딩 확인
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div._aagw"))
    )
    print("Page loaded successfully.")
except Exception as e:
    print(f"Error while loading hashtag page: {e}")

