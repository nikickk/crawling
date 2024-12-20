# 1. 필요 패키지 설치 및 데이터 불러오기
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import matplotlib.font_manager as fm  # 폰트 설정을 위해 추가

# 데이터 로드
file_path = "/Users/lovelyjoo/Github/Github_joo_loves_/crawling/wordcloud_youtube/nike_youtube_crawling(fix).csv"  # 파일 경로
df = pd.read_csv(file_path)

# 2. 데이터 전처리
okt = Okt()
df['cleaned_comments'] = df['comment'].str.replace(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", regex=True)  # 한글과 공백만 남기기

# 불용어 리스트 정의 (한국어 불용어 예시)
stopwords = set([
    "그리고", "하지만", "그래서", "또한", "즉", "왜냐하면", "때문에", "때문", "무슨", "그게",
    "이것", "저것", "그것", "너무", "정말", "매우", "아주", "어느", "이", "저", "그",'사면',
    "점점", "계속", "다른", "일단", "바로", "가장", "이후", "어디", "부터", "년도", "이상", 
    "등등", "정도", "절대", "조금", "거의", "사서", "사고", '제일', '그냥', '이제', '가지',
    '대비', '뭔가', '거기', '지금', '누가', '순간', '얼마', '언제', '몇번', '보고', '진짜',
    '역시', '해도', '시간', '최근', '요즘', '나이키', '만원', '사람', '신고', '하나', '신어',
    '이유', '자주', '세상', '그거', '점점', '전부', '년전', '세대', '일이', '우리', 
    '된거', '원래', '시작', '년대', '이건', '거지',' 산다', '처음', '굳이', '아이', '부분',
    '항상', '사도', '어보', '보임', '사실', '한번', '다가', '부분', '시절', '그동안', '금방',
    '장난', '자체', '얘기', '요새', '보임', '다시', '오히려', '시대', '소리', '얼마나', '하니',
    '인정', '돼지', '팔고', '댓글', '느낌', '메이드', '생각', '달라', '가면', '상황', '매수',
    '이름', '출시', '개월', '알리', '신경', '경우', '마음', '새끼', '신음', '기준', '그때', 
    '산다', '아예', '수가', '사나', '완전', '사지', '구분', '이번', '결과', '자리', '사장',
    '그때', '추천', '사용', '친구', '처럼', '졸라', '이해', '살때', '제대로', '착용', '차이', 
    '일반', '아픔', '리지', '만하', '직원', '반등', '주의', '고객', '전혀', '던데', '모두', 
    '일반인', '팔면', '소비', '먹기', '업체', '몇개', '개비', '신지', '동안', '바보', '무조건',
    '브렌', '나라', '이면', '인식', '처리', '실제', '영상', '안해', '마찬가지', '인터넷', '건가',
    '면티', '사기', '여기', '오지', '다스', '그대로', '누구', '최고', '우시', '유지', '개인',
    '도대체', '아무', '장가', '품질', '신발', '브랜드'
    
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
    ('년도', '못가서'), # n년도 못가서
    ('스케', '쳐스'), # 스케쳐스
    ('스케', '쳐'), # 스케쳐
    ('장난', '질'), # 장난질
    ('도', '대체'), # 도대체
    ('나이', '키'), # 나이키
    ('알파', '플라이'), # 알파플라이
    ('드', '로우'), # 드로우
    ('크', '록스'), # 크록스
    ('발', '바닥'), # 발바닥
    ('밑', '바닥'), # 밑바닥
    ('덩크', '로우'), # 덩크로우
    ('오니츠카', '타이거'), # 오니츠카타이거
    ('개비', '싸'), # 개비싸
    ('개비', '쌈'), # 개비쌈
    ('스', '우시'), # 스우시
    ('아디', '다스'), # 아디다스
    ('온', '라인') # 온라인
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

# 워드클라우드 생성
wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=600)
wordcloud.generate_from_frequencies(word_counts)
wordcloud.to_file("youtube_wordcloud_output(except_품질_신발_브랜드).png")

# 워드클라우드 시각화
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# 4. 빈도분석 시각화
top_words_df = pd.DataFrame(top_words, columns=["word", "count"])
plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())  # 그래프에 한글 폰트 적용
top_words_df.plot(kind='bar', x='word', y='count', legend=False, figsize=(12, 6), color="skyblue")
plt.title("Top Words Frequency")
plt.ylabel("Frequency")
plt.savefig("youtube_Frequency_output(except_품질_신발_브랜드).png", bbox_inches='tight')
plt.show()