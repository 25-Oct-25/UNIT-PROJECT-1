# External libraries
from huggingface_hub import InferenceClient
from colorama import Fore, Style
# Built-in modules
import os
import time
import re
from datetime import datetime


class AIHelper:
    """
    Handles communication with Hugging Face models and manages
    story generation, error recovery, retries, and clean text handling.
    """
    def __init__(self):
        """Initialize the AI helper and connect to Hugging Face safely."""
        try:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("Hugging Face API key not found. Check your .env file.")

            # ✅ fixed model name (stable and supported)
            self.model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            self.client = InferenceClient(api_key=api_key)

        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize AIHelper: {e}")
    


    def generate_part(self, prompt: str, genre: str, length: str = "short"):
        """
        Generate the next story part, automatically retrying on connection issues.
        Returns a dictionary:
        {
            'text': generated story text,
            'options': list of user choices,
            'is_true_end': bool (True if story has logically ended)
        }
        """
        # System instructions for consistent storytelling
        system_message = (
            f"You are a skilled {genre} story writer. "
            f"Continue the story naturally from where it left off. "
            f"Write in a cinematic, immersive, emotional tone — around 4 to 6 short paragraphs. "
            f"Focus on the next logical event and keep consistent with characters and tone. "
            f"If the story arc is resolved, gracefully end with 'THE END'. "
            f"If it continues, end with 3 numbered choices (1., 2., 3.) for what happens next. "
            f"Never include both 'THE END' and choices together."
        )

        try:
            # CREATIVE BEHAVIOR CONTROL 
            creativity = getattr(self, "creativity", "balanced").lower()
            temperature_map = {"balanced": 0.7, "imaginative": 1.0, "serious": 0.4}
            temperature = temperature_map.get(creativity, 0.7)

            #  MODEL CALL WITH RETRIES 
            response = None
            for attempt in range(3):
                try:
                    print(Fore.CYAN + f"🪄 Generating attempt {attempt + 1}..." + Style.RESET_ALL)

                    # ✅ Always use chat_completion (Mixtral supports it)
                    response = self.client.chat_completion(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=750 if length == "short" else 1100,
                        temperature=temperature,
                        top_p=0.9,
                    )

                    if response and hasattr(response, "choices"):
                        break
                    time.sleep(2)

                except Exception as inner_error:
                    print(Fore.YELLOW + f"⚠️ Attempt {attempt+1} failed: {inner_error}" + Style.RESET_ALL)
                    if attempt == 2:
                        raise inner_error
                    time.sleep(2)

            if not response or not hasattr(response, "choices"):
                raise RuntimeError("No valid AI response after 3 attempts.")

            # TEXT CLEANING 
            story_text = response.choices[0].message["content"].strip()
            story_text = re.sub(r'\n{3,}', '\n\n', story_text)
            story_text = re.sub(r'(\b\w+\b)( \1\b)+', r'\1', story_text)
            story_text = "\n".join([line for line in story_text.split("\n") if line.strip()])

            # OPTION DETECTION 
            lines = story_text.split("\n")
            options = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]

            # END DETECTION 
            is_true_end = "THE END" in story_text.upper() or any(
                phrase in story_text.lower()
                for phrase in [
                    "the journey was complete",
                    "finally free",
                    "at last, peace",
                    "their story had ended",
                    "and that was the end",
                ]
            )

            # FALLBACK OPTIONS (for AI outputs missing choices) 
            if not options and not is_true_end:
                options = [
                    "1. The hero takes a bold action to change the situation.",
                    "2. A mysterious twist forces a new decision.",
                    "3. The hero pauses to reflect before moving forward.",
                ]
                story_text += "\n\n" + "\n".join(options)

            # LOGGING 
            try:
                os.makedirs("logs", exist_ok=True)
                with open("logs/ai_history.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now()}] Model: {self.model_name} | Creativity: {creativity}\n")
                    f.write(f"Prompt: {prompt[:250]}...\nResponse: {story_text[:600]}...\n" + "-" * 60 + "\n")
            except Exception as log_error:
                print(Fore.YELLOW + f"⚠️ Failed to write log: {log_error}" + Fore.RESET)

            # FINAL VALIDATION 
            if not story_text.strip():
                raise RuntimeError("Generated story text was empty.")

            return {
                "text": story_text,
                "options": options,
                "is_true_end": is_true_end,
            }

        except Exception as e:
            # GLOBAL SAFE FALLBACK 
            print(Fore.RED + f"\n❌ AI Error: {e}" + Fore.RESET)
            print(Fore.YELLOW + "⚠️ The AI connection failed. You can retry later safely.")
            print(Fore.LIGHTCYAN_EX + "Your story progress has been saved.\n" + Fore.RESET)

            fallback_text = (
                "⚠️ AI service connection issue.\n"
                "Please check your internet or API key.\n"
                "Your progress is safe — you can continue later."
            )
            fallback_options = [
                "1. Retry generating this part.",
                "2. Change the story's direction.",
                "3. End the story for now.",
            ]
            return {
                "text": fallback_text,
                "options": fallback_options,
                "is_true_end": False,
            }
