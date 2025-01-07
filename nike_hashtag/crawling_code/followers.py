import json
import pandas as pd

# JSON 파일 경로
json_file_path = r'C:\Tave2\crawling\nike_hashtag\crawling_code\following.json'

# JSON 파일 읽기
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 데이터를 담을 리스트
records = []

# JSON 데이터에서 필요한 정보 추출
for entry in data.get('relationships_following', []):
    for string_list_data in entry.get('string_list_data', []):
        records.append({
            'value': string_list_data.get('value', ''),
            'href': string_list_data.get('href', '')
        })

# pandas DataFrame 생성
df = pd.DataFrame(records)
df["category"]="러닝"
# CSV 파일로 저장
csv_file_path = r'C:\Tave2\crawling\nike_hashtag\crawling_code\influencer_following.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"CSV 파일이 생성되었습니다: {csv_file_path}")
