"""
Provides functions to interact with the YouTube Data API.
This docs helps me to understand and write the code:
https://developers.google.com/youtube/v3/docs
"""
from googleapiclient.discovery import build

    
def fetcher_Channel_data(channel_id, api_key):
    '''Retrieve data for a given channel information'''
    youtube=build("youtube","v3",developerKey=api_key)
    # Get API besed on the URL that input from user
    if channel_id.startswith("UC"):
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        ).execute()
    else:
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            forHandle=channel_id
        ).execute()

    item=response["items"][0]

    title, description, published_at,=[item["snippet"][k] for k in ("title","description","publishedAt")]

    view_count, subscriber_count, video_count=[item["statistics"][j] for j in ("viewCount","subscriberCount","videoCount")]
    channel_data={
        "title":title,
        "description":description,
        "published_at":published_at,
        "view_count":view_count,
        "subscriber_count":subscriber_count,
        "video_count":video_count
    }
    return channel_data


def thumbnail_channel(channel_id, api_key):
    """Retrieve a YouTube channel's thumbnail URL safely."""
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.channels().list(
        part="snippet",
        id=channel_id
    ).execute()

    # If no items, channel doesn't exist
    if "items" not in response or len(response["items"]) == 0:
        print(f"⚠️ No channel found for ID: {channel_id}")
        return None

    item = response["items"][0]
    thumbnails = item["snippet"].get("thumbnails", {})

    # If channel has no thumbnails
    if not thumbnails:
        print("⚠️ This channel has no thumbnail image.")
        return None

    # quality thumbnail available
    thumbnail_url = (
        thumbnails.get("high", {}).get("url")
        or thumbnails.get("medium", {}).get("url")
        or thumbnails.get("default", {}).get("url")
    )

    if not thumbnail_url:
        print("⚠️ Thumbnail URL missing in API response.")
        return None

    print(f"✅ Thumbnail URL found: {thumbnail_url}")
    return thumbnail_url


def fetch_top_viewed_video(channel_id, api_key):
    '''Retrieve top 5 most viewed videos'''
    youtube=build("youtube","v3",developerKey=api_key)
    response=youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    if "items" not in response or len(response["items"]) == 0:
        print(f"⚠️ No channel found for the provided ID: {channel_id}")
        return None, []
    
    item=response["items"][0]
    #Get upload videos in channel
    uploads_videos=item["contentDetails"]["relatedPlaylists"]["uploads"]
    videos, next_page_token=[],None
    while True:
        res=youtube.playlistItems().list(
        part="contentDetails",
        playlistId=uploads_videos,
        maxResults=50,
        pageToken=next_page_token
    ).execute()
        if "items" not in res:
            break

        for item in res["items"]:
            videos.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    #the channel dosen't have uploaded videos
    if not videos:
        print("⚠️ No uploaded videos found.")
        return None, []  
      
    #Get the statistics for each video
    video_stats =[]
    for i in range(0,len(videos),50):
        res=youtube.videos().list(
        part="snippet,statistics",
        id=",".join(videos[i:i+50])
        ).execute()

        if "items" not in res:
            continue

        for item in res["items"]:
            stats = item.get("statistics", {})
            video_stats.append({
                "id":item["id"],
                "title":item["snippet"]["title"],
                "views":int(stats.get("viewCount",0)),
                "likes":int(stats.get("likeCount",0)),
                "comments":int(stats.get("viewCount",0))
            })

    if not video_stats:
        print("⚠️ No video stats available.")
        return None, []
            
    #Sorted videos based on views        
    sorted_by_views = sorted(video_stats, key=lambda x: x["views"], reverse=True)
    # finally store 5 top videos
    top_viewed = [
        {
            "title": v["title"],
            "views": v["views"],
            "url": f"https://www.youtube.com/watch?v={v['id']}"
        }
        for v in sorted_by_views[:5]
    ]
    #Get Id to summary comments of hight views video
    top_video_id =sorted_by_views[0]["id"]   
    return top_video_id, top_viewed