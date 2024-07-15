import os
import hashlib
from datetime import datetime
from abc import ABC, abstractmethod

# Abstract class (LibraryItem)
class LibraryItem(ABC):
    def __init__(self, title, price):
        self.title = title
        self.price = price

    @abstractmethod
    def display(self):
        pass

# Product class (inherits from LibraryItem)
class Product(LibraryItem):
    def __init__(self, title, price, stock_quantity):
        super().__init__(title, price)
        self.stock_quantity = stock_quantity

    # Method Overloading eg.
    def display(self):
        print(f"Product: {self.title} - Rs.{self.price} - Stock: {self.stock_quantity}")

    def update_stock(self, quantity):
        self.stock_quantity += quantity
        if self.stock_quantity < 0:
            self.stock_quantity = 0  # Ensure stock doesn't go negative

    def __str__(self):
        return f"{self.title}, Rs.{self.price}, Stock: {self.stock_quantity}"

# User class
class User:
    def __init__(self, first_name, last_name, username, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.user_data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "password": self.password  # Store the hashed password
        }
        self.cart = Cart()
        self.purchase_history = [] # Initialize purchase history

    def add_purchase_history(self, purchase_record):
        self.purchase_history.append(purchase_record)

    def view_purchase_history(self,file_manager):
        user_history = file_manager.load_purchase_history(self.username)  # Load purchase history for the current user
        if user_history:
            for purchase in user_history:
                print(f"-------------------------------\nDate: {purchase['date']}, Total Bill: Rs.{purchase['total_bill']}")
                for item in purchase["items"]:
                    print(f"{item['title']} - Rs.{item['price']} x {item['quantity']}")
                print(f"Shipping Address: {purchase['address']}")
        else:
            print("\n-------------------------------")
            print_red("User has no Previous Shopping History\n")
            
# Customer class (inherits from User)
class Customer(User):
    def __init__(self, first_name, last_name, username, password):
        super().__init__(first_name, last_name, username, password)

# Cart class
class Cart:
    def __init__(self):
        self.items = []

    def add_to_cart(self, product, quantity):
        if product.stock_quantity >= quantity:
            self.items.append({"title": product.title, "price": product.price, "quantity": quantity})
            product.update_stock(-quantity)
            print_green(f"Added {quantity} Quantity of {product.title} to the cart.\n")
        else:
            print_red(f"Insufficient stock for {product.title}. Available quantity: {product.stock_quantity}")
            print("-------------------------------")

    def remove_from_cart(self, product_title, quantity):
        for item in self.items[:]:
            if item["title"].lower() == product_title.lower():
                if quantity <= item["quantity"]:
                    item["quantity"] -= quantity
                    if item["quantity"] == 0:
                        self.items.remove(item)
                    print_green(f"Removed {quantity} Quantity of {product_title} from the cart.\n")
                    return quantity  # Return the quantity removed
                else:
                    print_red(f"Quantity {quantity} exceeds the available quantity in the cart for {product_title}.")
                    return 0  # Indicate no items were removed
        print_red(f"{product_title} not found in the cart.\n")
        return 0  # Indicate no items were removed

    def view_cart(self):
        if self.items:
            total_price = sum(item["price"] * item["quantity"] for item in self.items)
            for item in self.items:
                print(f"{item['title']} - Rs.{item['price']} x {item['quantity']}")
            print(f"Total Price: Rs.{total_price}\n")
        else:
            print_red("Your cart is empty.")
            print("-------------------------------")

