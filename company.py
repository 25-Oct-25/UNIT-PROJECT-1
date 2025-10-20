from community import CommunityUser

#Create company class
class Company(CommunityUser):
    def __init__(self, user_id, name, location, email, password_number):
        super().__init__(user_id, name, location, email, password_number)
    