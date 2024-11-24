import googleapiclient.discovery
import csv

# API 키와 검색 엔진 ID
api_key = 'AIzaSyCaxtuMxsT4AMI3FgnSWrCQNC4wgz0HO3Y'  # 생성한 API 키 입력
search_engine_id = '46ba27537ee604e39'  # 생성한 검색 엔진 ID 입력

# 구글 API 클라이언트 설정
service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)

# 검색 쿼리
query = '나이키 아디다스'

# 검색 결과를 저장할 CSV 파일 열기
with open('search_results.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Link', 'Snippet'])  # CSV 헤더

    # 여러 페이지의 결과를 가져오기
    for start in range(1, 101, 10):  # 1부터 30까지, 10씩 증가 (총 3 페이지)
        response = service.cse().list(q=query, cx=search_engine_id, start=start).execute()
        
        if 'items' in response:
            for item in response['items']:
                writer.writerow([item['title'], item['link'], item['snippet']])
        else:
            print("검색 결과가 없습니다.")
        
print("검색 결과가 'search_results.csv' 파일에 저장되었습니다.")