# FileManagement class
class FileManagement:
    def __init__(self):
        self.create_database_folder()  # Ensure database folder exists

    def create_database_folder(self):
        try:
            os.mkdir('database')  # Create the database folder if it doesn't exist
        except FileExistsError:
            pass

    def save_users_data(self, users):
        self.create_database_folder()  # Ensure the database folder exists
        users_filename = "database/users_data.txt"
        with open(users_filename, 'w') as f:
            for user in users:
                f.write(f"{user.user_data}\n")  # Write the user_data dictionary

    def load_users_data(self):
        self.create_database_folder()  # Ensure the database folder exists
        users_filename = "database/users_data.txt"
        if os.path.exists(users_filename):
            with open(users_filename, 'r') as f:
                data = f.readlines()
            users = []
            for line in data:
                user_data = eval(line.strip())  # Convert the string representation back to a dictionary
                # Create a new User object using the user_data dictionary
                user = User(user_data["first_name"], user_data["last_name"], user_data["username"], user_data["password"])
                users.append(user)
            return users
        return []

    def save_purchase_history(self, username, purchase_record):
        self.create_database_folder()  # Ensure the database folder exists
        filename = f"database/{username}_purchase_history.txt"
        with open(filename, 'a') as f:
            f.write(f"{purchase_record}\n")

    def load_purchase_history(self, username):
        self.create_database_folder()  # Ensure the database folder exists
        filename = f"database/{username}_purchase_history.txt"
        try:
            with open(filename, 'r') as f:
                data = f.readlines()
            return [eval(line) for line in data if line.strip()]
        except FileNotFoundError:
            return []

# StoreOperations class (inherits from FileManagement)
class StoreOperations(FileManagement):
    def __init__(self,store_name):
        super().__init__()
        self.products = []  # Initialize an empty list for products
        self.users = self.load_users_data()  # Load data from file
        self.store_name=store_name

    def add_product(self, title, price, stock_quantity):
        self.products.append(Product(title, price, stock_quantity))

    def update_stock(self, product_title, quantity):
        for product in self.products:
            if product.title.lower() == product_title.lower():
                product.update_stock(quantity)
                print(f"Updated stock for {product_title}. New quantity: {product.stock_quantity}")
                return
        raise ProductNotAvailableException(product_title)

    def display_products(self):
        if self.products:
            for i, product in enumerate(self.products, 1):
                print(f"{i}. ", end="")
                product.display()
        else:
            print_red("No products available.\n-------------------------------")

    def feedback_form(self):
        try:
            while True:
                feedback = input("Would you like to give feedback on our Services(yes/no)?: ").lower()
                if feedback == 'yes':
                    print('Please Provide us with Your Valuable feedback to help us improve our services')
                    feedback_form = input("Give your Feedback here: ")
                    if feedback_form.strip():
                        print_green(f"Thank you for your feedback: {feedback_form}\n")
                        break
                    else:
                        print_red("Feedback cannot be empty. Please provide your valuable feedback.")
                        print("-------------------------------")
                elif feedback == 'no':
                    break
                else:
                    print_red("Invalid input. Please answer 'yes' or 'no'")
                    print("-------------------------------")
        except ValueError as ve:
            print_red(f'Invalid Input.\n{ve}')
            print('-------------------------------')

    def Payment_plan(self):
        while True:
            try:
                payment = input('\nWhich type of payment would you like to proceed with:\n\t1. Cash-On-Delivery\n\t2. Card\nEnter your response here: ').lower().strip()
                if payment == '1' or payment == 'cash-on-delivery' or payment == 'cod':
                    print_green('\nYou Have Selected Cash-On Delivery.\nRider will collect the Payment at your Doorstep\nYour Order will be delivered to you in 4-5 working days')
                    break
                elif payment == '2' or payment == 'card':
                    card = input("Enter Your Card Details: ")
                    if card.strip():  # Checks if card details are not empty after stripping whitespace
                        print_green("Processing payment with card details:", card, '\nYour Order will be delivered to you in 4-5 working days\n-------------------------------')
                        break
                    else:
                        raise ValueError("Card details cannot be empty.")
                else:
                    raise ValueError("Invalid payment type. Please choose '1' for Cash-On-Delivery or '2' for Card.")
            except ValueError as ve:
                print_red(f'Invalid Input.\n{ve}')
                print('-------------------------------')

    def checkout(self, address, user):
        if user.cart.items:
            total_price = sum(item["price"] * item["quantity"] for item in user.cart.items)
            date = datetime.now().strftime("%d-%m-%Y \t%H:%M:%S")
            purchase_record = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date": date,
                "items": user.cart.items,
                "total_bill": total_price,
                "address": address
            }
            user.add_purchase_history(purchase_record)  # Add to user's purchase history
            self.save_purchase_history(user.username, purchase_record)  # Save users purchase history to file
            user.cart.items = []  # Clear cart after checkout
            self.Payment_plan()
            print_green("Checkout successful! Your order will be delivered in 4-5 working days. Thank you!\n")
            self.feedback_form()
        else:
            print_red("Your cart is empty. Nothing to checkout.\n")

