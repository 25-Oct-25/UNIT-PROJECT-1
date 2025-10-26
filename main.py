"""
YouTube Channel & Comment Analyzer & Gemini AI Report Generator
"""
from config.settings import YOUTUBE_API_KEY
from youtube.fetcher_comments import fetch_comments, get_video_title
from youtube.validator import get_valid_video_id, get_valid_channel_id
from youtube.fetcher_channel import fetcher_Channel_data, fetch_top_viewed_video, thumbnail_channel
from analysis.sentiment import analyze_sentiment, top_words
from analysis.gemini_summary import gemini_summary
from report.pdf_generator import create_pdf_report, youtube_channel_report
from report.json_generator import save_analysis_json, save_channel_data
from utils.text_cleaner import clean_markdown

import os
from art import text2art
from colorama import Fore, Style, init, just_fix_windows_console

just_fix_windows_console()
init(autoreset=True)

# Welcome Screen
def welcome_screen():
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + text2art("YOUTUBE ANALYZER", font="small"))
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.GREEN + "Welcome to the YouTube Comment Analyzer & AI Report Generator!")
    print(Fore.MAGENTA + "Powered by Gemini AI ✨\n")

# Main Menu
def show_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n📜 Main Menu")
    print(Fore.WHITE + "-" * 30)
    print(Fore.YELLOW + 
    '''
    1. Enter the YouTube Video ID
    2. Show short summary of comments
    3. Check overall feeling (sentiment)
    4. See most repeated words or ideas
    5. Get tips to improve next video
    6. Get information about a specific channel
    7. Generate PDF Report
    8. Exit''')
    print(Fore.WHITE + "-" * 30)

