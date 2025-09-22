import csv
import os ## to make sure the file is found in the OS


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
        # we pass the objects to the classes
        self.checking = CheckingAccount(checking, active, overdraft_count)
        self.savings = SavingsAccount(savings, active, overdraft_count)





def parse_balance(value):## this function to make sure that values like faluse and empty str are put to zeros
 
    if value is None:
        return 0.0
    s = str(value).strip()
    if s.lower() == "false" or s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0



# Load Customers from CSV

def load_customers(filename="bank.csv"):
    customers = {}
    ## if the file doesnt exists make the file 
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id","first_name","last_name","password","checking","savings","active","overdraft_count"])
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)## we read the csv file using this dictreader 
        for row in reader:
            id = row["id"]
            checking = parse_balance(row.get("checking"))
            savings = parse_balance(row.get("savings"))
            active = True if str(row.get("active")).strip().lower() == "true" else False
            overdraft_count = int(row.get("overdraft_count") or 0)
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



# Save Customers to CSV

def save_customers(customers, filename="bank.csv"):
   
    fieldnames = ["id","first_name","last_name","password","checking","savings","active","overdraft_count"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames) ## using the dictwriter to write the changes made to the csv file 
        writer.writeheader()
        for custom in customers.values():
            writer.writerow({
                "id": custom.id,
                "first_name": custom.first_name,
                "last_name": custom.last_name,
                "password": custom.password,
                # wrttien as zeros 
                "checking": custom.checking.balance,
                "savings": custom.savings.balance,
                #as a true or false
                "active": str(custom.checking.active),
                "overdraft_count": custom.checking.overdraft_count ## as a zero 
            })



# Create New Account

def create_account(customers, filename="bank.csv"):
    print("\n--- Create New Account ---")
    while True:
        new_id = input("Enter Your ID: ").strip()
        if new_id in customers:
            print("ID already exists. log in to your account.")
        else:
            break
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    password = input("Password: ").strip()
    #initilize the variabls w zeros 
    checking = 0
    savings = 0
    active = True
    overdraft_count = 0
    new_customer = Customer(new_id, first_name, last_name, password, checking, savings, active, overdraft_count)
    customers[new_id] = new_customer
    ## call this function to write the new customers in the csv file 
    save_customers(customers, filename)
    print(f"Account for {first_name} {last_name} created successfully!")
    return new_customer



# Login Function

def login(customers):
    print("Welcome to Ghada Bank!")
    while True:
        choice = input("Do you have an account? (yes/no): ").lower().strip()
        if choice == "yes":
            user_id = input("Enter your ID: ").strip()
            password = input("Enter your password: ").strip()
            if user_id in customers and customers[user_id].password == password:
                print(f"Welcome, {customers[user_id].first_name}!")
                return customers[user_id]
            else:
                print("Invalid ID or password. Try again.")
        elif choice == "no":
            create_choice = input("Do you want to create a new account? (yes/no): ").lower().strip()
            if create_choice == "yes":
                return create_account(customers)
            else:
                print("Okay, maybe next time.")
                exit()
        else:
            print("Please answer 'yes' or 'no'.")



# Deposit Function 

def deposit(customer, customers, filename="bank.csv"):
    
    print("\n--- Deposit ---")
    
    while True:## keep the loop till the input is correct 
        acct = input("Deposit to (checking/savings): ").strip().lower() ##acct short for account , used strip n lower to insure clean input 
        if acct in ("checking", "savings"):
            break
        print("Please type 'checking' or 'savings'.")

   ## the amount that the user want to deposit 
    amount_str = input("Amount to deposit: ").strip()
    try:
        amount = float(amount_str) ##change the str to float 
    except ValueError: ##if input value isnt accepted 
        print("Invalid amount. Please enter a number.")
        return  ## exit if the input isnt valid 

    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    #add the correct amount to the chosen account 
    if acct == "checking":
        customer.checking.balance += amount
    else:
        customer.savings.balance += amount

    #print to insure the user that the process is done 
    print(f"✅ Deposited {amount:.2f} to your {acct}.")
    print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")

    ## saving the changes again
    save_customers(customers, filename)

# Main Menu

def main_menu(customer, customers):
    while True:
        print("\nMain Menu")
        print("1. View Balances")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Logout")
        choice = input("Select an option: ").strip()
        if choice == "1":
            print(f"Checking: {customer.checking.balance}, Savings: {customer.savings.balance}") ## print the customer balance 
        elif choice == "2":
            deposit(customer, customers)  ## call the deposit function 
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Plaase choose from the menu above ")



# Main Program

def main():
    customers = load_customers()
    user = login(customers)
    main_menu(user, customers)

if __name__ == "__main__":
    main()
