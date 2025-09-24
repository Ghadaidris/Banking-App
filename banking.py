import csv
import os ## to make sure the file is found in the OS


#the classes

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
    s = str(value).strip() ##transfer the value to str n make sure its w/o any spaces 
    if s.lower() == "false" or s == "":## if the str is false or empty return 0.0
        return 0.0
    try:
        return float(s) ## transfer the str to float if fails return 0.0
    except ValueError:
        return 0.0



# Load Customers from CSV

def load_customers(filename="bank.csv"):
    customers = {}## holds all our customers 
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



##save customers to csv

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



##create new account

def create_account(customers):
    print("--- Create New Account ---")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")

    # generate new ID
    if customers:
        new_id = max(int(cid) for cid in customers.keys()) + 1
    else:
        new_id = 10001  # first ID if file is empty

    # initialize checking and savings
    open_checking = input("Do you want to open a Checking Account? (y/n): ").lower()
    if open_checking == "y":
        checking = 0.0
        checking_active = True
    else:
        checking = 0.0
        checking_active = False

    open_savings = input("Do you want to open a Savings Account? (y/n): ").lower()
    if open_savings == "y":
        savings = 0.0
        savings_active = True
    else:
        savings = 0.0
        savings_active = False

    # create new customer
    new_customer = Customer(
        id=new_id,
        first_name=first_name,
        last_name=last_name,
        password=password,
        checking=checking,
        savings=savings,
        active=True,
        overdraft_count=0
    )

    # set account activeness
    new_customer.checking.active = checking_active
    new_customer.savings.active = savings_active

    # add to dictionary and save
    customers[str(new_id)] = new_customer
    save_customers(customers)

    

    print(f"Account for {first_name} {last_name} created successfully! Your ID is {new_id}")
    return new_customer


# login function

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



# deposit function 

def deposit(customer, customers, filename="bank.csv"):
    
    print("--- Deposit ---")
    
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
    print(f"Deposited {amount:.2f} to your {acct}.")
    print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}") ## used .2f to print float number 

    ## saving the changes again
    save_customers(customers, filename)

# main menu

def main_menu(customer, customers): ## customer is the class for one customers , customers is the dictionary that holds all our customers 
    while True:
        print("Main Menu")
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



# main program

def main():
    customers = load_customers()
    user = login(customers)
    main_menu(user, customers)

if __name__ == "__main__":
    main()
