# ai_advisor.py
import os
import google.generativeai as genai

class AIAdvisor:
    """
    An AI assistant using Google Gemini to provide advice on imported cars.
    """
    @staticmethod
    def get_advice(car,cost):
        """
        Asks Google Gemini for a brief purchasing advice on a specific car model.
        """
        try:
            #check if theres an API KEY
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "Error: GOOGLE_API_KEY environment variable not set."
            
            genai.configure(api_key=api_key)

            #use the model
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            #create the prompt
            prompt = (
                f"Act as a car import analyst for the Saudi Arabian market.\n"
                f"I have a deal for a {car.year} {car.make} {car.model} imported from {car.origin_country}.\n"
                f"My total calculated cost to get this car to Saudi Arabia is approximately {cost["total_cost"]:,.0f} SAR.\n\n"
                f"Your task is in two parts:\n"
                f"1. First, estimate the realistic resale price range for this car in the current Saudi market (e.g., on Haraj).\n"
                f"2. Second, compare your estimated price with my total cost. Based on this comparison, analyze the potential profit margin and provide a clear recommendation: is this a 'Good Deal', 'Average Deal', or 'Bad Deal'?\n"
                f"Provide the analysis in English."
            )

            #the API call
            response = model.generate_content(prompt)
            
            return response.text.strip()

        except Exception as e:
            return f"An error occurred: {e}"