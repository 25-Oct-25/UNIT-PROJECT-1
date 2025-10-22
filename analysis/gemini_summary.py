import google.generativeai as genai
import re

def gemini_summary(comments):
    text_data = "\n".join(comments[:2000])
    prompt = f"""
    Analyze these YouTube comments and provide:
    1. Summary of opinions.
    2. Overall sentiment.
    3. Common phrases.
    4. Feedback for improvement.

    Comments:
    {text_data}
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def clean_markdown(text):
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"^\s*[\*\-]\s*", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()
