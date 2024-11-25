from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Selenium WebDriver 시작
driver = webdriver.Chrome()

# 기본 URL 설정 (Jordan 카테고리 첫 페이지)
base_url = "https://www.nike.com/kr/w/men-jordan-shoes-37eefznik1zy7ok"

# 리뷰 데이터를 저장할 리스트
result_list = []

def close_popups():
    """팝업 닫기 또는 제거."""
    try:
        # 팝업 닫기 버튼 클릭 시도
        popup_close_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'bluecoreLowerRightPopup'))
        )
        driver.execute_script("arguments[0].style.display = 'none';", popup_close_button)
        print("팝업 제거 완료.")
    except Exception:
        # 팝업이 없거나 제거할 수 없는 경우
        print("팝업 제거할 필요 없음.")

try:
    current_page = 1  # 시작 페이지
    while True:
        print(f"현재 페이지: {current_page}")
        driver.get(f"{base_url}?page={current_page}")
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

            for n in range(1, total_divs + 1):
                if n == 2:  # n=2는 제외
                    print(f"n={n} 제외됨")
                    continue

                # XPath 생성
                xpath = f'//*[@id="skip-to-products"]/div[{n}]/div/figure'
                print(f"현재 XPath: {xpath}")

                try:
                    # 팝업 제거 시도
                    close_popups()

                    # 해당 요소 클릭
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    element.click()
                    time.sleep(5)  # 페이지 전환 대기
                    print(f"n={n} 요소 클릭 성공")

                    # 리뷰 섹션 열기
                    try:
                        first_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/summary')
                            )
                        )
                        # 가려진 요소 제거
                        driver.execute_script("arguments[0].scrollIntoView(true);", first_button)
                        first_button.click()
                        time.sleep(3)
                        print("첫 번째 버튼 클릭 성공")

                        # 리뷰 더보기 버튼 클릭
                        try:
                            second_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, '//*[@id="pdp-info-accordions__reviews-accordion"]/div/div/div/button[2]')
                                )
                            )
                            second_button.click()
                            time.sleep(3)
                            print("두 번째 버튼 클릭 성공")
                        except Exception as e:
                            print(f"리뷰 더보기 버튼 없음: {e}")

                        # 페이지 별 리뷰 크롤링 반복
                        while True:
                            # 페이지 소스를 가져와서 BeautifulSoup로 파싱
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')

                            # 리뷰 데이터 가져오기
                            reviews_section = soup.find_all('span', class_='tt-c-review__text-content')
                            for index, review in enumerate(reviews_section):
                                review_text = review.get_text()
                                print(f"[{index}] {review_text}")
                                result_list.append({
                                    'Product': f"Page {current_page} Product {n}",
                                    'Review': review_text
                                })

                            # 다음 리뷰 페이지 버튼 클릭
                            try:
                                next_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="tt-reviews-list"]/div/div/nav/ul/li[2]/a'))
                                )
                                next_button.click()
                                time.sleep(3)
                                print("리뷰 다음 페이지로 이동")
                            except Exception as e:
                                print("리뷰 페이지가 끝났습니다.")
                                break

                    except Exception as e:
                        print(f"제품 {n}: 리뷰 섹션 처리 중 에러 - {e}")

                    # 제품 목록으로 복귀
                    driver.get(f"{base_url}?page={current_page}")
                    time.sleep(5)

                except Exception as e:
                    print(f"제품 {n}: 크롤링 실패 - {e}")

            # 다음 페이지로 이동
            try:
                next_page_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[contains(@aria-label, "다음 페이지")]')
                    )
                )
                next_page_button.click()
                current_page += 1
                time.sleep(5)
            except Exception as e:
                print("다음 제품 페이지 버튼이 더 이상 존재하지 않습니다.")
                break

        except Exception as e:
            print("제품 섹션 처리 중 에러 발생:", e)
            break

except Exception as e:
    print("전체 크롤링 중 에러 발생:", e)

finally:
    # 브라우저 종료
    driver.quit()
    print("크롤링 완료 및 브라우저 종료")
    print(f"총 {len(result_list)}개의 리뷰 데이터를 크롤링했습니다.")

    # CSV 저장
    import pandas as pd
    df = pd.DataFrame(result_list)
    df.to_csv('nike_reviews.csv', index=False, encoding='utf-8-sig')
    print("리뷰 데이터가 nike_reviews.csv에 저장되었습니다.")