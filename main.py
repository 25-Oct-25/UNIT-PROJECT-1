"""
🎬 YouTube Comment Analyzer & Gemini AI Report Generator
"""
from config.settings import YOUTUBE_API_KEY
from youtube.fetcher import fetch_comments, get_video_title
from youtube.validator import get_valid_video_id
from analysis.sentiment import analyze_sentiment, top_words
from analysis.gemini_summary import gemini_summary
from report.pdf_generator import create_pdf_report
from report.json_generator import save_analysis_json
from utils.text_cleaner import clean_markdown

import os
from art import text2art
from colorama import Fore, Style, init, just_fix_windows_console

just_fix_windows_console()
init(autoreset=True)

# Welcome Screen
# ===============================
def welcome_screen():
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + text2art("YOUTUBE ANALYZER", font="small"))
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.GREEN + "Welcome to the YouTube Comment Analyzer & AI Report Generator!")
    print(Fore.MAGENTA + "Powered by Gemini AI ✨\n")

# Simple Main Menu
# ===============================
def show_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n📜 Main Menu")
    print(Fore.WHITE + "-" * 30)
    print(Fore.YELLOW + "1. Re-enter the YouTube Video ID")
    print(Fore.YELLOW + "2. Show short summary of comments")
    print(Fore.YELLOW + "3. Check overall feeling (sentiment)")
    print(Fore.YELLOW + "4. See most repeated words or ideas")
    print(Fore.YELLOW + "5. Get tips to improve next video")
    print(Fore.YELLOW + "6. Generate PDF Report")
    print(Fore.YELLOW + "7. Exit")
    print(Fore.WHITE + "-" * 30)

# MAIN FUNCTION
# ===============================
def main():
    welcome_screen()
    data_cache = {}

    video_id, video_title = get_valid_video_id(YOUTUBE_API_KEY)
    data_cache["video_title"] = video_title

    while True:
        show_menu()
        choice = input(Fore.CYAN + "👉 Choose an option (1-6): ").strip()

        
        if choice == "1":
            video_id, video_title = get_valid_video_id(YOUTUBE_API_KEY)
            data_cache["video_title"] = video_title
        # 2 Concise Summary of Main Opinions    
        elif choice == "2":
            
            print(Fore.CYAN + "⏳ Fetching comments...")
            comments = fetch_comments(video_id, YOUTUBE_API_KEY)
            print(Fore.GREEN + f"✅ {len(comments)} comments retrieved!")

            print(Fore.CYAN + "🧠 Creating short AI summary...")
            summary = gemini_summary(comments)
            summary_clean = clean_markdown(summary)
            short_summary = "\n".join(summary_clean.split("\n")[:3]) 

            print(Fore.MAGENTA + "\n🧩 Concise Summary:")
            print(Fore.YELLOW + short_summary + "\n")

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

            if not data_cache["comments"]:
                print(Fore.RED + "⚠️ No comments found for this video. Sentiment analysis cannot be performed.")
                input("Press any key to return to menu: ")
                continue

            print(Fore.CYAN + "🧠 Analyzing overall sentiment...")
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
            if not data_cache["comments"]:
                print(Fore.RED + "⚠️ No comments found for this video.")
                input("Press any key to return to menu: ")
                continue

            print(Fore.CYAN + "🔁 Extracting top repeated ideas...")
            words = top_words(data_cache["comments"])
            data_cache["words"] = words
            save_analysis_json(data_cache.get("video_title", "YouTube_Report"), data_cache)

            print(Fore.MAGENTA + "\n💬 Most Repeated Phrases:")
            for word, count in words[:5]:
                print(f"   💡 {word} ({count})")
            print(Fore.GREEN + "✅ Done!\n")
            input("Press any key to return to menu: ")

        # 5 Actionable Feedback for Next Video
        elif choice == "5":
            if "summary" not in data_cache:
                print(Fore.RED + "⚠️ Please run option 1 first!")
                continue

            if not data_cache.get("comments"):
                print(Fore.RED + "⚠️ No comments available to analyze.")
                input("Press any key to return to menu: ")
                continue

            print(Fore.CYAN + "💡 Generating actionable feedback...")
            feedback_prompt = (
                "Based on the viewers’ comments, give 3 short actionable tips "
                "to improve the next YouTube video (≤5 lines)."
            )
            feedback = gemini_summary([data_cache["summary"], feedback_prompt])
            feedback_clean = "\n".join(clean_markdown(feedback).split("\n")[:5])

            print(Fore.MAGENTA + "\n✨ Actionable Feedback:")
            print(Fore.YELLOW + feedback_clean + "\n")
            input("Press any key to return to menu: ")

        # 6 Generate PDF Report
        elif choice == "6":
            print(Fore.CYAN + "🧾 Generating PDF report...")

            if "comments" not in data_cache:
                comments = fetch_comments(video_id, YOUTUBE_API_KEY)
                data_cache["comments"] = comments
            else:
                comments = data_cache["comments"]

            if not comments:
                print(Fore.RED + "⚠️ No comments found for this video. Cannot generate report.")
                input("Press any key to return to menu: ")
                continue     
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

        # 7 Exit
        elif choice == "7":
            print(Fore.YELLOW + "\n👋 Thanks for using YouTube Analyzer!")
            print(Fore.MAGENTA + "✨ Powered by Gemini AI ✨")
            print(Fore.CYAN + "=" * 60)
            break

        # Invalid Choice
        else:
            print(Fore.RED + "❌ Invalid choice. Please enter a number (1–6).")

if __name__ == "__main__":
    main()