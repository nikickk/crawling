import pandas
from googleapiclient.discovery import build

# 댓글 저장 리스트
comments = list()

# YouTube API 객체 생성
api_obj = build('youtube', 'v3', developerKey='AIzaSyC48b0ITiNHkrJeXxhOeGl4Fza_K8agvRk')

# 크롤링 대상 비디오 ID
video_id = 'McS7W7UN_Nc'

# 댓글 수집
response = api_obj.commentThreads().list(
    part='snippet,replies',
    videoId=video_id,  # 대상 비디오 ID
    maxResults=100
).execute()

# 댓글 수집 반복
while response:
    for item in response['items']:
        # 최상위 댓글 처리
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([comment['textDisplay'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])

        # 대댓글 처리
        if item['snippet']['totalReplyCount'] > 0 and 'replies' in item:
            for reply_item in item['replies']['comments']:
                reply = reply_item['snippet']
                comments.append([reply['textDisplay'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])

    # 다음 페이지로 이동
    if 'nextPageToken' in response:
        response = api_obj.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,  # 여전히 같은 videoId를 사용
            pageToken=response['nextPageToken'],
            maxResults=100
        ).execute()
    else:
        break

# 댓글 저장
df = pandas.DataFrame(comments)
df.to_csv('./nike_youtube_crawling.csv', header=['comment', 'author', 'date', 'num_likes'], encoding="utf-8-sig")