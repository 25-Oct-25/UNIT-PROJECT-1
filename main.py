from collections.abc import Sized
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

users_list = []

#Writting welcom message
tprint("Welcome To \nTransolter \n Comunity")



#Display th program
while True:
    user_input = input("What are you looking for ? \n" \
    "1- Freelance translator.\n" \
    "2- Corporate offers for translators.\n" \
    "3- Join the community.\n"\
    "4- Simultaneus translation.\n" \
    "5- Exit \n")

    if user_input == "5":
        #print a good bye sentence
        print("Thank you to visit our program, see you again.")
        break
    if user_input == "4":
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
    if user_input == "3":
        #To determine the user type if the user translator 
        # will create a new translator object and if the user is a company 
        # will create a new company object
        user_type = input("Who are you?\n" \
        "1- Translator.\n" \
        "2- Company.\n")
        if user_input == "1":
            #Add user information
            user_id = int(input("Enter your id by number: "))
            user_name = input("Enter your name: ")
            user_location = input("Where are you live? ")
            user_email = input("Enter your email: ")#I should check if the email format is valid or not
            user_password = input("Enter your password: ")
            user = Translator(user_id, user_name, user_location, user_email, user_password)
            users_list.append(user)
            
        elif user_type == "2":
            #Add user information
            user_id = int(input("Enter your id by number: "))
            user_name = input("Enter your name: ")
            user_location = input("Where are you live? ")
            user_email = input("Enter your email: ")#I should check if the email format is valid or not
            user_password = input("Enter your password: ")
            user = Company(user_id, user_name, user_location, user_email, user_password)
            users_list.append(user)
            
            
        else: print("Wrong input, try again")

        pass

