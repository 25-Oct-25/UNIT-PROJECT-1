from community import CommunityUser

#Create translator class
class Translator(CommunityUser):
    def __init__(self, user_id, name, email, password_number, languges ):
        super().__init__(user_id, name, email, password_number)
        self.name = name
    pass

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

#Test
user = Translator(21,"Ahmed","bora@gmail.com", 321) 
print(user.get_name())
user_name = Translator()
user_name.set_name("mohammed")
print(user_name.get_name())