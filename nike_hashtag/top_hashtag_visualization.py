import pandas as pd
import ast  # 안전한 문자열 평가를 위해 사용
from collections import Counter
import matplotlib.pyplot as plt

# 데이터 로드
path = r"C:\Tave2\adidas_data.csv"
c_df = pd.read_csv(path, encoding='utf-8')

# 광고성 해시태그 제거
remov = []
ad = ["#광고", "#유료광고", "#제품증정광고", "#제품협찬", "#협찬"]

# 제외할 단어 리스트 추가
exclude_words = ["#아디다스"]

# 해시태그 열을 리스트로 변환
all_hashtags = []  # 모든 해시태그를 모으는 리스트

for i in range(len(c_df)):
    try:
        # 문자열을 리스트로 변환
        hashtags = ast.literal_eval(c_df.iloc[i, 1])
        
        # 광고성 해시태그 확인
        if any(tag in ad for tag in hashtags):
            remov.append(i)  # 광고성 포함 행 추가
        else:
            all_hashtags.extend(hashtags)  # 광고성 제외 해시태그 추가
    except Exception as e:
        print(f"Error processing row {i}: {e}")

# 광고성 해시태그 포함된 행 제거
filtered_docs = c_df.drop(remov).reset_index(drop=True)

# 해시태그 빈도수 계산 (제외할 단어를 필터링)
filtered_hashtags = [tag for tag in all_hashtags if tag not in exclude_words]
hashtag_counts = Counter(filtered_hashtags)

# 상위 20개 해시태그 추출
top_hashtags = hashtag_counts.most_common(30)

# 데이터프레임으로 변환 (시각화용)
df_top_hashtags = pd.DataFrame(top_hashtags, columns=["Hashtag", "Count"])

# 빈도수 출력
print(df_top_hashtags)

# 빈도수 시각화
plt.figure(figsize=(12, 8))
plt.bar(df_top_hashtags["Hashtag"], df_top_hashtags["Count"])
plt.xticks(rotation=45, ha="right", fontname='Malgun Gothic')  # 한글 폰트 적용
plt.xticks(rotation=45, ha="right")
plt.title("Top 20 Hashtags Frequency")
plt.xlabel("Hashtag")
plt.ylabel("Frequency")
plt.tight_layout()
# 그래프를 이미지 파일로 저장 (PNG 형식)
plt.savefig("아디다스해시태그.png", dpi=300, bbox_inches='tight')  # DPI: 해상도 설정
plt.show()