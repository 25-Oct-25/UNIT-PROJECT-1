import os

def burn_subtitles(video_path, subtitles_path, output_path="translated_video.mp4"):
    """
    Embed Arabic subtitles (.srt) inside the video permanently using ffmpeg.
    """
    try:
        command = f'ffmpeg -i "{video_path}" -vf subtitles="{subtitles_path}" "{output_path}" -y'
        os.system(command)
        return output_path
    except Exception as e:
        print(f"Failed to burn subtitles: {e}")
        return None
