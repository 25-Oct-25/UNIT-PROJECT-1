import car_profile
import file_manager
from calculator import Calculator
from ai_advisor import AIAdvisor




def show_menu():
    """Displays the main menu to the user."""
    print("\n--- Car Importer's Toolkit ---")
    print("1. Add a new car profile")
    print("2. View all car profiles")
    print("3. Calculate cost for a specific car")
    print("4. Get AI advice on a specific car")
    print("5. Exit")

def main():
    cars = file_manager.load_cars()

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            #Gives The Car Details
            print("\nEnter the details for the new car:")
            make = input("Make: ")
            model = input("Model: ")
            year = int(input("Year: ")) 
            price_usd = float(input("Price (USD): "))
            origin = input("Origin Country: ")
            new_car = car_profile.Car(make, model, year, price_usd, origin)
            cars.append(new_car)
            file_manager.save_cars(cars)
            print(f"\n✅ Successfully added {year} {make} {model}!")

        elif choice == '2':
            # ... (code for viewing cars) ...
            if not cars:
                print("\nNo car profiles found. Add one first!")
            else:
                for car in (cars):
                    car_profile.Car.print_car_info(car)
                    

        elif choice == '3':
            # ... (code for calculating cost) ...
            if not cars:
                print("\nNo cars to calculate. Please add a car first.")
                continue
            print("\nSelect a car to calculate its total import cost:")
            for i, car in enumerate(cars):
                print(f"[{i+1}] {car.year} {car.make} {car.model}")
            try:
                car_choice = int(input("Enter the number of the car: "))
                selected_car = cars[car_choice - 1]
                cost_details = Calculator.calculate_total_cost(selected_car)
                print("\n--- Cost Calculation Report ---")
                selected_car.display()
                # print(f"  Base Price SAR: ${cost_details['base_price']:,.2f}")
                # print(f"  Shipping SAR:   +{cost_details['shipping']:,.2f}")
                # print(f"Insurance SAR:   +{cost_details['insurance']:,.2f}")
                # print(f"  Customs (5%) SAR: +{cost_details['customs']:,.2f}")
                # print(f"  VAT (15%) SAR:    +{cost_details['vat']:,.2f}")
                # print("---------------------------------")
                # print(f"  TOTAL ESTIMATED COST IN SAR: SAR{cost_details['total_cost']:,.2f}")
                # print("---------------------------------")
                Calculator.print_colored_summary(cost_details)
            except (ValueError, IndexError):
                print("\nInvalid selection. Please enter a valid number from the list.")

        elif choice == '4':
            #Get AI Advice
            if not cars:
                print("\nNo cars to analyze. Please add a car first.")
                continue

            print("\nSelect a car to get AI advice:")
            for i, car in enumerate(cars):
                print(f"[{i+1}] {car.year} {car.make} {car.model}")
            
            try:
                car_choice = int(input("Enter the number of the car: "))
                selected_car = cars[car_choice - 1]
                cost = Calculator.calculate_total_cost(selected_car)
                print("\n🧠 Asking the AI for advice... Please wait.")
                advice = AIAdvisor.get_advice(selected_car,cost)

                print("\n--- AI Advisor ---")
                print(advice)
                print("------------------")

            except (ValueError, IndexError):
                print("\nInvalid selection. Please enter a valid number from the list.")

        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()