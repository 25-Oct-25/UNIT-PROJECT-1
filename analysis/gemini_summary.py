"""
Handles AI-powered summarization using Google Gemini API.
"""
import google.generativeai as genai


def gemini_summary(comments, mode="terminal"):
    '''Generate a summary of YouTube comments using Gemini AI.'''
    text_data = "\n".join(comments[:2000])
    if mode == "terminal":
        prompt = f"""
        You are summarizing YouTube comments.
        Write ONE short paragraph (no more than 3 lines) in simple English.
        Describe what most viewers think or feel about the video.
        Avoid technical or complex words.
        
        Comments:
        {text_data}
        """
    else: 
        prompt = f"""
        Analyze these YouTube comments and provide (use a clear and simple word Without abbreviating):
        1. A concise summary of main opinions.
        2. The overall sentiment (positive, negative, or mixed).
        3. The most repeated phrases or ideas.
        4. Actionable feedback to improve the next video.

        Comments:
        {text_data}
        """
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("⚠️ gemini-2.5-flash failed, switching to gemini-2.5-pro")
        print("Detailed error:", e)
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()






