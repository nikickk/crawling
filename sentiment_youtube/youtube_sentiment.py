# 필요한 패키지 설치
import pandas as pd
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
from transformers import pipeline

# 데이터 로드
file_path = "nike_youtube_crawling(fix).csv"  # 파일 경로
df = pd.read_csv(file_path)

# 1. 데이터 전처리
okt = Okt()
df['cleaned_comments'] = df['comment'].str.replace(r"[^\uAC00-\uD7A3\s]", "", regex=True)  # 한글과 공백만 남기기

# 불용어 리스트 정의
stopwords = set([
    "그리고", "하지만", "그래서", "또한", "즉", "왜냐하면", "때문에", "때문", "무슨", "그게",
    "이것", "저것", "그것", "너무", "정말", "매우", "아주", "어느", "이", "저", "그",
    "점점", "계속", "다른", "일단", "바로", "가장", "이후", "어디", "부터", "년도", "이상", "등등",
    "정도", "절대", "조금", "거의", "사서", "사고"
])

# 형태소 분석 및 불용어 제거
def extract_keywords(comment):
    nouns = okt.nouns(comment)
    filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]
    return filtered_nouns

df['nouns'] = df['cleaned_comments'].apply(lambda x: extract_keywords(x))

# 2. 단어 조합 처리
word_pairs = [
    ("가성", "비"),
    ("프로", "스펙스"),
    ("운동", "화")
]

def combine_word_pairs(tokens, word_pairs):
    combined_tokens = []
    i = 0
    while i < len(tokens):
        for pair in word_pairs:
            if i + len(pair) - 1 < len(tokens) and tuple(tokens[i:i + len(pair)]) == pair:
                combined_tokens.append("".join(pair))
                i += len(pair)
                break
        else:
            combined_tokens.append(tokens[i])
            i += 1
    return combined_tokens

df['nouns'] = df['nouns'].apply(lambda x: combine_word_pairs(x, word_pairs))

# 5. 감정분석 준비 및 실행
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def analyze_sentiment(comment):
    try:
        result = sentiment_analyzer(comment)
        return result[0]['label']
    except Exception as e:
        return "Error"

df['sentiment'] = df['cleaned_comments'].apply(lambda x: analyze_sentiment(x) if isinstance(x, str) else "Neutral")

# 6. 감정분석 결과 요약
sentiment_counts = df['sentiment'].value_counts()
print("Sentiment Analysis Results:")
print(sentiment_counts)

# 감정분석 결과 시각화
sentiment_counts.plot(kind='bar', figsize=(10, 6), color="lightcoral")
plt.title("Sentiment Analysis Results")
plt.xlabel("Sentiment")
plt.ylabel("Count")
plt.savefig("youtube_sentiment_analysis_output.png", bbox_inches='tight')
plt.show()

# 감정분석 결과 저장
df.to_csv("nike_youtube_sentiment_analysis_results.csv", index=False)