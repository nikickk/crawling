import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import requests
import re

# 크롬 드라이버 경로 설정
CHROME_DRIVER_PATH = r"/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/chromedriver-mac-x64/chromedriver"

# 이미지 저장 폴더
IMAGE_SAVE_PATH = "profile_images"
os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)

# Selenium 설정
options = webdriver.ChromeOptions()
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

def sanitize_filename(filename):
    """파일 이름에 허용되지 않는 문자 제거"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def scrape_top_posts(profile_url, profile_name, max_posts=5):
    try:
        driver.get(profile_url)
        time.sleep(5)  # 초기 대기 시간

        # 프로필 이미지 URL 추출
        profile_image_element = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[class*='xpdipgo']"))
        )
        profile_image_url = profile_image_element.get_attribute("src")

        # 이미지 다운로드
        sanitized_name = sanitize_filename(profile_name)
        image_file_name = f"{sanitized_name}.jpg"
        image_file_path = os.path.join(IMAGE_SAVE_PATH, image_file_name)
        with open(image_file_path, "wb") as file:
            file.write(requests.get(profile_image_url).content)

        results = []
        loaded_posts = []

        # 최소 max_posts 만큼의 게시물이 로드될 때까지 스크롤
        scroll_attempts = 0
        while len(loaded_posts) < max_posts and scroll_attempts < 15:
            loaded_posts = driver.find_elements(By.CSS_SELECTOR, "div[class*='_aagw']")

            if len(loaded_posts) >= max_posts:
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            scroll_attempts += 1

        if len(loaded_posts) < max_posts:
            print(f"Only {len(loaded_posts)} posts loaded. Proceeding with available posts.")

        loaded_posts = loaded_posts[:max_posts]

        for index, post in enumerate(loaded_posts):
            actions = ActionChains(driver)
            actions.move_to_element(post).perform()
            time.sleep(random.uniform(1, 2))

            try:
                likes_element = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located((By.XPATH, "//ul/li[1]/span/span"))
                )
                likes = likes_element.text

                try:
                    comments_element = WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located((By.XPATH, "//ul/li[2]/span/span"))
                    )
                    comments = comments_element.text
                except Exception:
                    comments = 0

                results.append({
                    "likes": likes,
                    "comments": comments
                })

                print(f"Post {index + 1}: Likes = {likes}, Comments = {comments}")

            except Exception as e:
                results.append({
                    "likes": "정보를 가져올 수 없음",
                    "comments": f"정보를 가져올 수 없음: {str(e)}"
                })
                print(f"Post {index + 1}: Error retrieving data: {str(e)}")

            time.sleep(random.uniform(3, 5))

        return results, profile_image_url, image_file_path

    except Exception as e:
        print(f"Error accessing profile {profile_url}: {str(e)}")
        return [{"likes": "추후에 다시", "comments": "추후에 다시"}], None, None

if __name__ == "__main__":
    csv_file_path = r"/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/influencer_following_with_followers.csv"
    accounts = pd.read_csv(csv_file_path)

    # 입력: 특정 행들 또는 시작 행 번호
    user_input = input("크롤링할 행 번호를 입력하세요 (예: 0 또는 01,12,14): ")

    if "," in user_input:
        # 특정 행들 크롤링
        row_indices = [int(i.strip()) for i in user_input.split(",") if i.strip().isdigit()]
    else:
        # 단일 행 번호부터 시작
        start_index = int(user_input.strip())
        row_indices = list(range(start_index, len(accounts)))

    output_file = "instagram_scrape_results(final).csv"
    all_profiles_data = []

    for index in row_indices:
        if index >= len(accounts):
            print(f"Index {index} is out of range. Skipping...")
            continue

        row = accounts.iloc[index]
        profile_name = row['value']
        profile_url = row['href']

        print(f"Scraping profile: {profile_name}")
        data, profile_image_url, profile_image_path = scrape_top_posts(profile_url, profile_name, max_posts=5)

        profile_data = {"profile_name": profile_name}
        for i, post_data in enumerate(data):
            profile_data[f"like_{i+1}"] = post_data["likes"]
            profile_data[f"comment_{i+1}"] = post_data["comments"]

        profile_data["profile_image_url"] = profile_image_url
        profile_data["profile_image_path"] = profile_image_path

        all_profiles_data.append(profile_data)
        print(f"Data collected for profile: {profile_name}")
        print(profile_data)

        pd.DataFrame(all_profiles_data).to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"All data saved to {output_file}")
    driver.quit()