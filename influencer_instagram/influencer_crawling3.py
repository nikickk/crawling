import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

# 크롬 드라이버 경로 설정 (경로 확인)
CHROME_DRIVER_PATH = r"/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/chromedriver-mac-x64/chromedriver"

# Selenium 설정
options = webdriver.ChromeOptions()
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

def scrape_top_posts(profile_url, max_posts=5):
    driver.get(profile_url)
    time.sleep(random.uniform(4, 6))  # 페이지 로드 대기

    # 페이지 스크롤하여 게시물 로드
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))  # 로딩 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 게시물 로드
    try:
        posts = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._aagw"))
        )
    except TimeoutException:
        print("게시물을 찾을 수 없습니다. 페이지 로드 문제 발생.")
        return []

    results = []
    for index, post in enumerate(posts[:max_posts]):
        try:
            # 각 게시물의 좋아요 및 댓글 수 가져오기
            actions = ActionChains(driver)
            actions.move_to_element(post).perform()  # Hover 동작
            time.sleep(random.uniform(2, 4))  # 추가 대기

            likes = post.find_element(By.XPATH, ".//ul/li[1]/span/span").text
            comments = post.find_element(By.XPATH, ".//ul/li[2]/span/span").text
            results.append({"likes": likes, "comments": comments})
            print(f"Post {index + 1}: Likes = {likes}, Comments = {comments}")

        except Exception as e:
            print(f"Post {index + 1}: Error retrieving data: {e}")
            results.append({"likes": None, "comments": None})

    return results

    for index, post in enumerate(posts[:max_posts]):
        actions = ActionChains(driver)
        actions.move_to_element(post).perform()  # Hover 동작

        try:
            likes_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//ul/li[1]/span/span"))
            )
            likes = likes_element.text
            try:
                comments_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//ul/li[2]/span/span"))
                )
                comments = comments_element.text
            except Exception:
                comments = 0

            results.append({
                "post_index": index + 1,
                "likes": likes,
                "comments": comments
            })

            print(f"Post {index + 1}: Likes = {likes}, Comments = {comments}")

        except Exception as e:
            print(f"Post {index + 1}: Error retrieving data: {str(e)}")
            results.append({
                "post_index": index + 1,
                "likes": "정보를 가져올 수 없음",
                "comments": f"정보를 가져올 수 없음: {str(e)}"
            })

        # 게시물 처리 후 랜덤 대기 시간 주기
        time.sleep(random.uniform(3, 5))

    return results

if __name__ == "__main__":
    # CSV 파일에서 데이터 읽기
    csv_file_path = r"/Users/lovelyjoo/개발/Github/Github_joo_loves_/crawling/influencer_instagram/influencer_following.csv"  # CSV 파일 경로
    accounts = pd.read_csv(csv_file_path)

    # CSV 파일에 헤더가 이미 존재할 수 있기 때문에, 첫 번째 프로필을 처리할 때만 헤더를 쓴다.
    output_file = "instagram_scrape_results.csv"

    # 프로필 하나씩 처리 후 실시간으로 CSV에 저장
    for index, row in accounts.iterrows():
        profile_name = row['value']  # 계정 이름 (예: 'username')
        profile_url = row['href']  # 프로필 링크 (예: 'https://www.instagram.com/username/')

        print(f"Scraping profile: {profile_name}")
        data = scrape_top_posts(profile_url, max_posts=5)

        all_data = []
        for post_data in data:
            all_data.append({
                "profile_name": profile_name,
                "post_index": post_data["post_index"],
                "likes": post_data["likes"],
                "comments": post_data["comments"]
            })

        # 결과를 DataFrame으로 변환
        results_df = pd.DataFrame(all_data)

        # 프로필 하나씩 결과 CSV로 저장 (헤더는 처음 한 번만 작성, 이어쓰기로 저장)
        results_df.to_csv(output_file, mode='a', header=not pd.io.common.file_exists(output_file), index=False, encoding="utf-8-sig")

        print(f"Data saved for profile: {profile_name}")

    driver.quit()