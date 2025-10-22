from huggingface_hub import InferenceClient
import os


class AIHelper:
    def __init__(self):
        """Initialize connection to Hugging Face API."""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please check your .env file.")
        self.client = InferenceClient(api_key=api_key)

    def generate_part(self, prompt, genre, length="short"):
        """
        Generate a story part with smooth continuation and concise storytelling.
        Always ends with exactly three numbered choices.
        """
        system_message = (
            f"You are a concise, talented {genre} story writer. "
            f"Continue the story naturally and logically from the previous events. "
            f"Write in a cinematic and emotional style but keep it concise — "
            f"no more than 4 to 6 short paragraphs. "
            f"Avoid repeating any previous information or summarizing earlier parts. "
            f"Focus only on what happens next. "
            f"After writing, provide exactly THREE numbered choices (1., 2., 3.) "
            f"that are short (one line each), clear, and mutually distinct. "
            f"Never include 'THE END' unless the story truly concludes."
        )

        try:
            # 🔮 Generate story continuation
            response = self.client.chat_completion(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=750 if length == "short" else 1100,
                temperature=0.7,  # أقل شوي لتقليل الحشو
                top_p=0.9,
            )

            # 📝 Extract response text
            story_text = response.choices[0].message["content"].strip()

            # ✅ Detect numbered options (1–3)
            lines = story_text.split("\n")
            options = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]

            # ⚙️ Add fallback if missing
            if not options:
                options = [
                    "1. The hero takes a bold action to change the situation.",
                    "2. A mysterious twist forces a new decision.",
                    "3. The hero pauses to reflect before moving forward."
                ]
                story_text += "\n\n" + "\n".join(options)

            # 🧹 Clean up unwanted endings or empty lines
            story_text = story_text.replace("THE END", "").strip()
            story_text = "\n".join([line for line in story_text.split("\n") if line.strip()])

            
            return {"text": story_text, "options": options}

        except Exception as e:
            # 💥 Safe fallback
            fallback_text = (
                f"⚠️ HF API Error: {str(e)}\n"
                "The connection to the AI service was interrupted.\n"
                "Don't worry — your progress is saved and you can continue!"
            )
            fallback_options = [
                "1. Retry the last part.",
                "2. Change the story’s direction.",
                "3. End the story for now."
            ]
            print("\n" + fallback_text)
            return {"text": fallback_text, "options": fallback_options}
