from googleapiclient.discovery import build

def fetch_comments(video_id, api_key, max_pages=10):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments, next_page_token = [], None

    for _ in range(max_pages):
        response = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText",
            pageToken=next_page_token
        ).execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            if "replies" in item:
                for reply in item["replies"]["comments"]:
                    comments.append(reply["snippet"]["textDisplay"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


def get_video_title(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    items = response.get("items", [])
    return items[0]["snippet"]["title"] if items else "Unknown Title"
