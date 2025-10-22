import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

file_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products.json'
reviews_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/comments_ratings.json'
products_most_solds_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products_most_sold.json'

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def chat_with_ai():

    # Load Products (Crucial data)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No product data found! Cannot proceed.")
        return # Cannot continue without products

    # Load Reviews (Optional data for recommendation)
    try:
        with open(reviews_path, "r", encoding="utf-8") as f:
            reviews = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No reviews data found. Providing recommendations without review data.")
        reviews = [] # Initialize as empty list

    # Load Sales Data (Optional data for recommendation)
    try:
        with open(products_most_solds_path, "r", encoding="utf-8") as f:
            most_sold_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No sales data found. Providing recommendations without sales data.")
        most_sold_data = {} # Initialize as empty dictionary

    query = input("\n🤖 Gemini Assistant: Hi! What are you looking for today? 💬\n👉 ")

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are a shopping assistant. The user asked: {query}.
Here is the product list, product sales, and product reviews (in JSON):
Products: {json.dumps(products, indent=2)}
Reviews: {json.dumps(reviews, indent=2)}
Most Sold: {json.dumps(most_sold_data, indent=2)}

Find the best matching product(s) and explain why it's a good choice.
    """

    try:
        response = model.generate_content(prompt)
        print("\n🧠 Gemini Recommendation:\n")
        print(response.text)
    except Exception as e:
        print(f"\n❌ Error while calling Gemini API:\n{e}")
