from huggingface_hub import InferenceClient
import os

class AIHelper:
    def __init__(self):
        """
        initial the connection to the hugging face Ai
        """
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please check your .env file.")
        self.client = InferenceClient(api_key=api_key)

    def generate_part(self, prompt, genre, length="short"):
        """
        generate new part of the story with 3 user choices
        allows control over story length (short or long)
        """
        # system message that instructs the AI model how to write
        system_message = (
        f"You are a talented creative writer who writes {genre} stories. "
        f"This story should be {'brief and concise' if length == 'short' else 'detailed and immersive'}. "
        f"Continue the story in the same tone and style. "
        f"If the story has reached its natural conclusion, end it gracefully and write 'THE END'. "
        f"Otherwise, after the story, provide EXACTLY THREE numbered choices (1, 2, and 3) for what happens next."
    )

        try:
            # requst the model to generate the next story part
            response = self.client.chat_completion(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400 if length == "short" else 800,
                temperature=0.9
            )

            story_text = response.choices[0].message["content"]
            print("\n" + story_text)

            # extract choices (1,2,3) from the story 
            options = []
            for line in story_text.split("\n"):
                if line.strip().startswith(("1.", "2.", "3.")):
                    options.append(line.strip())

            # display option to the user
            if options:
                print("\n Choose what happens next:")
                for opt in options:
                    print(opt)

                choice = input("\nEnter your choice (1-3): ").strip()
                if choice not in ["1", "2", "3"]:
                    print("Invalid choice. Continuing with option 1.")
                    choice = "1"

                # generate new part of the story based on the selcted option
                followup_prompt = (
                    f"{prompt}\nThe reader chose option {choice}. Continue the story accordingly. "
                    f"Keep the same tone and detail level ({length})."
                )

                next_response = self.client.chat_completion(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": followup_prompt}
                    ],
                    max_tokens=400 if length == "short" else 800,
                    temperature=0.9
                )

                continuation = next_response.choices[0].message["content"]
                print("\n" + continuation)

                # merge the orignal story with the continuation
                return {
                    "text": prompt + "\n\n" + story_text + "\n\n" + continuation,
                    "choice": choice
                }

            else:
                # in case the model didn't provide any choices
                return {
                    "text": story_text,
                    "choice": None
                }

        except Exception as e:
            return {
                "text": f"HF API Error: {str(e)}",
                "choice": None
            }
