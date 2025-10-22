from audio_to_text import AudioProcessor
from summarize import Summarizer
from qa_generator import QAGenerator
from pdf_generator import GeneratePDF
from json_storage import save_file_record
from email_sender import EmailSender
from user_manager import UserManager
from view_history import ViewHistory
import os


if __name__ == "__main__":
    print("Welcome to Smart Video Assistant")
    print("------------------------------------")
    print("This program helps you process videos using AI.")
    print("------------------------------------")

    user_manager = UserManager()
    processor = AudioProcessor()
    summarizer = Summarizer()
    qa_gen = QAGenerator()
    pdf_gen = GeneratePDF()
    email_sender = EmailSender()
    view_history = ViewHistory()

    # LOGIN / SIGNUP 
    while True:
        print("1 Login")
        print("2 Sign Up")
        print("------------------------------------")
        choice = input("Enter your choice (1/2): ").strip()

        if choice == "1":
            user_email = user_manager.login()
        elif choice == "2":
            user_email = user_manager.signup()
        else:
            print("Invalid choice. Try again.")
            continue

        if not user_email:
            print("\nReturning to main menu...")
            input("Press Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        print(f"\nWelcome, {user_email}!")
        break

    # MAIN MENU 
    while True:
        print("\nWhat would you like to do?")
        print("1. Process a new video")
        print("2. View History")
        print("3. Logout")
        print("------------------------------------")

        main_choice = input("Enter your choice (1/2/3): ").strip()

        # OPTION 1: PROCESS NEW VIDEO 
        if main_choice == "1":
            video_path = input("\nEnter your video file path: ").strip('"')
            video_title = os.path.basename(video_path)
            video_name_no_ext = os.path.splitext(video_title)[0]

            if not os.path.exists(video_path):
                print("Video file not found! Please check your path.")
                continue

            print("Processing your video, this may take a few minutes...")
            audio_path = processor.extract_audio(video_path)
            text = processor.transcribe_audio(audio_path)

            with open(os.path.join("files", "output_text.txt"), "w", encoding="utf-8") as f:
                f.write(text)

            # SUB MENU FOR VIDEO PROCESSING
            while True:
                print("\nWhat would you like to do with this video?")
                print("1. Convert Video to Text")
                print("2. Summarize the Video")
                print("3. Generate Q&A")
                print("4. Back to Main Menu")
                print("------------------------------------")
                choice = input("Enter your choice (1/2/3/4): ").strip()

                if choice == "4":
                    break

                #  1: CONVERT VIDEO TO TEXT 
                if choice == "1":
                    print("\nConvert video to text...")
                    print(f"\nTranscript ready!\n{text}.")
                
                    pdf_name = f"transcript_{video_name_no_ext}.pdf"
                    pdf_path = os.path.join("files", pdf_name)
                    pdf_gen.create_pdf(text, pdf_path, title=f"Transcript for {video_title}")
                    save_file_record(user_email, "transcript", video_title, pdf_name, pdf_path)

                    save_choice = input("\nWould you like to send this file to your email? (yes/no): ").strip().lower()
                    if save_choice == "yes":
                        email_sender.send_email(
                            user_email,
                            subject="Your Video Transcript",
                            body="Here’s your transcript file from Smart Video Assistant.",
                            attachment_path=pdf_path
                        )
                    else:
                        print("File saved locally.")
                    print("\nPress Enter to return to Main Menu...")
                    input()

                # 2: SUMMARIZE 
                elif choice == "2":
                    print("\nGenerating summary of your video...")
                    summary = summarizer.summarize_text(text)
                    print(f"Summary completed\n{summary}.")
                    summary_txt_path = os.path.join("files", f"summary_{video_name_no_ext}.txt")
                    with open(summary_txt_path, "w", encoding="utf-8") as f:
                        f.write(summary)

                    pdf_name = f"summary_{video_name_no_ext}.pdf"
                    pdf_path = os.path.join("files", pdf_name)
                    pdf_gen.create_pdf(summary, pdf_path, title=f"Summary for {video_title}")

                    # Save file record first (always)
                    save_file_record(user_email, "summary", video_title, pdf_name, pdf_path)

                    # Then ask if the user wants to send it
                    save_choice = input("\nWould you like to send this file to your email? (yes/no): ").strip().lower()
                    if save_choice == "yes":
                        email_sender.send_email(
                            user_email,
                            subject="Your Video Summary",
                            body="Here’s your summary file from Smart Video Assistant.",
                            attachment_path=pdf_path
                        )
                    else:
                        print("File saved locally.")

                    print("\nPress Enter to return to Main Menu...")
                    input()

                # 3: GENERATE Q&A 
                elif choice == "3":
                    print("\nGenerating Questions and Answers from your video...")
                    qa_output = qa_gen.generate_qa(text)
                    print("\nGenerated Q&A Pairs:\n")
                    print(qa_output)
                    qa_txt_path = os.path.join("files", f"qa_{video_name_no_ext}.txt")
                    with open(qa_txt_path, "w", encoding="utf-8") as f:
                        f.write(qa_output)
                    pdf_name = f"qa_{video_name_no_ext}.pdf"
                    pdf_path = os.path.join("files", pdf_name)
                    pdf_gen.create_pdf(qa_output, pdf_path, title=f"Q&A for {video_title}")
                    save_file_record(user_email, "qa", video_title, pdf_name, pdf_path)

                    save_choice = input("\nWould you like to send this file to your email? (yes/no): ").strip().lower()
                    if save_choice == "yes":
                        email_sender.send_email(
                            user_email,
                            subject="Your Q&A File",
                            body="Here’s your Questions and Answers file from Smart Video Assistant.",
                            attachment_path=pdf_path
                        )
                    else:
                        print("File saved locally.")
                    print("\nPress Enter to return to Main Menu...")
                    input()

                else:
                    print("Invalid choice, please try again.")

        # 2: VIEW HISTORY
        elif main_choice == "2":
            result = view_history.show_user_videos(user_email)
            if result == "main_menu":
                continue

        # 3: LOGOUT 
        elif main_choice == "3":
            print("Logged out successfully. Goodbye! 👋")
            break

        else:
            print("Invalid choice. Try again.")
