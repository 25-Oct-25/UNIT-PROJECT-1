#import translator package
from googletrans import Translator

#Create object


#Create  a translation function
def quick_translator (phrase:str, target_language:str) ->str:
    '''
    The function has two parameters : the first one for the text
    and the second one for a target language
    The function return the text after translate
    '''
    translator = Translator()
    #Call Translate method
    translated_phrase = translator.translate(phrase, dest = target_language)
    return translated_phrase.text


#Function test
print(quick_translator("مرحبا بالعالم","ko"))
