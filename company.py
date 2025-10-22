from community import CommunityUser

#Create company class
class Company(CommunityUser):

    #Initilize constructor
    def __init__(self, name ,location ,email ,translation_major ,translation_type ,registration_date , translate_to:str, translator_type:str, translator_major:str, price_offer:float):

        super().__init__( name, location, email ,translation_major ,translation_type ,registration_date ) 
        self.translate_to = translate_to
        self.translator_type = translator_type
        self.translator_major = translator_major
        self.price_offer = price_offer
    
    #Convert the characterstic of the user to dictionary to help us in json
    def to_dict(self):
        super().to_dict()
        return {
            "translate_to": self.translate_to,
            "translator_type": self.translator_type,
            "translator_major": self.translator_major,
            "price_offer" : self.price_offer
        }
    
    #Method for print Translator information
    def user_information(self):
        return f"Cmpany name: {self.name}, Location: {self.location}, The language required: {self.translate_to},Translator type: {self.translator_type}, Translator major: {self.translator_major}"

#Test
#company1 = Company("Naver","South Korea","info@naver.kr","Arabic","Face to Face","Technical",200)
#print(company1.user_information())

