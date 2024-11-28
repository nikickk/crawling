import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import rc

# 한글 폰트 설정 (Windows 기준)
rc('font', family='Malgun Gothic')

# 파일 경로
file_path = r'C:\Tave2\Processed_Nike_data_review.csv'

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 3번째 컬럼 데이터 추출
third_column_data = df.iloc[:, 2]  # 3번째 컬럼

# 단어 리스트 생성
all_words = []
for text in third_column_data:
    if pd.notna(text):  # NaN 값 제외
        all_words.extend(str(text).split())

# 단어 빈도 계산
word_counts = Counter(all_words)

# 워드 클라우드 생성
wordcloud = WordCloud(
    font_path='malgun.ttf',  # 한글 폰트 경로 (Windows: Malgun Gothic)
    background_color='white',
    width=800,
    height=400,
    max_words=200,
    colormap='viridis'
).generate_from_frequencies(word_counts)

# 워드 클라우드 시각화
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('워드 클라우드', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(r'C:\Tave2\wordcloud_output.png')  # 이미지 저장
plt.show()

print("워드 클라우드가 생성되고 저장되었습니다: C:\\Tave2\\Nike_insta_post_wordcloud.png")
