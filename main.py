from email_validator import validate_email, EmailNotValidError
#from collections.abc import Sized
from art import *
import json
from simultaneous_translation import quick_translator
from translator import Translator
from company import Company
"""

welcome message shows in the begining of the program

Menu:
1- Add company
2- Add freelancer (Transolator)
3- Show a company list
    -choose one of the companies to show more information
    and can contanct with them ( Request order )
4- Show a freelancer list
    -choose one of the freelancers to show more information
    and can contact with them ( Request order )
5- Search by city for companies or freelancer 
    -check if the freelancer available to work in this city (location)
6- Search by specific name of company or freelancer 


"""

def check_email(email:str)-> bool:
    try:
        isValid = validate_email(email)
        email_address = isValid.email
        return True
        print(f'{email_address} The email is correct')
        
    except EmailNotValidError as e:
        return False
        print(f"{str(e)} The email unvalid")
        


translator_list = []
company_list = []

#create json read function for translator
def load_to_translator_list():
    global translator_list
    try: 
        with open('translator_list.json','r', encoding = "UTF-8" ) as file:
            content = file.read()
            translator_list = json.loads(content)
    except:
        pass

#create json read function for company
def load_to_company_list():
    global company_list
    try: 
        with open('company_list.json','r', encoding = "UTF-8" ) as file:
            content = file.read()
            company_list = json.loads(content)
    except:
        pass

#create json write function for translator
def save_to_translator_list():
    with open('translator_list.json','w', encoding = "UTF-8") as file:
        json_content = json.dump(translator_list, indent = 2)
        file.write(json_content)

#create json write function for company
def save_to_company_list():
    with open('company_list.json','w', encoding = "UTF-8") as file:
        json_content = json.dump(company_list, indent = 2)
        file.write(json_content)

#Writting welcom message
tprint("Welcome To \nTransolter \n Comunity")

load_to_translator_list()

#Display th program
while True:
    user_input = input("What are you looking for ? \n" \
    "1- Freelance translator.\n" \
    "2- Corporate offers for translators.\n" \
    "3- Join the community.\n"\
    "4- Simultaneus translation.\n" \
    "5- Exit \n")

    if user_input == "1":

        #Print translators pre info  
        if len(translator_list) == 0:
            print("The list is empty, there is not translator available ..\n" \
            "Try later.")
        # for more specific kind of search choose one of the list below

        search_type = input("What kind of translator are you looking for ?\n"
        "1- Searching by type.\n"
        "2- Searching by major.\n"
        "3.Searching by location.\n") 

        if search_type == "1":
            search_phrase = input("Enter searching type: ")
            search_result = list(filter(lambda translator: search_phrase ))
            for index, trans_list in enumerate (translator_list):

                pass
        elif search_type == "2":
            pass
        elif search_type == "3":
            pass
        else: print("Wrong input, please enter a valid choice.")

    elif user_input == "2":
        pass
    elif user_input == "3":
        #To determine the user type if the user translator 
        # will create a new translator object and if the user is a company 
        # will create a new company object
        user_type = input("Who are you?\n" \
        "1- Translator.\n" \
        "2- Company.\n")
        if user_input == "1":
            #Add user information

            #Print a menu to tell the user what will be enter in the next
            print("To add a user name we need a following information:\n" \
            "1- Translator name.\n" \
            "2- Translator location.\n" \
            "3- Translator email.\n" \
            "4- Translator gender.\n" \
            "5- Translator major.\n" \
            "6- Translator mother tongue.\n" \
            "7- Is Translator have an offical certificate? ('True' or 'False')\n" \
            "9- How many years of experience do Translator have? (number) \n")

            
            #Add translator information
            user_name = input("Enter your name: ")
            user_location = input("Where are you live? ")
            user_email = input("Enter your email: ")  
            
            #if statement to check if the user entered a right email or not
            #email check function
            if check_email(user_email):
                continue
            else: 
                user_email = input("Enter your email again: ")
            
            user_gender = input("Enter your gender: ")
            user_major = input("Enter your major: ")
            user_mother_tongue = input ("Enter your mother tongue: ")
            user_certificate = input ("Enter 'True' or 'False' if you have official certificate: ")
            user_experience_years = int( input("Enter a number of years of experience do you have: "))
            

    
            #name, location, email, gender, major, language,  official_certificate, years_of_experience 
            user = Translator(user_name, user_location, user_email, user_gender, user_major, user_mother_tongue, user_certificate, user_experience_years)
            translator_list.append(user)
            print("New Translator added Successfully ...")
            
        elif user_type == "2":
            #Add user information
            user_name = input("Enter your name: ")
            user_location = input("Where are you live? ")
            user_email = input("Enter your email: ")#I should check if the email format is valid or not
            user_password = input("Enter your password: ")
            
            #name, location, email, translate_to:str, translator_type:str, translator_major:str, price_offer:float
            user = Company( user_name, user_location, user_email, user_password)
            company_list.append(user)
            
          
        else: print("Wrong input, please enter a valid choice.")

    elif user_input == "4":
        #ask a user to enter the text want translate
        text_to_translate = input("Enter the text want to translate: ")
        select_language = input("Enter a language charachter want to translate to it from the list:\n" \
        "-'ar' for Arabic.\n" \
        "-'en' for English.\n" \
        "-'es' for Spanish.\n" \
        "-'de' for German.\n" \
        "-'zh-cn' or 'zh' for Chinese.\n" \
        "-'ja' for Japanese.\n" \
        "-'ko' for Korean.\n" \
        "-'ru' for Russian.\n" \
        "-'tr' for Turkish.\n" \
        "-'it' for Italian.\n" )
        print("Your translation text is: ", quick_translator(text_to_translate, select_language))
    
    elif user_input == "5":
        #save the content to the file
        save_to_translator_list()
        save_to_company_list()
        #print a good bye sentence
        print("Thank you to visit our program, see you again.")
        break
    
    else: print("Wrong input, please enter a valid choice.")

