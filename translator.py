from community import CommunityUser

#Create translator class
class Translator(CommunityUser):

    #Initilize constructor
    def __init__(self, user_id, name,location, email, password_number, gender:str, major:str,language:str,  official_certificate:bool,years_of_experience:int=0):
        super().__init__(user_id, name, location,email, password_number)
        self.gender = gender
        self.major = major
        self.language = language
        self.language_list = []
        self.years_of_experience = years_of_experience
        self.official_certificate = official_certificate
    
    #Convert the characterstic of the user to dictionary to help us in json
    def to_dict(self):
        super().to_dict()
        return {
            "gender": self.gender,
            "major": self.major,
            "language": self.language,
            "official_certificate": self.official_certificate,
            "years_of_experience": self.years_of_experience
        }
    
    #To add more than one language can traslate
    def add_language(self,lang:str):
       
         #is every time run the code set to empty?!! or if i call the method twice?!!
        self.language = lang
        self.language_list.append(self.language)
    
    #Method to return a language list
    def get_language(self):
        return self.language_list #Should i write self.language_list?!!

    '''   
        def add_certificate(self, certificate:str):
            global certificate_list 
            self.official_certificate = certificate
            certificate_list.append(self.official_certificate)
        
        def get_certificate(self):
            return certificate_list #Should I write self.language_list?!!
    '''

    #Method for print Translator information
    def user_information(self):
        return f"User ID: {self.user_id}, Name: {self.name}, Location: {self.location},Gender: {self.gender}, Major: {self.major}, Languages: {self.get_language()}, Offical certificates: {self.get_certificate()}, Years of exoerience: {self.years_of_experience}"


#Test
user = Translator("Bora_94", "Bora","Riyadh","bora@gmail.com","123a123","Female", "IT", "Arabic", True, 1)
print(user.user_information())
user.add_language("Korean")
print(user.user_information())
