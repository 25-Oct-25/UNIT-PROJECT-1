#External libraries
from huggingface_hub import InferenceClient
from colorama import Fore, Style
#Built-in module
import os
import time
import re
from datetime import datetime


class AIHelper:
        
    def __init__(self, model_name):
        """Initialize connection to Hugging Face API with optional model selection."""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please check your .env file.")

        # Initialize the Hugging Face client
        self.client = InferenceClient(api_key=api_key)
        # Store selected model name
        self.model_name = model_name



    def generate_part(self, prompt, genre, length="short"):
        """
        Generate a story part with smooth continuation and concise storytelling.
        Ends with three numbered choices unless the story is concluded.
        """
        system_message = (
            f"You are a skilled {genre} story writer. "
            f"Continue the story naturally and logically from where it left off. "
            f"Write in a cinematic, emotional, and immersive style — around 4 to 6 short paragraphs per part. "
            f"Focus only on what happens next, keeping consistency with tone and characters. "

            f"If the main story arc feels resolved, or the hero completes their goal, "
            f"then conclude gracefully with a satisfying final paragraph followed by 'THE END'. "

            f"Only include numbered choices (1., 2., 3.) if the story naturally continues afterward. "
            f"If the story is truly finished, DO NOT include any numbered choices — just end with 'THE END'. "

            f"Never generate both 'THE END' and numbered options together."
        )

        try:
            if getattr(self, "creativity", "balanced") == "balanced":
                temperature = 0.7
            elif self.creativity == "imaginative":
                temperature = 1.0
            elif self.creativity == "serious":
                temperature = 0.4
            else:
                temperature = 0.7
            for attempt in range(3):
                try:

                    # Generate story continuation
                    response = self.client.chat_completion(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=750 if length == "short" else 1100,
                        temperature=temperature,
                        top_p=0.9,
                        timeout=30 )
                    break
                except Exception as e:
                    if attempt == 2: 
                        raise e
                    print(Fore.YELLOW +f"⚠️ Attempt {attempt+1} failed, retrying..."+ Style.RESET_ALL)
                    time.sleep(2)

            # Extract response text
            story_text = response.choices[0].message["content"].strip()
            
            story_text = re.sub(r'\n{3,}', '\n\n', story_text)
            story_text = re.sub(r'(\b\w+\b)( \1\b)+', r'\1', story_text)
            story_text = story_text.strip()

            # Detect numbered options (1–3)
            lines = story_text.split("\n")
            options = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]

            # Add fallback if missing
            if not options:
                options = [
                    "1. The hero takes a bold action to change the situation.",
                    "2. A mysterious twist forces a new decision.",
                    "3. The hero pauses to reflect before moving forward."
                ]
                story_text += "\n\n" + "\n".join(options)

            # Clean up unwanted blank lines only — keep 'THE END' if it's actually there
            story_text = "\n".join([line for line in story_text.split("\n") if line.strip()])

            # Detect if it's a true ending
            is_true_end = "THE END" in story_text.upper()
            if any(phrase in story_text.lower() for phrase in [
                "the journey was complete",
                "finally free",
                "at last, peace",
                "their story had ended",
                "and that was the end" ]):
                is_true_end = True
            
            os.makedirs("logs", exist_ok=True)
            with open("logs/ai_history.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now()}] Model: {self.model_name} | Creativity: {getattr(self, 'creativity', 'balanced')}\n")
                f.write(f"Prompt: {prompt[:200]}...\n")
                f.write(f"Response: {story_text[:500]}...\n")
                f.write("-" * 60 + "\n")

            # Return final result (no dead code after)
            return {"text": story_text, "options": options, "is_true_end": is_true_end}

        except Exception as e:
            # Safe fallback
            fallback_text = (
                f"⚠️ HF API Error: {str(e)}\n"
                "The connection to the AI service was interrupted.\n"
                "Don't worry — your progress is saved and you can continue!"
            )
            fallback_options = [
                "1. Retry the last part.",
                "2. Change the story's direction.",
                "3. End the story for now."
            ]
            print("\n" + fallback_text)
            return {"text": fallback_text, "options": fallback_options}
