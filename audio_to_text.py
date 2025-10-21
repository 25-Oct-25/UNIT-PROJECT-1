import ffmpeg
import whisper
import os
import warnings


warnings.filterwarnings("ignore")
class AudioProcessor:
    def __init__(self):
        pass

    # Step 1: Extract audio
    def extract_audio(self, video_path, output_audio="audio.wav"):
        (
            ffmpeg
            .input(video_path)
            .output(output_audio, ac=1, ar="16k")  # Mono, 16kHz
            .global_args("-hide_banner", "-loglevel", "error")
            .run(overwrite_output=True)
        )
        return output_audio

    # Step 2: Transcribe with Whisper
    def transcribe_audio(self, audio_path):
        model = whisper.load_model("small")
        result = model.transcribe(audio_path)
        return result["text"]
