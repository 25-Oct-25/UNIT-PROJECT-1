from audio_to_text import extract_audio, transcribe_audio
from translate import translate_to_arabic
import os

if __name__ == "__main__":
    video_path = "test.mp4"

    if not os.path.exists(video_path):
        print("Video file not found!")
    else:
       
        audio_path = extract_audio(video_path)
        text = transcribe_audio(audio_path)

        with open("output_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("\nTranscription completed and saved in output_text.txt")

      
        print("\n🔹 What would you like to do next?")
        print("1 Translate to Arabic")
        print("2 Summarize the text")

        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            translation = translate_to_arabic(text)
            print("\n🇸🇦 Arabic Translation:\n", translation)
            with open("translated_text.txt", "w", encoding="utf-8") as f:
                f.write(translation)
        

        else:
            print("Invalid choice. Please enter 1 or 2.")

