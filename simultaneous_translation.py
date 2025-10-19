#import translator package
from googletrans import Translator

#Create object
translator = Translator()

#Create  a transtion function
def quick_translator (phrase:str, target_language:str)->str:
    user_input = phrase

    #Create a variable to find the language of the phrase
    detect_lang = translator.detect(user_input).lang
    print(detect_lang)

    #Call Translate method
    translated_phrase = translator.translate(user_input, dest = target_language)
    return translated_phrase


#Function test
sent = "Hello world"
print(quick_translator(sent, "ar"))
'''
print(quick_translator(sent,"kr"))
print(quick_translator(sent, "zh"))
print(quick_translator(sent,"jp"))
'''