# Main function
def main():
    welcome_screen()
    data_cache = {}

    while True:
        show_menu()
        choice = input(Fore.CYAN + "👉 Choose an option (1-8): ").strip()

        #1 To Enter the youtube video id  
        if choice == "1": 
            video_id, video_title = get_valid_video_id(YOUTUBE_API_KEY)
            data_cache["video_title"] = video_title

        # 2 Summary of Main Opinions    
        elif choice == "2":
            #Fetch comments
            print(Fore.CYAN + " Fetching comments...")
            comments = fetch_comments(video_id, YOUTUBE_API_KEY)
            print(Fore.GREEN + f"✅ {len(comments)} comments retrieved!")

            #Gemini summary
            print(Fore.CYAN + " Creating short AI summary...")
            summary = gemini_summary(comments)
            summary_clean = clean_markdown(summary)
            short_summary = "\n".join(summary_clean.split("\n")[:3]) 

            print(Fore.MAGENTA + "\n Concise Summary:")
            print(Fore.YELLOW + short_summary + "\n")

            #sava data in json file
            video_title = get_video_title(video_id, YOUTUBE_API_KEY)
            data_cache["video_title"] = video_title
            data_cache["comments"] = comments
            data_cache["summary"] = summary_clean
            save_analysis_json(video_title, data_cache)
            input("Press any key to return to menu: ")

        # 3 Overall Sentiment
        elif choice == "3":
            if "comments" not in data_cache: 
                print(Fore.RED + "⚠️ Please run option 1 first!")
                continue

            if not data_cache["comments"]: #If the video does not contain comments
                print(Fore.RED + "⚠️ No comments found for this video. Sentiment analysis cannot be performed.")
                input("Press any key to return to menu: ")
                continue
            #overall sentiment
            print(Fore.CYAN + " Analyzing overall sentiment...")
            _, distribution = analyze_sentiment(data_cache["comments"])
            data_cache["distribution"] = distribution
            save_analysis_json(data_cache.get("video_title", "YouTube_Report"), data_cache)

            print(Fore.MAGENTA + "\n😊 Overall Sentiment:")
            for sentiment, pct in distribution.items():
                bar = "█" * int(pct // 5)
                print(f"{sentiment.capitalize():<10} | {bar} {pct:.1f}%")
            print(Fore.GREEN + "✅ Sentiment analysis complete!\n")
            input("Press any key to return to menu: ")

        # 4 Most Repeated Phrases or Ideas
        elif choice == "4":
            if "comments" not in data_cache:
                print(Fore.RED + "⚠️ Please run option 1 first!")
                continue
            #If the video does not contain comments.
            if not data_cache["comments"]:
                print(Fore.RED + "⚠️ No comments found for this video.")
                input("Press any key to return to menu: ")
                continue
            #Top repeated words
            print(Fore.CYAN + " Extracting top repeated ideas...")
            words = top_words(data_cache["comments"])
            data_cache["words"] = words
            #save inside json file
            save_analysis_json(data_cache.get("video_title", "YouTube_Report"), data_cache)
            #Top repeated Phrases
            print(Fore.MAGENTA + "\n Most Repeated Phrases:")
            for word, count in words[:5]:
                print(f"   💡 {word} ({count})")
            print(Fore.GREEN + "✅ Done!\n")
            input("Press any key to return to menu: ")

        # 5 Actionable Feedback for Next Video
        elif choice == "5":
            if "summary" not in data_cache:
                print(Fore.RED + "⚠️ Please run option 1 first!")
                continue
            
            #If the video does not contain comments
            if not data_cache.get("comments"):
                print(Fore.RED + "⚠️ No comments available to analyze.")
                input("Press any key to return to menu: ")
                continue
            print(Fore.CYAN + " Generating actionable feedback...")
            #Gemini Feedback
            feedback_prompt = (
                "Based on the viewers’ comments, give 3 short actionable tips "
                "to improve the next YouTube video (≤5 lines)."
            )
            feedback = gemini_summary([data_cache["summary"], feedback_prompt])
            feedback_clean = "\n".join(clean_markdown(feedback).split("\n")[:5])

            print(Fore.MAGENTA + "\n Actionable Feedback:")
            print(Fore.YELLOW + feedback_clean + "\n")
            input("Press any key to return to menu: ")

        # 6 Get information about a specific channel (new version:) )
        elif choice == "6":
            channel_url = input("🔗 Enter YouTube Channel URL or Channel ID: ").strip()
            id = get_valid_channel_id(channel_url, YOUTUBE_API_KEY)
            if id:
                print(f"✅ Extracted identifier: {id}")
            else:
                print("❌ Invalid YouTube channel input.")
                continue
            #thumb for render in pdf 
            thumb=thumbnail_channel(id,YOUTUBE_API_KEY)
            if not thumb:
                print("⚠️ Channel thumbnail missing. A default image will be used.")
            #Channel data and top views for pdf and json file
            channel_data=fetcher_Channel_data(id, YOUTUBE_API_KEY)
            top_video_id, top_views=fetch_top_viewed_video(id,YOUTUBE_API_KEY)
            if not top_video_id:
                print("⚠️ Could not fetch top videos.")
                continue
            channel_info = {**channel_data, "top_videos":top_views}

            print("\n Channel Information:")
            for key, value in channel_data.items():
                print(f"{key}: {value}")

            print("\n🔥 Top Viewed Videos:")
            for i, video in enumerate(channel_info["top_videos"], start=1):
                print(f"{i}. {video['title']} — {video['views']} views - {video['url']}")

            print("Summary Highest viewed video:") 
            
            #Ask user if you want to save data in pdf and json file.
            save_json=input("Do you want to save the channel information in PDF and json file?(y/n): ").strip().lower()

            if save_json =="y":
                json_path=save_channel_data(channel_info)
            else:
                input("Press any key to return to menu: ")
                continue  
            os.makedirs("data", exist_ok=True)
            os.chdir("data")
            if not thumb:
                print("⚠️ Thumbnail not available — using default placeholder.")
            youtube_channel_report(channel_info,thumb)
            os.chdir("..")
            print(Fore.GREEN + f"✅ PDF and JSON reports saved in 'data/' folder.\n📄 {json_path}")
            
        # 7 Generate PDF Report
        elif choice == "7":
            print(Fore.CYAN + "🧾 Generating PDF report...")

            if "comments" not in data_cache:
                video_id, video_title = get_valid_video_id(YOUTUBE_API_KEY)
                data_cache["video_title"] = video_title
                comments = fetch_comments(video_id, YOUTUBE_API_KEY)
                data_cache["comments"] = comments
            else:
                comments = data_cache["comments"]
            #If the video does not contain comments
            if not comments:
                print(Fore.RED + "⚠️ No comments found for this video. Cannot generate report.")
                input("Press any key to return to menu: ")
                continue  
            #In case user enter 7 as first input, cache data
            if "distribution" not in data_cache:
                _, distribution = analyze_sentiment(comments)
                data_cache["distribution"] = distribution
            else:
                distribution = data_cache["distribution"]
   
            if "words" not in data_cache:
                words = top_words(comments)
                data_cache["words"] = words
            else:
                words = data_cache["words"]   

            if "video_title" not in data_cache:
                video_title = get_video_title(video_id, YOUTUBE_API_KEY)
                data_cache["video_title"] = video_title
            else:
                video_title = data_cache["video_title"]
            detailed_summary = gemini_summary(comments, mode="pdf")
            detailed_summary_clean = clean_markdown(detailed_summary)

            json_path = save_analysis_json(video_title, data_cache)

            os.makedirs("data", exist_ok=True)
            os.chdir("data")
            create_pdf_report(video_title, distribution, words, detailed_summary_clean, len(comments))
            os.chdir("..")

            print(Fore.GREEN + f"✅ PDF and JSON reports saved in 'data/' folder.\n📄 {json_path}")
            input("Press any key to return to menu: ")

        # 8 Exit
        elif choice == "8":
            print(Fore.YELLOW + "\n👋 Thanks for using YouTube Analyzer!")
            print(Fore.CYAN + "=" * 60)
            break

        # Invalid Choice
        else:
            print(Fore.RED + "❌ Invalid choice. Please enter a number (1–8).")

if __name__ == "__main__":
    main()