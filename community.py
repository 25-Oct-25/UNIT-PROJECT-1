from datetime import datetime
import json

#Create community class
class CommunityUser:

    #Initilize constructor
    def __init__(self,name:str ,location:str ,email:str ,translation_major:str ,translation_type:str ,registration_date = None):
        #Add attributes
        self.name = name
        self.location = location
        self.email = email
        self.translation_major = translation_major
        self.translation_type = translation_type
        self.registration_date = datetime.now()
    
    #Convert the characterstic of the user to dictionary to help us in json
    def to_dict(self):
        return{
        "name": self.name,
        "location": self.location,
        "email":self.email,
        "translation_major": self.translation_major,
        "translation_type": self.translation_type,
        "registration_date": self.registration_date.isoformat(),
        "user_type": "User"}
    
    #Write a method to set a user id attribute and check if the enter value is right or not (just accept a name)

    #Write a method to check if the enter email is a valid email or not

    #Update information
    def update_information(self,email:str):
        self.email = email

        print("Your Email updated")
        
    #Show user information
    def user_information(self):
        return f"User name: {self.name}, Location: {self.location}, Translation major: {self.translation_major}, Translation type: {self.translation_type}, Contact information: {self.email} "
        #return f"User name: {self.name}, Location: {self.location}, Translation major: {self.translation_major}, Translation type: {self.translation_type}, Contact information: {self.email} Registered on: {self.registration_date}"
    
    


'''
#Test
user = CommunityUser(21,"Ahmed","riyadh","bora@gmail.com","123")
print (user.user_information())
'''

