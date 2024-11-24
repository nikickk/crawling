import pandas as pd

# 기존 CSV 파일 읽기 (기존 인코딩으로 읽기, 예시로 'utf-8'을 사용)
df = pd.read_csv("nike_homepage/shoe_reviews.csv", encoding="utf-8")

# 새로운 인코딩으로 CSV 파일 저장하기 (cp949)
df.to_csv("nike_homepage/shoe_reviews.csv", encoding="utf-8-sig", index=False)
