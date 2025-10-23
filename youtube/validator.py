"""
Handles validation of YouTube video IDs using basic checks
and API confirmation via the YouTube Data API.
"""

from youtube.fetcher import get_video_title
from colorama import Fore


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

            # Basic validation
            if not video_id:
                raise ValueError("Video ID cannot be empty.")
            if len(video_id) < 8 or len(video_id) > 15:
                raise ValueError("Invalid YouTube Video ID length (must be between 8–15 characters).")

            # Check existence using YouTube Data API
            print(Fore.CYAN + "🔍 Validating video ID...")
            title = get_video_title(video_id, api_key)
            if title == "Unknown Title":
                raise ValueError("Video not found. Please check the ID and try again.")

            print(Fore.GREEN + f"✅ Valid video ID confirmed! Video Title: {title}\n")
            return video_id, title

        except ValueError as e:
            print(Fore.RED + f"⚠️ {e}")
            print(Fore.YELLOW + "Please try again.\n")

        except Exception as e:
            print(Fore.RED + f"❌ Unexpected error while checking video ID: {e}")
            print(Fore.YELLOW + "Please verify your internet connection or API key, and try again.\n")
