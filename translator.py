from community import CommunityUser

#Create translator class
class TranslatorUser(CommunityUser):

    #Initilize constructor
    def __init__(self, name ,location ,email ,translation_major ,translation_type ,registration_date , gender:str, major:str,language:str,  official_certificate:bool,  years_of_experience:int=0 ,rate:int = 0, more_language_list=[]):
        super().__init__(name, location,email, translation_major, translation_type,registration_date )
        self.gender = gender
        self.major = major
        self.language = language
        self.more_language_list = more_language_list
        self.more_language_list = []
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
            "more_language_list": self.more_language_list,
            "years_of_experience": self.years_of_experience,
            "official_certificate": self.official_certificate,
            "rate":self.rate
            }
    
    #To add more than one language can traslate
    def add_language(self,lang):
       
        self.more_language_list.append(lang)
    
    #Method to print a language list
    def show_language_list(self):
        i = 0 
        while self.more_language_list:
            if i == len(self.more_language_list):
                break
            print(self.more_language_list[i], end=" ")
            i +=1

    #Method for print Translator information
    def user_information(self):
        return f"User name: {self.name}, Location: {self.location}, Gender: {self.gender}, Major: {self.major}, Mother language: {self.language}, and other languages: {self.show_language_list()}, Offical certificates: {self.official_certificate}, Years of exoerience: {self.years_of_experience}, Rate: {self.rate}"


#Test
#user = TranslatorUser("Bora","Riyadh","bora@gmail.com","Female","clinc", "Arabic", True, 4, 2, "Korean")
#print(user.user_information())
#user.add_language("English")
#print(user.user_information())
