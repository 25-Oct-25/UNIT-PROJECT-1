import json
import os
from .car_profile import Car

DIRICTION = os.path.dirname((__file__))

DATA_FILE= os.path.join(DIRICTION, "data", "DATA.json")

def save_cars(cars_list):
    """
    Saves the car obejct in a JSON format.
    """
    cars_data =[]
    for car in cars_list:
        cars_data.append(car.__dict__)
    with open (DATA_FILE, "w") as f:
        json.dump(cars_data,f, indent=4)

def load_cars():
    """
    Load the cars back into a list.
    """
    try:
        with open (DATA_FILE,"r") as f:
            cars_data = json.load(f)

            cars_list =[]

            for data in cars_data:
                cars_list.append(Car(**data))
            
            return cars_list
    
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
