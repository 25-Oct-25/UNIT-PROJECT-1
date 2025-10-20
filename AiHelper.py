from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

class AIHelper:
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))

    def generate_part(self, prompt, genre, length="short"):
        """
        generate part of story(short أو long)
        """
        if length == "short":
            max_tokens = 200
        elif length == "long":
            max_tokens = 500
        else:
            max_tokens = 300

        system_message = (
            f"You are a talented creative writer who writes {genre} stories. "
            f"Write a {length} story continuation that stays coherent and interesting."
        )

        try:
            response = self.client.chat_completion(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.9,
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"❌ HF API Error: {str(e)}"

    def generate_choices(self, current_part):
        """
        generate 3 choices for path of story
        """
        prompt = (
            f"Based on the story so far, suggest 3 possible next actions for the main character.\n\n"
            f"Story so far:\n{current_part}\n\n"
            "Respond in this format:\n"
            "1. [First choice]\n2. [Second choice]\n3. [Third choice]"
        )

        try:
            response = self.client.chat_completion(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": "You are a creative story generator."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=250,
                temperature=0.8,
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error generating choices: {str(e)}"


