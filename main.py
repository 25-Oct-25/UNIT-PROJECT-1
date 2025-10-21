from audio_to_text import AudioProcessor
from summarize import Summarizer
from qa_generator import QAGenerator
from pdf_generator import GeneratePDF
import os


if __name__ == "__main__":
    print("Welcome to Smart Video Assistant")
    print("------------------------------------")
    print("This program helps you process videos using AI.")
    print("------------------------------------")
    video_path = input("\nEnter your video file path: ").strip('"')
    if not os.path.exists(video_path):
        print("Video file not found! Please check your path.")
        exit()
    print("Processing your video, this may take a few minutes...")

    processor = AudioProcessor()
    summarizer = Summarizer()
    qa_gen = QAGenerator()
    pdf_gen = GeneratePDF()
    audio_path = processor.extract_audio(video_path)
    text = processor.transcribe_audio(audio_path)

    # Save transcript
    with open("output_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    while True:
        print("\nWhat would you like to do?")
        print("1 Convert Video to Text")
        print("2 Summarize the Video")
        print("3 Generate Qustions and Answers from the Video")
        print("4 Exit")
        print("------------------------------------")

        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        if choice == "4":
            print("\nThank you for using Smart Video Assistant! 👋")
            break

        # Option 1: Only convert video to text 
        if choice == "1":
            print("\nConvert video to text...")
            print(f"\nTranscript ready!\n{text}.")
            while True:
                save_choice = input("\nWould you like to save this Transcript as a PDF and send to email? (yes/no): ").strip().lower()
                if save_choice == "yes":
                    pdf_gen.create_pdf(text, "output_text.pdf", title="Video Transcript")
                    print("PDF saved successfully.")
                    break
                elif save_choice == "no":
                    print("Skipped saving.")
                    break
                else:
                    print("Invalid choice, please enter yes or no.")

        # Option 2: Summarize
        elif choice == "2":
            print("\nGenerating summary of your video...")
            summary = summarizer.summarize_text(text)
            with open("summary.txt", "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"Summary completed\n{summary}.")
            while True:
                save_choice = input("\nWould you like to save this summary as a PDF and send to email? (yes/no): ").strip().lower()
                if save_choice == "yes":
                    pdf_gen.create_pdf(summary, "summary.pdf", title="Video Summary")
                    print("PDF saved successfully.")
                    break
                elif save_choice == "no":
                    print("Skipped saving.")
                    break
                else:
                    print("Invalid choice, please enter yes or no.")


        # Option 3: Generate Q&A 
        elif choice == "3":
            print("\nGenerating Questions and Answers from your video...")
            qa_output = qa_gen.generate_qa(text)
            with open("qa_output.txt", "w", encoding="utf-8") as f:
                f.write(qa_output)
            print("\nGenerated Q&A Pairs:\n")
            print(qa_output)
            while True:
                save_choice = input("\nWould you like to save this Questions and Answers as a PDF and send to email? (yes/no): ").strip().lower()
                if save_choice == "yes":
                    pdf_gen.create_pdf(qa_output, "qa_output.pdf", title="Questions and Answers")
                    print("PDF saved successfully.")
                    break
                elif save_choice == "no":
                    print("Skipped saving.")
                    break
                else:
                    print("Invalid choice, please enter yes or no.")

                

        else:
            print("Invalid choice, please enter 1, 2, 3, and 4.")