# UserOperations class (inherits from FileManagement)
class UserOperations(FileManagement):
    def __init__(self):
        super().__init__()
        self.users = self.load_users_data()

    def create_account(self):
        while True:
            try:
                first_name = input("Enter your first name: ").strip()
                last_name = input("Enter your last name: ").strip()
                username = input("Enter your username: ").strip()

                if not first_name or not last_name or not username:
                    raise ValueError("First-Name, Last-Name, and Username cannot be empty.")

                if not (first_name.isalpha() and last_name.isalpha()):
                    raise ValueError("First-Name and Last-Name must contain only alphabets.")

                if any(user.username == username for user in self.users):
                    print_red("Username already exists. Please choose a different username.")
                    continue
                password = input("Enter a unique password: ")
                confirm_password = input("Confirm your password: ")
                if password != confirm_password or len(password) < 8:
                    print_red("Passwords do not match or Password does not meet criteria (must be at least 8 characters long). Please try again.")
                    continue
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                new_user = User(first_name, last_name, username, hashed_password)
                self.users.append(new_user)
                self.save_users_data(self.users)  # Save user data after creation
                print_green("Account created successfully!\n")
                break
            except Exception as e:
                print_red(f"Invalid Input.\n{e}")

    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
        for user in self.users:
            if user.username == username and user.password == password:
                print_green(f"\nWelcome {user.first_name} {user.last_name}!")
                user.purchase_history = self.load_purchase_history(user.username)  # Load purchase history
                return user
        print_red("\nInvalid username or password.")
        return None

# Operator overloading
class LibrarySystem:
    def __init__(self, store_operations):
        self.store_operations = store_operations

    def __len__(self):
        return len(self.store_operations.products)

    def __str__(self):
        return f"Product Library of {self.store_operations.store_name}"

# Exception handling
class LibraryException(Exception):
    pass

class ProductNotAvailableException(LibraryException):
    def __init__(self, title):
        super().__init__(f"The product '{title}' is not available in the catalog.")

##for Error Msgs
def print_red(text):
    print(f"\033[91m{text}\033[0m")

#for successfull text
def print_green(text):
    print("\033[32m" + text + "\033[0m")

