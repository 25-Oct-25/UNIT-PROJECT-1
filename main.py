from halo import Halo
from toolkit.car_profile import Car
from toolkit.file_manager import load_cars, save_cars
from toolkit.auth import login
from toolkit.calculator import Calculator
from toolkit.ai_advisor import AIAdvisor
from toolkit.report_generator import save_ai_report_to_pdf

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
        print("3. Buy a car")
        print("4. Get AI advice on a specific car")
        print("5. Exit")

def handle_ai_advice(cars_list):
    if not cars_list:
        print("\nNo cars found to analyze.") 
        return
    
    print("\nSelect a car to get AI advice:")
    for i, car in enumerate(cars_list): 
         print(f"[{i+1}] {car.year} {car.make} {car.model}")
    
    try:
        car_choice = int(input("Enter the number of the car: "))
        selected_car = cars_list[car_choice - 1] 
        cost = Calculator.calculate_total_cost(selected_car)

        spinner = Halo(text='Asking the AI for advice... Please wait.', spinner='dots')
        spinner.start()
        advice = AIAdvisor.get_advice(selected_car, cost)

        if advice.startswith("Error:") or advice.startswith("An error occurred:"):
            spinner.fail(advice)
        else:
            spinner.succeed("Got it!")
            print(advice)
            print("------------------")
         
        save_choice = input("Do you want to save this analysis as a PDF? (y/n): ").lower()
        if save_choice == 'y':
            filename = f"AI_Report_{selected_car.make}_{selected_car.model}_{selected_car.year}.pdf"
            save_ai_report_to_pdf(selected_car, cost, advice, filename)

    except (ValueError, IndexError):
        print("\nInvalid selection.")

def main():
    cars = load_cars()
    is_admin = False 

    while True:
        show_menu(is_admin)
        choice = input("Enter your choice: ")
        #Admin part
        if is_admin:
            if choice == '1':
                try:
                    print("\nEnter the details for the new car:")
                    make = input("Make: ")
                    model = input("Model: ")
                    year = int(input("Year: ")) 
                    price_usd = float(input("Price (USD): "))
                    origin = input("Origin Country: ")
                    new_car = Car(make, model, year, price_usd, origin)
                    cars.append(new_car)
                    save_cars(cars)
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
                handle_ai_advice(cars)




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

                    new_price_str = input(f"Enter the new price for {selected_car.make} (Current: ${selected_car.price_usd:,.2f}): ")
                    new_price_usd = float(new_price_str)

                    selected_car.price_usd = new_price_usd
                    save_cars(cars)
                    
                    print(f"\n✅ Price updated successfully for {selected_car.make} {selected_car.model}.")

                except (ValueError, IndexError):
                    print("\n❌ Invalid selection or price. Please try again.")

            elif choice == '6':
                is_admin = False 
                print("\nLogged out successfully.")
            else:
                print("\nInvalid choice. Please try again.")



        #Guest part
        else:
            available_cars = [car for car in cars if car.status == "For Sale"]
            if choice == '1':
                if login():
                    is_admin = True
                else:
                    print("\nSorry, wrong password or username")
                    continue
            
            elif choice == '2':
                if not available_cars:
                    print("\nNo car profiles found.")
                else:
                    for car in available_cars:
                        car.print_car_info()



            elif choice =='3':
                if not available_cars:
                    print("\nSorry, no cars are available for sale right now.")
                    continue

                print("\nSelect a car to purchase:")
                for i, car in enumerate(available_cars):
                    print(f"[{i+1}] {car.year} {car.make} {car.model} - ${car.price_usd:,.2f}")
                
                try:
                    car_choice_idx = int(input("Enter the number of the car you wish to buy: "))
                    selected_car = available_cars[car_choice_idx - 1]

                    selected_car.status = "Sold"
                    save_cars(cars)
                    
                    print(f"\n✅ Congratulations! You have purchased the {selected_car.make} {selected_car.model}.")
                    print("An admin will contact you shortly.")

                except (ValueError, IndexError):
                    print("\n❌ Invalid selection. Please try again.")




            elif choice == '4':
                handle_ai_advice(available_cars)


            
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()