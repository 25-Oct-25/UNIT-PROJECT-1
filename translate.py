from deep_translator import GoogleTranslator

def translate_to_arabic(text):
    try:
        translated = GoogleTranslator(source='auto', target='ar').translate(text)
        return translated
    except Exception as e:
        return f"Translation failed: {e}"

