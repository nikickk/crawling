import pandas as pd
import re
from konlpy.tag import Okt

# 파일 경로 설정
path = r'C:\Tave2\Nike_data_review.csv'
stopwords_path = r'C:\Tave2\crawling\nike_hashtag\stopword.txt'  # 스탑워드 파일 경로

# 스탑워드 파일 읽기
with open(stopwords_path, 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()  # 각 줄을 하나의 스탑워드로 처리

# CSV 파일 읽기
df = pd.read_csv(path)

# 첫 번째 컬럼 추출
first_column = df.iloc[:, 0]

# Okt 초기화
okt = Okt()

# 전처리 함수
def preprocess_text(text):
    if pd.isna(text):
        return ""

    # 1. 해시태그 제거 (#으로 시작하는 단어 전체 제거)
    text = re.sub(r'#\S+', '', text)

    # 2. 숫자+주 패턴 제거 (숫자+주 통째로 제거)
    text = re.sub(r'\d+주', '', text)

    # 3. 특수기호 제거 (한국어, 영어, 숫자, 공백만 유지)
    text = re.sub(r'[^ㄱ-ㅎ가-힣a-zA-Z0-9\s]', '', text)

    # 4. 형태소 분석 및 품사 태깅
    tokens_with_pos = okt.pos(text)

    # 5. 조사, 접속사 등 불필요한 품사 제거
    tokens_filtered = [word for word, pos in tokens_with_pos if pos not in ['Josa', 'Conjunction']]

    # 6. 한 글자 단어 및 자음/모음만 있는 단어 제거
    tokens_filtered = [token for token in tokens_filtered if len(token) > 1 and not re.fullmatch(r'[ㄱ-ㅎㅏ-ㅣ]', token)]

    # 7. 스탑워드 제거
    tokens_filtered = [token for token in tokens_filtered if token not in stopwords]

    # 8. 결과를 다시 하나의 문자열로 변환
    text = ' '.join(tokens_filtered)

    # 9. 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# 데이터 전처리
processed_column = first_column.apply(preprocess_text)

# 새로운 데이터프레임에 결과 저장
df['Processed_First_Column'] = processed_column

# 결과 확인
print(df.head())

# 새로운 CSV 파일로 저장
output_path = r'C:\Tave2\Processed_Nike_data_review.csv'
df.to_csv(output_path, index=False)
