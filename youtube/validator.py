"""
Handles validation of YouTube video IDs using basic checks
and API confirmation via the YouTube Data API.
"""

from youtube.fetcher_comments import get_video_title
from colorama import Fore
import re
from googleapiclient.discovery import build


def get_valid_video_id(api_key):
    """
    Prompt the user for a YouTube Video ID and validate it.
    """
    while True:
        try:
            # Ask user for the video ID
            print(Fore.LIGHTCYAN_EX + "🎥 Please provide the YouTube Video ID to start analyzing.")
            print(Fore.WHITE + "Example: dQw4w9WgXcQ (from https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
            video_id = input(Fore.GREEN + "\n🔗 Enter the YouTube Video ID here: ").strip()

            if not video_id:
                raise ValueError("Video ID cannot be empty.")
            if len(video_id) < 8 or len(video_id) > 15:
                raise ValueError("Invalid YouTube Video ID length (must be between 8–15 characters).")

            # Check existence using YouTube Data API
            print(Fore.CYAN + " Validating video ID...")
            title = get_video_title(video_id, api_key)
            if title == "Unknown Title":
                raise ValueError("Video not found. Please check the ID and try again.")

            print(Fore.GREEN + f"✅ Valid video ID confirmed! Video Title: {title}\n")
            return video_id, title

        except ValueError as e:
            print(Fore.RED + f"⚠️ {e}")
            print(Fore.YELLOW + "Please try again.\n")

        # Unexpected error
        except Exception as e:
            print(Fore.RED + f"❌ Unexpected error while checking video ID: {e}")
            print(Fore.YELLOW + "Please verify your internet connection or API key, and try again.\n")



def get_valid_channel_id(input_text, api_key):
    """Resolve YouTube channel input (URL, handle, or name) into a valid UC... channel ID."""
    youtube = build("youtube", "v3", developerKey=api_key)

    #ID from URL 
    match = re.search(r"(UC[\w-]{22})", input_text)
    if match:
        return match.group(1)

    #Handle full URLs like https://www.youtube.com/@channelname
    handle_match = re.search(r"@([\w-]+)", input_text)
    if handle_match:
        handle = handle_match.group(1)
    else:
        handle = input_text.strip("@ ").strip()

    #Search in the channel by handle or name
    try:
        response = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        ).execute()
    except Exception as e:
        print(f"❌ API Error while resolving channel: {e}")
        return None

    if "items" in response and len(response["items"]) > 0:
        #Extract channel ID
        channel_id = response["items"][0]["snippet"]["channelId"]
        print(f"✅ Found channel ID: {channel_id}")
        return channel_id

    print(f"❌ Could not find a valid channel for: {input_text}")
    return None
   