# Main program
if __name__ == "__main__":
    store_name = "Super Store"  # Define your store name
    store = StoreOperations(store_name)  # Initialize StoreOperations with store name
    user_ops = UserOperations()
    # Initialize LibrarySystem with StoreOperations
    library_system = LibrarySystem(store)
    file_manager=FileManagement()
    # Adding products to the store
    product_list = [
        {"title": "Hoodie", "price": 9999, "stock_quantity": 10},
        {"title": "T-shirt", "price": 4499, "stock_quantity": 20},
        {"title": "Pendant-chain", "price": 7499, "stock_quantity": 15},
        {"title": "Bandana", "price": 2499, "stock_quantity": 25},
        {"title": "Cap", "price": 1499, "stock_quantity": 12},
        {"title": "Rings", "price": 3499, "stock_quantity": 30},
        {"title": "Earrings", "price": 1099, "stock_quantity": 35},
        {"title": "Gucci-Belt", "price": 14499, "stock_quantity": 7},
        {"title": "Leather-Jacket", "price": 14999, "stock_quantity": 5},
        {"title": "Ripped-Jeans", "price": 4999, "stock_quantity": 6}
    ]
    for product in product_list:
        store.add_product(**product)

    # Welcome message
    print('.................................................................')
    print('Welcome to the Super Store, the Store of Ultimate Drip!! ')
    print("Greetings! How may I assist you today?")
    print("We offer a wide range of products and services to meet your needs.")

    while True:
        print("-------------------------------\n• Welcome Page:\n")
        print("1. Login")
        print("2. Create Account")
        print("3. Exit")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            logged_in_user = user_ops.login()
            if logged_in_user:
                while True:
                    print("-------------------------------\n• Logged-in Home-Page:\n")
                    print("1. View Products")
                    print("2. Add to Cart")
                    print("3. View Cart")
                    print("4. Remove from Cart")
                    print("5. Checkout")
                    print("6. View Purchase History")
                    print("7. Logout\n")
                    logged_in_choice = input("Enter your choice: ")

                    if logged_in_choice == "1":
                        try:
                            print(f"-------------------------------\n\t•{library_system}:\n")
                            store.display_products()
                        except Exception as e:
                            print(e)
                    elif logged_in_choice == "2":
                        print(f"-------------------------------\n\t•{library_system}:\n")
                        store.display_products()
                        if store.products:
                            try:
                                product_index = input("\nEnter the product index to add to cart: ")
                                if not product_index.isdigit():
                                    raise ValueError("Invalid Input.\nPlease enter an Integer Value")
                                product_index=int(product_index)
                                if 1 <= product_index <= len(store.products):
                                    selected_product = store.products[product_index - 1]
                                    quantity = input(f"Enter quantity for '{selected_product.title}': ")
                                    if not quantity.isdigit():
                                        raise ValueError("Invalid Input.\nPlease enter an Integer Value")
                                    quantity=int(quantity)
                                    logged_in_user.cart.add_to_cart(selected_product, quantity)
                                else:
                                    print_red("Invalid product index.")
                            except ValueError as e:
                                print_red(e)
                        else:
                            print_red("No products available.")

                    elif logged_in_choice == "3":
                        print("-------------------------------\nCurrent Cart Info:\t",datetime.now().strftime("%d %B,%Y\t%H:%M:%S"),'\n')
                        logged_in_user.cart.view_cart()

                    elif logged_in_choice == "4":
                        print("-------------------------------\nCurrent Cart Info:\t",datetime.now().strftime("%d %B,%Y\t%H:%M:%S"),'\n')
                        logged_in_user.cart.view_cart()
                        if logged_in_user.cart.items:
                            product_title = input("Enter the product title to remove from cart: ")
                            try:
                                quantity = input(f"Enter quantity to remove for '{product_title}': ")
                                if not quantity.isdigit():
                                    raise ValueError("Invalid Input.\nEnter An Integeric Value")
                                quantity=int(quantity)
                                removed_quantity=logged_in_user.cart.remove_from_cart(product_title, quantity)
                                if removed_quantity>0:
                                    #Update Store Product stock
                                    for product in store.products:
                                        if product.title.lower() == product_title.lower():
                                            product.update_stock(removed_quantity)
                                            break           
                            except ValueError as ve:
                                print_red(ve)  
                        else:
                            print_red("Add Products to remove from Cart")
                    elif logged_in_choice == "5":
                        while True:
                            try:
                                if logged_in_user.cart.items:
                                    residence = str(input("-------------------------------\nPlease enter your address of residence: "))
                                    famous_location = str(input("Enter a famous location near your area of residence: "))
                                    city = str(input("Enter your city where you reside: "))
                                    state = str(input("Enter your state: "))
                                    ###Check if even one field is empty:
                                    if not residence or not famous_location or not city or not state:
                                        raise ValueError("All address fields are required. Please enter each part of the Address correctly.")
                                    address = f"{residence}, {famous_location}, {city}, {state}"
                                    store.checkout(address, logged_in_user)
                                    break  # Exit the loop after successful checkout
                                print_red("Your cart is empty. Nothing to checkout.")
                                print("\n-------------------------------")
                                break
                            except ValueError as ve:
                                print_red(f'Invalid Input.\n{ve}')

                    elif logged_in_choice == "6":
                        logged_in_user.view_purchase_history(file_manager)

                    elif logged_in_choice == "7":
                        print("-------------------------------")
                        print_green(f"Logged out successfully.\nThank you for visiting our store.\nHave a nice day, {logged_in_user.username}!")
                        print(".................................................................")
                        exit()

                    else:
                        print_red("Invalid choice. Please enter a valid option.")

        elif choice == "2":
            user_ops.create_account()

        elif choice == "3":
            print_green("Thank you for visiting our store. Goodbye!")
            print(".................................................................")
            break

        else:
            print_red("Invalid choice. Please enter a valid option.")
