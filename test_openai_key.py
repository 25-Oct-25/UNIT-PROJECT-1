import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY is not set in your .env file.")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

print("Attempting to generate an image with DALL-E 3...")

try:
    response = client.images.generate(
        model="dall-e-3",
        prompt="A majestic lion wearing a crown, cinematic style, vibrant colors, 4k",
        size="1024x1792", # حجم بوستر عمودي
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url # DALL-E 3 غالبًا يعطي رابط مباشر
    if image_url:
        print(f"Image generated successfully! URL: {image_url}")
        print("You can open this URL in your browser to see the image.")
    else:
        print("Failed to get image URL from OpenAI response.")
except Exception as e:
    print(f"An error occurred during DALL-E 3 image generation: {e}")
    print("\nPossible reasons:")
    print("1. Your API key might be invalid or expired.")
    print("2. Your OpenAI account might have insufficient credits or payment issues.")
    print("3. Network issues or temporary OpenAI service downtime.")
    print("4. Your account does not have access to DALL-E 3 (less common).")