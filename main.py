import os
from audio_to_text import extract_audio, transcribe_audio

if __name__ == "__main__":
    video_path = "test.mp4"

    if not os.path.exists(video_path):
        print("Video file not found!")
    else:
        audio_path = extract_audio(video_path)
        text = transcribe_audio(audio_path)

        with open("output_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
                      
        print("\nTranscription Result:\n")
        print(text)
