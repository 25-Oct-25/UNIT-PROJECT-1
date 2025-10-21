import car_profile
import file_manager
import auth
from calculator import Calculator
from ai_advisor import AIAdvisor
from report_generator import save_ai_report_to_pdf

def show_menu(is_admin=False):
    print("\n--- Car Importer's Toolkit ---")
    
    if is_admin:
        print("1. Add a new car profile")
        print("2. View all car profiles")
        print("3. Calculate cost for a specific car")
        print("4. Get AI advice on a specific car")
        print("5. Update car price")
        print("6. Logout")
    else:
        print("1. Login as Admin")
        print("2. View all car profiles")
        print("3. Get AI advice on a specific car")
        print("4. Exit")

def main():
    cars = file_manager.load_cars()
    is_admin = False 

    while True:
        show_menu(is_admin)
        choice = input("Enter your choice: ")

        if is_admin:
            if choice == '1':
                try:
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
                except ValueError:
                    print("\n❌ Error: Year and Price must be valid numbers.")
                    continue

            elif choice == '2':
                if not cars:
                    print("\nNo car profiles found.")
                else:
                    for car in cars:
                        car.print_car_info()

            elif choice == '3':
                if not cars:
                    print("\nNo cars to calculate...")
                    continue
                print("\nSelect a car to calculate its total import cost:")
                for i, car in enumerate(cars):
                    print(f"[{i+1}] {car.year} {car.make} {car.model}")
                try:
                    car_choice = int(input("Enter the number of the car: "))
                    selected_car = cars[car_choice - 1]
                    cost_details = Calculator.calculate_total_cost(selected_car)
                    Calculator.print_colored_summary(cost_details)
                except (ValueError, IndexError):
                    print("\nInvalid selection.")

            elif choice == '4':
                    if not cars:
                        print("\nNo cars to analyze...")
                        continue
                    print("\nSelect a car to get AI advice:")
                    for i, car in enumerate(cars):
                        print(f"[{i+1}] {car.year} {car.make} {car.model}")
                    try:
                        car_choice = int(input("Enter the number of the car: "))
                        selected_car = cars[car_choice - 1]
                        cost = Calculator.calculate_total_cost(selected_car)
                        
                        print("\n🧠 Asking the AI for advice... Please wait.")
                        advice = AIAdvisor.get_advice(selected_car, cost)

                        print("\n--- AI Advisor ---")
                        print(advice)
                        print("------------------")
                        
                        save_choice = input("Do you want to save this analysis as a PDF? (y/n): ").lower()
                        if save_choice == 'y':
                            filename = f"AI_Report_{selected_car.make}_{selected_car.model}_{selected_car.year}.pdf"
                            save_ai_report_to_pdf(selected_car, cost, advice, filename)

                    except (ValueError, IndexError):
                        print("\nInvalid selection.")


            elif choice == '5':
                if not cars:
                    print("\nNo cars to update. Please add a car first.")
                    continue

                print("\nSelect a car to update its price:")
                for i, car in enumerate(cars):
                    print(f"[{i+1}] {car.year} {car.make} {car.model} (Current Price: ${car.price_usd:,.2f})")
                
                try:
                    car_choice = int(input("Enter the number of the car: "))
                    selected_car = cars[car_choice - 1]

                    new_price = input(f"Enter the new price for {selected_car.make} (Current: ${selected_car.price_usd:,.2f}): ")
                    price_usd = float(new_price)

                    selected_car.price_usd = price_usd
                    
                    file_manager.save_cars(cars)
                    
                    print(f"\n✅ Price updated successfully for {selected_car.make} {selected_car.model}.")

                except (ValueError, IndexError):
                    print("\n❌ Invalid selection or price. Please try again.")
                    

            elif choice == '6':
                is_admin = False 
                print("\nLogged out successfully.")
            else:
                print("\nInvalid choice. Please try again.")
        
        else:
            if choice == '1':
                if auth.login():
                    is_admin = True
            
            elif choice == '2':
                if not cars:
                    print("\nNo car profiles found.")
                else:
                    for car in cars:
                        car.print_car_info()
            elif choice == '3':
                if not cars:
                    print("\nNo cars to analyze...")
                    continue
                print("\nSelect a car to get AI advice:")
                for i, car in enumerate(cars):
                    print(f"[{i+1}] {car.year} {car.make} {car.model}")
                try:
                    car_choice = int(input("Enter the number of the car: "))
                    selected_car = cars[car_choice - 1]
                    cost = Calculator.calculate_total_cost(selected_car)
                    
                    print("\n🧠 Asking the AI for advice... Please wait.")
                    advice = AIAdvisor.get_advice(selected_car, cost)

                    print("\n--- AI Advisor ---")
                    print(advice)
                    print("------------------")
                    
                    save_choice = input("Do you want to save this analysis as a PDF? (y/n): ").lower()
                    if save_choice == 'y':
                        filename = f"AI_Report_{selected_car.make}_{selected_car.model}_{selected_car.year}.pdf"
                        save_ai_report_to_pdf(selected_car, cost, advice, filename)

                except (ValueError, IndexError):
                    print("\nInvalid selection.")
            
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()