# 1. 필요 패키지 설치 및 데이터 불러오기
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import matplotlib.font_manager as fm  # 폰트 설정을 위해 추가
from transformers import pipeline

# 데이터 로드
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

# 형태소 분석 및 불용어 제거
def extract_keywords(comment):
    nouns = okt.nouns(comment)  # 명사 추출
    filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]  # 불용어 제거 및 1글자 필터링
    return filtered_nouns

df['nouns'] = df['cleaned_comments'].apply(lambda x: extract_keywords(x))

# 3. 단어 조합 처리 (일반화된 단어 조합 처리)
word_pairs = [
    ("가성", "비"),  # 가성비
    ("프로", "스펙스"),  # 프로스펙스
    ("운동", "화"),  # 운동화
]

def combine_word_pairs(tokens, word_pairs):
    combined_tokens = []
    i = 0
    while i < len(tokens):
        for pair in word_pairs:
            if i + len(pair) - 1 < len(tokens) and tuple(tokens[i:i + len(pair)]) == pair:
                combined_tokens.append("".join(pair))  # 단어 조합 결합
                i += len(pair)  # 조합된 단어 수만큼 건너뜀
                break
        else:
            combined_tokens.append(tokens[i])
            i += 1
    return combined_tokens

df['nouns'] = df['nouns'].apply(lambda x: combine_word_pairs(x, word_pairs))

# 4. 감정 분석 모델 설정
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="beomi/KcELECTRA-base",
    device=0,  # GPU 사용 시 설정
    padding=True,  # 자동 패딩
    truncation=True,  # 초과하는 텍스트 자르기
    max_length=512  # 최대 시퀀스 길이 설정
)

# 5. 긍/부정 단어 추출 및 분석
positive_words = set()
negative_words = set()

for index, row in df.iterrows():
    comment = row['comment']
    result = sentiment_analyzer(comment)
    sentiment = result[0]['label']  # 결과의 'label' 필드

    if sentiment == 'POSITIVE':
        positive_words.update(row['nouns'])
    elif sentiment == 'NEGATIVE':
        negative_words.update(row['nouns'])

# 6. 결과 출력 및 시각화
print("긍정적인 단어들:", positive_words)
print("부정적인 단어들:", negative_words)

# 7. 워드클라우드 생성
font_path = "/Users/lovelyjoo/Library/Fonts/AppleSDGothicNeoB.ttf"  # macOS 예시. 사용 환경에 맞는 폰트 경로 지정

# 긍정 단어 워드클라우드
positive_wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600)
positive_wordcloud.generate(" ".join(positive_words))
positive_wordcloud.to_file("positive_wordcloud_output.png")

# 부정 단어 워드클라우드
negative_wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600)
negative_wordcloud.generate(" ".join(negative_words))
negative_wordcloud.to_file("negative_wordcloud_output.png")

# 워드클라우드 시각화
plt.figure(figsize=(10, 8))
plt.imshow(positive_wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("긍정적인 단어 워드클라우드")
plt.show()

plt.figure(figsize=(10, 8))
plt.imshow(negative_wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("부정적인 단어 워드클라우드")
plt.show()