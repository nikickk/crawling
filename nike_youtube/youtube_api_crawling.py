import pandas
from googleapiclient.discovery import build
# 각기 다른 추출위해 video ID 변경
# csv 파일명은 영상id 또는 영상title
#Id = 'MOVIE_ID'

comments = list()
api_obj = build('youtube', 'v3', developerKey='AIzaSyC48b0ITiNHkrJeXxhOeGl4Fza_K8agvRk')
# 댓글수집
response = api_obj.commentThreads().list(part='snippet,replies', videoId='McS7W7UN_Nc', maxResults=100).execute()


while response:
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([comment['textDisplay'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])

        if item['snippet']['totalReplyCount'] > 0:
            for reply_item in item['replies']['comments']:
                reply = reply_item['snippet']
                comments.append([reply['textDisplay'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])

    if 'nextPageToken' in response:
        response = api_obj.commentThreads().list(part='snippet,replies', videoId='sWC-pp6CXpA', pageToken=response['nextPageToken'], maxResults=100).execute()
    else:
        break


    # 댓글저장
df = pandas.DataFrame(comments)
df.to_csv('./nike_youtube_crawling.csv', header=['comment', 'author', 'date', 'num_likes'],encoding="utf-8-sig")


# df = pandas.DataFrame(comments)
# df.to_excel('results.xlsx', header=['comment', 'author', 'date', 'num_likes'], index=None)