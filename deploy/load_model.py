import tensorflow as tf
from tensorflow.keras.applications import VGG19
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam

from tensorflow.keras.models import load_model
from tensorflow.keras.applications import MobileNetV2
import joblib
import cv2
import numpy as np

le=joblib.load("deploy/le.pkl")

la={
    0:'thaa',
    1:'dha',
    2:'seen',
    3:'ya',
    4:'meem',
    5:'saad',
    6:'thal',
    7:'kaaf',
    8:'nun',
    9:'dal',
    10:'bb',
    11:'ain',
    12:'dhad',
    13:'taa',
    14:'yaa',
    15:'ghain',
    16:'ta',
    17:'waw',
    18:'sheen',
    19:'fa',
    20:'laam',
    21:'aleff'
}


def load_mdoel():
        
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = Flatten()(x)
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(22, activation='softmax')(x)  

    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.load_weights("deploy/MobileNetV2.h5")
    
    return model

model=load_mdoel()


def predict_image(image_path):
  
    image=cv2.imread(str(image_path))
    imageee=cv2.resize(image,(224,224))
    imageee=cv2.cvtColor(imageee,cv2.COLOR_BGR2RGB)
    imageee=imageee/255.0
    res= model.predict(np.array([imageee])) 
    return la[np.argmax(res)]



def get_letter(letter:str):
    arabic_letters_dict = {
    'ain': 'ع',
    'al': 'ال',
    'aleff': 'ا',
    'bb': 'ب',
    'dal': 'د',
    'dha': 'ظ',
    'dhad': 'ض',
    'fa': 'ف',
    'gaaf': 'ج',
    'ghain': 'غ',
    'ha': 'ه',
    'haa': 'ح',
    'jeem': 'ج',
    'kaaf': 'ك',
    'khaa': 'خ',
    'la': 'لا',
    'laam': 'ل',
    'meem': 'م',
    'nun': 'ن',
    'ra': 'ر',
    'saad': 'ص',
    'seen': 'س',
    'sheen': 'ش',
    'ta': 'ت',
    'taa': 'ط',
    'thaa': 'ث',
    'thal': 'ذ',
    'toot': 'ت',
    'waw': 'و',
    'ya': 'ي',
    'yaa': 'ى',
    'zay': 'ز'
    }
    
    return arabic_letters_dict[letter] 