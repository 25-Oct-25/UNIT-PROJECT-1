import google.generativeai as genai
import os
from dotenv import load_dotenv
import warnings
import logging

class QAGenerator:
    def __init__(self):
         # 🔹 Hide unwanted logs and warnings
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        warnings.filterwarnings("ignore")
        logging.getLogger("absl").setLevel(logging.ERROR)
        logging.getLogger("grpc").setLevel(logging.ERROR)
        
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def generate_qa(self, text):
        """Generate 5 question-answer pairs using Gemini API."""
        print(f"📝 Text received for Q&A generation (length: {len(text)})")

        if not text or len(text.strip()) < 100:
            return "The text is too short to generate meaningful Q&A. Please ensure the transcription is correct."

        prompt = f"""
        You are an intelligent Q&A generator.
        Read the following transcript carefully and generate 5 meaningful question-answer pairs in this format:

        Q1: [question]
        A1: [answer]
        Q2: [question]
        A2: [answer]
        ...

        Make sure the questions focus on the key ideas and answers are short, direct, and accurate.

        Transcript:
        {text}
        """

        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            qa_text = getattr(response, "text", "").strip()

            if not qa_text:
                return "Model did not return any text. Try with a longer or clearer transcript."

            with open("qa_output.txt", "w", encoding="utf-8") as f:
                f.write("Generated Q&A Pairs:\n\n")
                f.write(qa_text)

            print("Q&A pairs generated successfully and saved as 'qa_output.txt'")
            return qa_text

        except Exception as e:
            return f"Q&A generation failed: {e}"
