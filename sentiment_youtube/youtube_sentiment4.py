# 필요 패키지 설치 및 데이터 불러오기
import pandas as pd
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from transformers import pipeline

# 1. 데이터 로드
file_path = "nike_youtube_crawling(fix).csv"  # 파일 경로
df = pd.read_csv(file_path)

# 2. 텍스트 전처리
okt = Okt()

# (1) 한글과 공백만 남기기
df['cleaned_comments'] = df['comment'].str.replace(r"[^\uAC00-\uD7A3\s]", "", regex=True)

# (2) 불용어 정의
stopwords = set([
    "그리고", "하지만", "그래서", "또한", "즉", "왜냐하면", "때문에", "때문", "무슨", "그게",
    "이것", "저것", "그것", "너무", "정말", "매우", "아주", "어느", "이", "저", "그",
    "점점", "계속", "다른", "일단", "바로", "가장", "이후", "어디", "부터", "년도", "이상", "등등",
    "정도", "절대", "조금", "거의", "사서", "사고"
])

# (3) 명사 추출 및 불용어 제거
def extract_keywords(comment):
    nouns = okt.nouns(comment)  # 명사 추출
    filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]  # 불용어 및 1글자 필터링
    return filtered_nouns

df['nouns'] = df['cleaned_comments'].apply(lambda x: extract_keywords(x))

# (4) 단어 조합 처리
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

# 3. 단어 빈도 계산
all_nouns = sum(df['nouns'], [])  # 모든 댓글의 명사를 합침
word_counts = Counter(all_nouns)  # 단어 빈도 계산

# 4. 워드클라우드 생성
font_path = "/Users/lovelyjoo/Library/Fonts/AppleSDGothicNeoB.ttf"

wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600)
wordcloud.generate_from_frequencies(word_counts)
wordcloud.to_file("youtube_wordcloud_output.png")

plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# 5. 빈도 분석 시각화
top_words = word_counts.most_common(50)  # 상위 50개 단어

# 상위 단어 빈도 막대그래프
top_words_df = pd.DataFrame(top_words, columns=["word", "count"])
top_words_df.plot(kind='bar', x='word', y='count', legend=False, figsize=(12, 6), color="skyblue")
plt.title("Top Words Frequency")
plt.ylabel("Frequency")
plt.savefig("youtube_Frequency_output.png", bbox_inches='tight')
plt.show()

# 6. 감정 분석 파이프라인 설정
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="beomi/KcELECTRA-base",
    device=-1  # CPU 모드로 실행
)

# Label mapping based on the model's output
label_mapping = {
    'label_0': 'NEGATIVE',  # Assuming label_0 corresponds to negative sentiment
    'label_1': 'POSITIVE'   # Assuming label_1 corresponds to positive sentiment
}

# 7. 긍정적/부정적 단어 추출
positive_words = []
negative_words = []

for comment, nouns in zip(df['cleaned_comments'], df['nouns']):
    if not comment.strip():  # 비어 있는 댓글은 무시
        continue
    try:
        # Sentiment analysis call
        result = sentiment_analyzer(comment, truncation=True, max_length=512)
        label = result[0]['label']  # Get the label from the result
        
        # Map the label to a more readable format
        sentiment = label_mapping.get(label, None)
        if sentiment:
            print(f"Comment: {comment} -> Sentiment: {sentiment}")
            
            if sentiment == 'POSITIVE':
                positive_words.extend(nouns)
            elif sentiment == 'NEGATIVE':
                negative_words.extend(nouns)
        else:
            print(f"Unexpected label '{label}' for comment '{comment}'")
    
    except Exception as e:
        print(f"Error processing comment '{comment}': {e}")

# 중복 제거 및 정리
positive_words = list(set(positive_words))
negative_words = list(set(negative_words))

# 8. 긍정적 단어 워드클라우드 생성
if positive_words:
    positive_wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600).generate(" ".join(positive_words))
    plt.figure(figsize=(10, 8))
    plt.imshow(positive_wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Positive Words WordCloud")
    plt.savefig("positive_wordcloud_output.png")
    plt.show()
else:
    print("No positive words found for the word cloud.")

# 9. 부정적 단어 워드클라우드 생성
if negative_words:
    negative_wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600).generate(" ".join(negative_words))
    plt.figure(figsize=(10, 8))
    plt.imshow(negative_wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Negative Words WordCloud")
    plt.savefig("negative_wordcloud_output.png")
    plt.show()
else:
    print("No negative words found for the word cloud.")
