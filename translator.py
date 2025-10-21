from community import CommunityUser

#Create translator class
class Translator(CommunityUser):

    #Initilize constructor
    def __init__(self, name,location, email, gender:str, major:str,language:str,  official_certificate:bool, rate:int, years_of_experience:int=0 , more_language=[]):
        super().__init__(name, location,email)
        self.gender = gender
        self.major = major
        self.language = language
        self.language_list = more_language
        self.years_of_experience = years_of_experience
        self.official_certificate = False
        self.rate = rate
    
    #Convert the characterstic of the user to dictionary to help us in json
    def to_dict(self):
        super().to_dict()
        return {
            "gender": self.gender,
            "major": self.major,
            "language": self.language,
            "more_language": self.language_list,
            "years_of_experience": self.years_of_experience,
            "official_certificate": self.official_certificate,
            "rate":self.rate
            }
    
    #To add more than one language can traslate
    def add_language(self,lang:str):
       
        self.language_list.append(lang)
    
    #Method to print a language list
    def show_language_list(self):
        if len(self.language_list) == 0 :
            print("Nothing")
        else:
            print(self.language_list)


    #Method for print Translator information
    def user_information(self):
        return f"User name: {self.name}, Location: {self.location}, Gender: {self.gender}, Major: {self.major}, Mother language: {self.language}, and other languages: {self.show_language_list()}, Offical certificates: {self.official_certificate}, Years of exoerience: {self.years_of_experience}, Rate: {self.rate}"


#Test
user = Translator("Bora","Riyadh","bora@gmail.com","Female","clinc", "Arabic", True, 4, 2, "Korean")
print(user.user_information())
user.add_language("English")
print(user.user_information())
