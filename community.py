from datetime import datetime

#Create community class
class CommunityUser:

    #Initilize constructor
    def __init__(self, user_id:int ,name:str ,location:str ,email:str, password_number:str, registration_date = None):
        #Add attributes
        self.user_id = user_id
        self.name = name
        self.location = location
        self.email = email
        self.password_number = password_number
        self.registration_date = datetime.now()
    
    #Convert the characterstic of the user to dictionary to help us in json
    def to_dict(self):
        return{
        "user_id": self.user_id,
        "name": self.name,
        "location": self.location,
        "email":self.email,
        "password": self.password,
        "registration_date": self.registration_date.isoformat(),"user_type": "User"
        }

    #Update information
    def update_information(self,email:str, password_number:str):
        self.email = email
        self.password_number = password_number

        print("Your Email and Password updated")
        
    #Show user information
    def user_information(self):
        return f"User ID: {self.user_id}, Name: {self.name}, Location: {self.location}, Registered on: {self.registration_date}"
    
    def get_name(self):
        return self.name

#Test
user = CommunityUser(21,"Ahmed","riyadh","bora@gmail.com","123")
print (user.get_name())

