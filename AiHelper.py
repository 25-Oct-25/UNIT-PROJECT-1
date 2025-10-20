from huggingface_hub import InferenceClient
import os
class AIHelper:
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv('HF_API_KEY'))

    def generate_part(self, prompt, genre):
        system_message = f"You are a creative writer in {genre} genre. Create an interactive story with 3 choices where the user is the hero."
        try:
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model="mistralai/Mixtral-8x7B-Instruct-v0.1"
            )
            return response.choices[0].message.content 
        except Exception as e:
            return f"HF Error: {str(e)}"

# مثال للاستخدام
if __name__ == "__main__":
    ai_helper = AIHelper()
    result = ai_helper.generate_part("Start the story.", "fantasy")
    print(result)