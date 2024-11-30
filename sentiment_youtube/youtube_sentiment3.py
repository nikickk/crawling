import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import matplotlib.font_manager as fm  # 폰트 설정을 위해 추가
from transformers import pipeline
import torch

# 1. 데이터 로드
file_path = "nike_youtube_crawling(fix).csv"  # 파일 경로
df = pd.read_csv(file_path)

# 2. 데이터 전처리
okt = Okt()
df['cleaned_comments'] = df['comment'].str.replace(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", regex=True)  # 한글과 공백만 남기기

# 불용어 리스트 정의 (한국어 불용어 예시)
stopwords = set([
    "그리고", "하지만", "그래서", "또한", "즉", "왜냐하면", "때문에", "때문", "무슨", "그게",
    "이것", "저것", "그것", "너무", "정말", "매우", "아주", "어느", "이", "저", "그",
    "점점", "계속", "다른", "일단", "바로", "가장", "이후", "어디", "부터", "년도", "이상", "등등",
    "정도", "절대", "조금", "거의", "사서", "사고"
])

# 3. 감정 분석 파이프라인 설정
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="beomi/KcELECTRA-base",
    device=-1  # CPU 모드로 실행
)

# 최대 토큰 길이 설정 (모델의 최대 허용 길이에 따라 조정)
MAX_LENGTH = 512

# 4. 단어 리스트 초기화
positive_words = []
negative_words = []

# 5. 데이터 처리 루프
for comment in df['cleaned_comments']:
    if not comment.strip():  # 비어 있는 댓글은 무시
        continue

    # 텍스트 길이를 MAX_LENGTH로 제한
    if len(comment.split()) > MAX_LENGTH:
        comment = ' '.join(comment.split()[:MAX_LENGTH])
    
    result = sentiment_analyzer(comment)  # 텍스트를 직접 파이프라인에 입력
    print(f"Comment: {comment} -> Sentiment: {result}")

    # 긍정적/부정적 단어 추출 로직
    if result[0]['label'] == 'POSITIVE':
        positive_words.extend([word for word in okt.nouns(comment) if word not in stopwords])
    elif result[0]['label'] == 'NEGATIVE':
        negative_words.extend([word for word in okt.nouns(comment) if word not in stopwords])

# 6. 중복 제거 및 단어 리스트 정리
positive_words = list(set(positive_words))
negative_words = list(set(negative_words))

# 7. 긍정적 단어 워드클라우드 생성
if positive_words:
    positive_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(positive_words))
    plt.figure(figsize=(10, 5))
    plt.imshow(positive_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Positive Words WordCloud')
    plt.savefig('positive_wordcloud.png')  # 이미지 저장
    plt.show()
else:
    print("No positive words found for the word cloud.")

# 8. 부정적 단어 워드클라우드 생성
if negative_words:
    negative_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(negative_words))
    plt.figure(figsize=(10, 5))
    plt.imshow(negative_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Negative Words WordCloud')
    plt.savefig('negative_wordcloud.png')  # 이미지 저장
    plt.show()
else:
    print("No negative words found for the word cloud.")