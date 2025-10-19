from collections.abc import Sized
from art import *
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
#Writting welcom message
tprint("Welcome To \nTransolter \n Comunity")

#create a choice number variable
choice_number = 0

#Display th program
while True:
    user_input = input("What are you looking for ? \n" \
    "1- Freelance translator.\n" \
    "2- Corporate offers for translators.\n" \
    "3- Join the community.\n"\
    "4- Simultaneus translation.\n" \
    "5- Exit")

    if(user_input == "5"):
        print("Thank you to visit our program, see you again.")
        break
    if(user_input == "4"):
        pass