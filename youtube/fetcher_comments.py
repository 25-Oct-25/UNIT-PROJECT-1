"""
Provides functions to interact with the YouTube Data API.
This docs helps me to understand and write the code:
https://developers.google.com/youtube/v3/docs
"""
from googleapiclient.discovery import build

def fetch_comments(video_id, api_key, max_pages=10):
    '''Retrieve all comments and replies for a given video'''
    youtube = build("youtube", "v3", developerKey=api_key)
    comments, next_page_token = [], None

    for _ in range(max_pages):
        #to access the comments
        response = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText",
            pageToken=next_page_token
        ).execute()
        
        #represents one comment thread
        for item in response["items"]: 
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            if "replies" in item:
                #to access the replies of comment
                for reply in item["replies"]["comments"]:
                    comments.append(reply["snippet"]["textDisplay"])
        #Go to next page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments

# used to validate the id of video, or displays the title
def get_video_title(video_id, api_key):
    '''Retrieve the video title from its ID'''
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    items = response.get("items", [])
    return items[0]["snippet"]["title"] if items else "Unknown Title"
