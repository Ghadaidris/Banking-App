import csv
import os ##يتاكد اذا الملف موجود بالنظام وعشان يشتغل بدون اي اخطاء


# Classes


class Account:
    def __init__(self, balance=0, active=True, overdraft_count=0):
        self.balance = float(balance)
        self.active = active
        self.overdraft_count = int(overdraft_count)

class CheckingAccount(Account):
    pass

class SavingsAccount(Account):
    pass

class Customer:
    def __init__(self, id, first_name, last_name, password, checking, savings, active, overdraft_count):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.checking = CheckingAccount(checking, active, overdraft_count)
        self.savings = SavingsAccount(savings, active, overdraft_count)


# Load Customers from CSV

def load_customers(filename="bank.csv"):
    customers = {}
    if not os.path.exists(filename):
        # إذا الملف غير موجود، نعمله ونعطيه رؤوس الأعمدة
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id","first_name","last_name","password","checking","savings","active","overdraft_count"])
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row["id"]
            checking = float(row["checking"]) if row["checking"] not in ["False", "False"] else 0
            savings = float(row["savings"]) if row["savings"] not in ["False", "False"] else 0
            active = True if row["active"] == "True" else False
            overdraft_count = int(row["overdraft_count"])
            customers[id] = Customer(
                id,
                row["first_name"],
                row["last_name"],
                row["password"],
                checking,
                savings,
                active,
                overdraft_count
            )
    return customers


# Create New Account

def create_account(customers, filename="bank.csv"):
    print("\n--- Create New Account ---")
    while True:
        new_id = input("Enter Your ID: ")
        if new_id in customers:
            print("ID already exists. log in to your account.")
        else:
            break
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")
    checking =0
    savings = 0
    active = True
    overdraft_count = 0
    # إنشاء كائن Customer جديد
    new_customer = Customer(new_id, first_name, last_name, password, checking, savings, active, overdraft_count)
    customers[new_id] = new_customer
    # إضافة البيانات لل CSV
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, first_name, last_name, password, checking, savings, active, overdraft_count])
    print(f"Account for {first_name} {last_name} created successfully!")
    return new_customer


# Login Function

def login(customers):
    print("Welcome to Ghada Bank!")
    while True:
        choice = input("Do you have an account? (yes/no): ").lower()
        if choice == "yes":
            user_id = input("Enter your ID: ")
            password = input("Enter your password: ")
            if user_id in customers and customers[user_id].password == password:
                print(f"Welcome, {customers[user_id].first_name}!")
                return customers[user_id]
            else:
                print("Invalid ID or password. Try again.")
        elif choice == "no":
            create_choice = input("Do you want to create a new account? (yes/no): ").lower()
            if create_choice == "yes":
                return create_account(customers)
            else:
                print("Okay, maybe next time.")
                exit()
        else:
            print("Please answer 'yes' or 'no'.")


# Main Menu

def main_menu(customer):
    while True:
        print("\nMain Menu")
        print("1. View Balances")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Logout")
        choice = input("Select an option: ")
        if choice == "1":
            print(f"Checking: {customer.checking.balance}, Savings: {customer.savings.balance}")
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("theres nothing yetyes" \
            "")


# Main Program

def main():
    customers = load_customers()
    user = login(customers)
    main_menu(user)

if __name__ == "__main__":
    main()
