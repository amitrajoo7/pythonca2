import csv
import bcrypt
import re
import requests

# Utility Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def email_validation(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def password_validation(password):
    if (len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[@$!%*#?&]', password)):
        return True
    return False

# Load users from CSV
def load_users():
    users = {}
    try:
        with open('users.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['email']] = {
                    'hashed_password': row['hashed_password'].encode('utf-8'),
                    'security_question': row['security_question'],
                    'security_answer': row['security_answer']
                }
    except FileNotFoundError:
        pass
    return users

# Save new user to CSV
def save_user(email, hashed_password, security_question, security_answer):
    with open('users.csv', mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['email', 'hashed_password', 'security_question', 'security_answer'])
        if file.tell() == 0:  # Write header if file is empty
            writer.writeheader()
        writer.writerow({
            'email': email,
            'hashed_password': hashed_password.decode('utf-8'),
            'security_question': security_question,
            'security_answer': security_answer
        })

# Registration
def register():
    email = input("Enter your email: ")
    if not email_validation(email):
        print("Invalid email format!")
        return
    password = input("Enter your password: ")
    if not password_validation(password):
        print("Password does not meet security requirements!")
        return
    hashed_password = hash_password(password)

    security_question = input("Enter your security question: ")
    security_answer = input("Enter your security answer: ")

    save_user(email, hashed_password, security_question, security_answer)
    print("Registration successful!")

# Login Process
def login():
    users = load_users()
    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        email = input("Enter your email: ")
        if not email_validation(email):
            print("Invalid email format!")
            continue
        
        password = input("Enter your password: ")
        if email in users and check_password(users[email]['hashed_password'], password):
            print("Login successful!")
            return True  # User logged in
        else:
            attempts += 1
            print(f"Incorrect email or password. {max_attempts - attempts} attempts remaining.")
    
    print("Maximum login attempts reached. Exiting...")
    return False

# Forgot Password Process
def forgot_password():
    users = load_users()
    email = input("Enter your registered email: ")
    
    if email in users:
        security_question = users[email]['security_question']
        security_answer = input(f"Security Question: {security_question}: ")
        
        if security_answer == users[email]['security_answer']:
            new_password = input("Enter new password: ")
            if password_validation(new_password):
                users[email]['hashed_password'] = hash_password(new_password)
                print("Password successfully reset!")
                # Save updated user information
                with open('users.csv', mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['email', 'hashed_password', 'security_question', 'security_answer'])
                    writer.writeheader()
                    for user_email, user_data in users.items():
                        writer.writerow({
                            'email': user_email,
                            'hashed_password': user_data['hashed_password'].decode('utf-8'),
                            'security_question': user_data['security_question'],
                            'security_answer': user_data['security_answer']
                        })
            else:
                print("Password does not meet security requirements.")
        else:
            print("Incorrect security answer.")
    else:
        print("Email not found.")

# CheapShark API Integration
def get_game_deals(game_title):
    url = f"https://www.cheapshark.com/api/1.0/deals?title={game_title}&limit=5"
    response = requests.get(url)
    
    if response.status_code == 200:
        deals = response.json()
        if deals:
            print(f"\nTop 5 deals for '{game_title}':")
            for deal in deals:
                print(f"\nGame: {deal['title']}")
                print(f"Store: {deal['storeID']}")
                print(f"Normal Price: {deal['normalPrice']}")
                print(f"Sale Price: {deal['salePrice']}")
                print(f"Savings: {deal['savings']}%")
                print(f"Deal Rating: {deal['dealRating']}")
                print(f"Store Link: https://www.cheapshark.com/redirect?dealID={deal['dealID']}")
        else:
            print("No deals found for this game.")
    else:
        print("Error fetching game deals.")

# Main Application Flow
def main():
    while True:
        print(f" 1 Do you want to  Login\n ""2 Register \n" " 3 Forgot Password" )
        choice = input("Enter your choice : ")
        if choice == "1":
            if login():
                game_title = input("Enter the game title to search for deals: ")
                get_game_deals(game_title)
                break
        elif choice == "2":
            register()
        elif choice == "3":
            forgot_password()
        else:
            print("Invalid choice, try again.")

# Run the application
if __name__ == "__main__":
    main()
