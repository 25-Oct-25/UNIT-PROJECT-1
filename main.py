from config.settings import YOUTUBE_API_KEY
from youtube.fetcher import fetch_comments, get_video_title
import pandas as pd


def main():
    video_id = input("🎥 Enter YouTube Video ID: ").strip()
    comments = fetch_comments(video_id, YOUTUBE_API_KEY)
    print(f"✅ Retrieved {len(comments)} comments")


    video_title = get_video_title(video_id, YOUTUBE_API_KEY)

    print(video_title)

if __name__ == "__main__":
    main()
