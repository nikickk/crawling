# 1. 필요 패키지 설치 및 데이터 불러오기
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import matplotlib.font_manager as fm

# 데이터 로드
file_path = "nike_youtube_crawling(fix).csv"  # 파일 경로
df = pd.read_csv(file_path)

# 2. 데이터 전처리
okt = Okt()
df['cleaned_comments'] = df['comment'].str.replace(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", regex=True)  # 한글과 공백만 남기기

# 불용어 리스트 정의 (한국어 불용어 예시)
stopwords = set([
    "그리고", "하지만", "그래서", "또한", "즉", "왜냐하면", "때문에", "때문" "무슨","그게",
    "이것", "저것", "그것", "너무", "정말", "매우", "아주", "어느", "이", "저", "그",
    "점점","계속","다른","일단","바로","가장","이후","어디","부터","년도","이상", "등등",
    "정도","절대","조금","거의","사서","사고","진짜","순간","년전","전부","년대","이건",
    "해도","생각","부분"
])

# 형태소 분석 및 불용어 제거
def extract_keywords(comment):
    nouns = okt.nouns(comment)  # 명사 추출
    filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]  # 불용어 제거 및 1글자 필터링
    return filtered_nouns

df['nouns'] = df['cleaned_comments'].apply(lambda x: extract_keywords(x))

# 3. 단어 조합 처리 (일반화된 단어 조합 처리)
# 조합할 단어 쌍을 정의합니다.
word_pairs = [
    ("가성", "비"),  # 가성비
    ("프로","스펙스"),  # 나이키제품
    ("운동", "화"),  # 운동화, 운동화이팅
    # 필요에 따라 더 많은 조합을 추가할 수 있습니다.
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

# 3. 워드클라우드 생성
all_nouns = sum(df['nouns'], [])  # 모든 댓글의 명사를 합침
word_counts = Counter(all_nouns)  # 단어 빈도 계산
top_words = word_counts.most_common(50)  # 상위 50개 단어 확인

# 한글 폰트 설정
font_path = "/Users/lovelyjoo/Library/Fonts/AppleSDGothicNeoB.ttf"

# 워드클라우드 시각화
wordcloud = WordCloud(font_path="AppleGothic.ttf", background_color="white", width=800, height=600)
wordcloud.generate_from_frequencies(word_counts)
wordcloud.to_file("youtube_wordcloud_output.png")


plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# 4. 빈도분석 시각화
top_words_df = pd.DataFrame(top_words, columns=["word", "count"])
top_words_df.plot(kind='bar', x='word', y='count', legend=False, figsize=(12, 6), color="skyblue")
plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())
plt.title("Top Words Frequency")
plt.ylabel("Frequency")
plt.savefig("youtube_Frequency_output.png", bbox_inches='tight')
plt.show()