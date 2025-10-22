from email_validator import validate_email, EmailNotValidError
from collections.abc import Sized
from art import *
import json
from simultaneous_translation import quick_translator
from translator import TranslatorUser
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

#email check function
def check_email(email:str)-> bool:
    try:
        isValid = validate_email(email)
        email_address = isValid.email
        return True
        
    except EmailNotValidError as e:
        return False


#check input in file function
def check_input_in_file(user_input, file_path='"C:/Users/96654/Desktop/Python/Unit_Project/UNIT-PROJECT-1/language_short.txt'):
    
    check_input = user_input.strip()
    try:
        with open( file_path, 'r', encoding = 'UTF-8') as file:
            file_content = file.readlines()
            if check_input in file_content:
                return True
            else:
                return False
    except FileNotFoundError:
        print(f"There is wrong in the file path: {file_path} ")
    except Exception as e:
        print(f"There is error when read the file {e}")



#users list
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
    with open('translator_list.json', "w", encoding="UTF-8") as file:
        json_content = json.dumps(translator_list , indent=2)
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


        if len(translator_list) == 0:
            print("The list is empty, there is not translator available ..\n" \
            "Try later.")
        
        else: 
            #Print translators pre info  
            for user_list in translator_list:
                print(user_list.user_information())
            
            # for more specific kind of search choose one of the list below (Y/N)
            while True:
                specific_search = input("Do you want more specific search? 'y' for yes, 'n' for no ")
                if specific_search == 'y': 
                    search_type = input("What kind of translator are you looking for ?\n"
                    "1- Searching by type.\n"
                    "2- Searching by major.\n"
                    "3.Searching by location.\n") 

                    if search_type == "1":
                                            
                        search_phrase =  input ("\nEnter your translation type: ( 'Written Translator' or 'Interprter' )")
                    
                        #To search about the type and store it in list
                        search_result = list(filter(lambda translator: search_phrase in translator.translation_type , translator_list )) 
                        
                        #To print the search result
                        for index, trans_list in enumerate (search_result):
                            print(f"{index+1}- {trans_list.user_information()} ")
                        print("-*20")   
                    elif search_type == "2":

                        search_phrase = input ("\n Enter your translation major: ( 'Medical Translation' or 'Legal Translation' or 'Technical / Engineering Translation' or 'Creative Translation' or 'Diplomatic and Political Translation' )")
                        
                        #To search about the major and store it in list
                        search_result = list(filter(lambda translator: search_phrase in translator.translation_major , translator_list )) 
    
                        #To print the search result
                        for index, trans_list in enumerate (search_result):
                            print(f"{index+1}- {trans_list.user_information()} ")
                        print("-*20")     

                    elif search_type == "3":
                        
                        search_phrase = input ("\n Enter your location: ")
                        
                        #To search about the major and store it in list
                        search_result = list(filter(lambda translator: search_phrase in translator.location , translator_list )) 
    
                        #To print the search result
                        for index, trans_list in enumerate (search_result):
                            print(f"{index+1}- {trans_list.user_information()} ")
                        print("-*20")  

                    else: search_type = input("Wrong input, please enter a valid choice.")

                elif specific_search == 'n':
                    break

                else: specific_search = input("Wrong input, please enter a valid choice.")

    elif user_input == "2":
        if len(company_list) == 0:
            print("The list is empty, there is not translator available ..\n" \
            "Try later.") 
        else: 
            #Print company pre info  
            for user_list in company_list:
                print(user_list.user_information())
                       
            # for more specific kind of search choose one of the list below (Y/N)
            while True:
                specific_search = input("Do you want more specific search? 'y' for yes, 'n' for no ")
                if specific_search == 'y': 
                    search_type = input("What kind of translator are you looking for ?\n"
                    "1- Searching by type.\n"
                    "2- Searching by major.\n"
                    "3.Searching by location.\n") 

                    if search_type == "1":
                                            
                        search_phrase =  input ("\nEnter company translation type: ( 'Written Translator' or 'Interprter' )")
                    
                        #To search about the type and store it in list
                        search_result = list(filter(lambda company: search_phrase in company.translation_type , company_list )) 
                        
                        #To print the search result
                        for index, company_ls in enumerate (search_result):
                            print(f"{index+1}- {company_ls.user_information()} ")
                        print("-*20") 

                    elif search_type == "2":

                        search_phrase = input ("\n Enter company translation major: ( 'Medical Translation' or 'Legal Translation' or 'Technical / Engineering Translation' or 'Creative Translation' or 'Diplomatic and Political Translation' )")
                        
                        #To search about the major and store it in list
                        search_result = list(filter(lambda company: search_phrase in company.translation_major , company_list )) 
    
                        #To print the search result
                        for index, company_ls in enumerate (search_result):
                            print(f"{index+1}- {company_ls.user_information()} ")
                        print("-*20")     

                    elif search_type == "3":
                        
                        search_phrase = input ("\n Enter company location: ")
                        
                        #To search about the major and store it in list
                        search_result = list(filter(lambda company: search_phrase in company.location , company_list )) 
    
                        #To print the search result
                        for index, company_ls in enumerate (search_result):
                            print(f"{index+1}- {company_ls.user_information()} ")
                        print("-*20")  

                    else: search_type = input("Wrong input, please enter a valid choice.")

                elif specific_search == 'n':
                    break

                else: specific_search = input("Wrong input, please enter a valid choice.")


    elif user_input == "3":
        #To determine the user type if the user translator 
        # will create a new translator object and if the user is a company 
        # will create a new company object
        user_type = input("Who are you?\n" \
        "1- Translator.\n" \
        "2- Company.\n")
        if user_type == "1":
            #Add user information

            #Print a menu to tell the user what will be enter in the next
            print("To add a user translator we need a following information:\n" \
            "1- Translator name.\n" \
            "2- Translator location.\n" \
            "3- Translator email.\n" \
            "4- Translator gender.\n" \
            "5- Translator mother tongue.\n"\
            "6- Translator other language.\n"\
            "7- Translator major.\n" \
            "8- Translator type.\n" \
            "9- Is Translator have an offical certificate? ('True' or 'False')\n" \
            "10- How many years of experience do Translator have? (number) \n")

            
            #Add translator information
            translator_name = input("Enter your name: ")
            translator_location = input("Where are you live? ")
            translator_email = input("Enter your email: ")  
            
            #if statement to check if the user entered a right email or not
            #email check function
            if not check_email(translator_email):
                translator_email = input("Enter your email again: ")
                check_email(translator_email)
            
            translator_gender = input("Enter your gender: ( 'F' or 'Female' , 'M' or 'Male')")

            if translator_gender.lower() == 'f' or translator_gender.lower() == 'female':
                translator_gender = "Female"
            elif translator_gender.lower() == 'm' or translator_gender.lower() == 'male':
                translator_gender = "Male" 
            else: translator_gender = input("Wrong input! .. try again \n Enter your gender: ( 'F' or 'Female' , 'M' or 'Male')") 

            translator_mother_tongue = input ("Enter your mother tongue: ")
            other_language = input("Enter the other language you know: ")


            translator_major = input("Enter your translation major: ( 'MT' 'Medical Translation' or 'LT' 'Legal Translation' or 'IT' 'Technical / 'ENG' Engineering Translation' or 'CT' 'Creative Translation' or 'DPT' 'Diplomatic and Political Translation' ) ")
            
            if translator_major.lower() == 'medical translation' or translator_major.lower() == 'mt':
                translator_major = 'Medical Translation'
            elif translator_major.lower() == 'legal translation' or translator_major.lower() == 'lt':
                translator_major = 'Legal Translation'
            elif translator_major.lower() == 'technical translation' or translator_major.lower() == 'it':
                translator_major = 'Technical Translation'
            elif translator_major.lower() == 'engineering translation' or translator_major.lower() == 'eng':
                translator_major = 'Engineering Translation'
            elif translator_major.lower() == 'creative translation' or translator_major.lower() ==  'ct':
                translator_major = 'Creative Translation'
            elif translator_major.lower() == 'diplomatic and political translation' or translator_major.lower() == 'dpt':
                translator_major ='Diplomatic and Political Translation'
            else: translator_major = input("Wrong input! .. try again \n ")

            translation_type = input("Enter your translation type: ( 'W' or 'Written Translator' , I or 'Interprter' )")
            
            if translation_type.lower() == 'w' or translation_type.lower() == 'written translator':
                translation_type = 'Written Translator'
            elif translation_type.lower() == 'i' or translation_type.lower() == 'interprter':
                translation_type = 'Interprter'
            else: translation_type = input("Wrong input! .. try again \n Enter your translation type: ( 'W' or 'Written Translator' , I or 'Interprter' )")
            
            translator_certificate = input ("Enter 'T' or 'True' , 'F' or 'False' if you have official certificate: ")
            if translator_certificate.lower() == 'false' or translator_certificate.lower() == 'f':
                translator_certificate = False
            elif translator_certificate.lower() == 'true' or translator_certificate.lower() == 't':
                translator_certificate = True
            translator_experience_years = int( input("Enter a number of years of experience do you have: "))
            

    
            #name ,location ,email ,translation_major ,translation_type , gender:str, language:str,  official_certificate:bool,  years_of_experience:int=0 ,rate:int = 0, 
            translator_user = TranslatorUser(translator_name, translator_location, translator_email, translator_major,translation_type, translator_gender,  translator_mother_tongue, translator_certificate, translator_experience_years)
            translator_user.add_language(other_language)
            
            #append information to the list
            translator_list.append(translator_user.to_dict())


            #print Successful add
            print("New Translator added Successfully ...")
            
        elif user_type == "2":
            #Add a company user  information
            print("To add a user company we need a following information:\n" \
            "1- Company name.\n" \
            "2- Company location.\n" \
            "3- Company email.\n" \
            "4- The language want translator translate to it.\n"\
            "5- Company translator major.\n" \
            "6- Company translator type. ( 'Written Translator' , 'interprter' )\n" \
            "7- Company price offer for translator per hour\n" )
                        
            company_name = input("Enter Company name: ")
            company_location = input("Enter the company location: ")
            company_email = input("Enter your email: ")
            
            #if statement to check if the user entered a right email or not
            #email check function
            if not check_email(company_email):
                company_email = input("Enter your email again: ")
                check_email(company_email)

            company_translator_major = input("Enter the translator major:  ( 'MT' 'Medical Translation' or 'LT' 'Legal Translation' or 'IT' 'Technical / 'ENG' Engineering Translation' or 'CT' 'Creative Translation' or 'DPT' 'Diplomatic and Political Translation' ) ")
            
            if company_translator_major.lower() == 'medical translation' or company_translator_major.lower() == 'mt':
                company_translator_major = 'Medical Translation'
            elif company_translator_major.lower() == 'legal translation' or company_translator_major.lower() == 'lt':
                company_translator_major= 'Legal Translation'
            elif company_translator_major.lower() == 'technical translation' or company_translator_major.lower() == 'it':
                company_translator_major = 'Technical Translation'
            elif company_translator_major.lower() == 'engineering translation' or company_translator_major.lower() == 'eng':
                company_translator_major = 'Engineering Translation'
            elif company_translator_major.lower() == 'creative translation' or company_translator_major.lower() ==  'ct':
                company_translator_major = 'Creative Translation'
            elif company_translator_major.lower() == 'diplomatic and political translation' or company_translator_major.lower() == 'dpt':
                company_translator_major ='Diplomatic and Political Translation'
            else: company_translator_major = input("Wrong input! .. try again \n ") 

            company_translator_language = input("Enter the company translator language: (the language want translate it to)")
            
            company_translator_type = input("Enter the company translator type: ( 'W' or 'Written Translator', 'I' or 'Interprter'  )")

            if company_translator_type.lower() == 'w' or company_translator_type.lower() == 'Written Translator':
                company_translator_type = 'Written Translator'
            elif company_translator_type.lower() == 'i' or company_translator_type.lower() == 'interprter':
                company_translator_type = 'Interprter'
            else: company_translator_type = input("Wrong input! .. try again \n Enter your translation type: ( 'W' or 'Written Translator' , I or 'Interprter' )")
            

            company_price_offer = input("Enter the company price offer: ")

            #name, location, email, translate_to:str, translator_type:str, translator_major:str, price_offer:float
            company_user = Company( company_name, company_location, company_email, company_translator_language, company_translator_type, company_translator_major,company_price_offer)
            company_list.append(company_user.to_dict())
            print("New Company added Successfully ...")
        else: user_type = input("Wrong input, please enter a valid choice.")

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
        
        
        #check input characters 
        if(check_input_in_file(select_language)):
            print("Your translation text is: ", quick_translator(text_to_translate, select_language))
        else: select_language = input("Wrong input! .. try again \n Enter the character: ")
        
        print("Your translation text is: ", quick_translator(text_to_translate, select_language))
    elif user_input == "5":

        #save information to the file
        save_to_translator_list()

        #print a good bye sentence
        print("Thank you to visit our program, see you again.")
        break
    
    else: print("Wrong input, please enter a valid choice.")

