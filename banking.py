import csv
import os



# base account class
class Account:
    def __init__(self, balance=0, active=True):
        self.balance = float(balance)  # current balance
        self.active = active  # is the account active

# checking account inherits from Account
class CheckingAccount(Account):
    pass

# savings account inherits from Account
class SavingsAccount(Account):
    pass

# customer class
class Customer:
    def __init__(self, id, first_name, last_name, password, checking, savings, active):
        self.id = id  # customer id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password  # login password
        self.checking = CheckingAccount(checking, active)  # checking account
        self.savings = SavingsAccount(savings, active)  # savings account



# safely parse balance value from CSV
def parse_balance(value):
    if value is None:
        return 0.0
    s = str(value).strip()
    if s.lower() == "false" or s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

# load all customers from CSV file
def load_customers(filename="bank.csv"):
    customers = {}
    if not os.path.exists(filename):
        # create CSV file with header if doesn't exist
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id","first_name","last_name","password","checking","savings","active"])
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row["id"]
            checking = parse_balance(row.get("checking"))
            savings = parse_balance(row.get("savings"))
            active = True if str(row.get("active")).strip().lower() == "true" else False
            # create Customer object
            customers[id] = Customer(
                id,
                row["first_name"],
                row["last_name"],
                row["password"],
                checking,
                savings,
                active
            )
    return customers

# save all customers back to CSV
def save_customers(customers, filename="bank.csv"):
    fieldnames = ["id","first_name","last_name","password","checking","savings","active"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for custom in customers.values():
            writer.writerow({
                "id": custom.id,
                "first_name": custom.first_name,
                "last_name": custom.last_name,
                "password": custom.password,
                "checking": custom.checking.balance,
                "savings": custom.savings.balance,
                "active": str(custom.checking.active)
            })



# create new account
def create_account(customers):
    print("--- Create New Account ---")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")

    # generate new unique ID
    if customers:
        new_id = max(int(cid) for cid in customers.keys()) + 1
    else:
        new_id = 10001

    # ask which accounts to open
    open_checking = input("Do you want to open a Checking Account? (y/n): ").lower()
    checking_active = open_checking == "y"
    checking = 0.0

    open_savings = input("Do you want to open a Savings Account? (y/n): ").lower()
    savings_active = open_savings == "y"
    savings = 0.0

    # create customer object
    new_customer = Customer(
        id=new_id,
        first_name=first_name,
        last_name=last_name,
        password=password,
        checking=checking,
        savings=savings,
        active=True
    )
    # set account status
    new_customer.checking.active = checking_active
    new_customer.savings.active = savings_active

    # add customer to dictionary
    customers[str(new_id)] = new_customer
    save_customers(customers)
    print(f"Account for {first_name} {last_name} created successfully! Your ID is {new_id}")
    return new_customer

# login function
def login(customers):
    print("Welcome to Kabsa Bank!")
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

# deposit money
def deposit(customer, customers):
    print("--- Deposit ---")
    if not customer.checking.active and not customer.savings.active:
        print("All your accounts are inactive. Cannot deposit.")
        return
    while True:
        acct = input("Deposit to (checking/savings): ").strip().lower()
        if acct in ("checking", "savings"):
            break
        print("Please type 'checking' or 'savings'.")
    account = customer.checking if acct=="checking" else customer.savings
    if not account.active:
        print(f"{acct.capitalize()} account is inactive. Cannot deposit.")
        return
    amount_str = input("Amount to deposit: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return
    if amount <= 0:
        print("Amount must be greater than 0.")
        return
    account.balance += amount
    print(f"Deposited {amount:.2f} to your {acct}.")
    print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")
    save_customers(customers)

# withdraw money with overdraft
def withdraw(customer, customers):
    print("--- Withdraw ---")
    if not customer.checking.active and not customer.savings.active:
        print("All your accounts are inactive. Cannot withdraw.")
        return
    while True:
        acct = input("Withdraw from (checking/savings): ").strip().lower()
        if acct in ("checking", "savings"):
            break
        print("Please type 'checking' or 'savings'.")
    account = customer.checking if acct=="checking" else customer.savings
    if not account.active:
        print(f"{acct.capitalize()} account is inactive. Cannot withdraw.")
        return
    amount_str = input("Amount to withdraw: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return
    if amount <= 0:
        print("Amount must be greater than 0.")
        return
    account.balance -= amount
    # check overdraft for this account only
    if account.balance < 0:
        account.balance -= 35  # overdraft fee
        print(f"Overdraft! You are charged $35. New balance: {account.balance:.2f}")
    else:
        print(f"Withdrawn {amount:.2f} from your {acct}. New balance: {account.balance:.2f}")
    save_customers(customers)

# transfer money with overdraft
def transfer(customer, customers):
    print("--- Transfer Money ---")
    if not customer.checking.active and not customer.savings.active:
        print("All your accounts are inactive. Cannot transfer.")
        return
    while True:
        dest = input("Transfer to (checking/savings/another customer): ").strip().lower()
        if dest in ("checking", "savings", "another customer"):
            break
        print("Please type 'checking', 'savings', or 'another customer'.")
    
    amount_str = input("Amount to transfer: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return
    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    if dest in ("checking", "savings"):
        # internal transfer
        from_account = customer.savings if dest=="checking" else customer.checking
        to_account = customer.checking if dest=="checking" else customer.savings
        if not from_account.active or not to_account.active:
            print(f"Cannot transfer. One of the accounts is inactive.")
            return
        from_account.balance -= amount
        if from_account.balance < 0:
            from_account.balance -= 35  # overdraft fee
            print(f"Overdraft! You are charged $35. New balance: {from_account.balance:.2f}")
        to_account.balance += amount
        print(f"Transferred {amount:.2f} between your accounts.")
        print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")
        save_customers(customers)
    else:
        # transfer to another customer
        target_id = input("Enter the ID of the customer to transfer to: ").strip()
        if target_id not in customers:
            print("Target customer not found.")
            return
        target = customers[target_id]
        while True:
            from_acc = input("Withdraw from (checking/savings): ").strip().lower()
            if from_acc in ("checking", "savings"):
                break
        from_account = customer.checking if from_acc=="checking" else customer.savings
        if not from_account.active:
            print(f"Your {from_acc} account is inactive. Cannot transfer.")
            return
        from_account.balance -= amount
        if from_account.balance < 0:
            from_account.balance -= 35  # overdraft
            print(f"Overdraft! You are charged $35. New balance: {from_account.balance:.2f}")
        while True:
            to_acc = input("Deposit to target's account (checking/savings): ").strip().lower()
            if to_acc in ("checking","savings"):
                break
        to_account = target.checking if to_acc=="checking" else target.savings
        if not to_account.active:
            print(f"Target's {to_acc} account is inactive. Cannot deposit.")
            return
        to_account.balance += amount
        print(f"Transferred {amount:.2f} from your {from_acc} to {target.first_name}'s {to_acc}.")
        print(f"Your balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")
        save_customers(customers)

# view balances
def view_balances(customer):
    print(f"Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")

# main menu
def main_menu(customer, customers):
    while True:
        print("Main Menu")
        print("1. View Balances")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Logout")
        choice = input("Select an option: ").strip()
        if choice == "1":
            view_balances(customer)
        elif choice == "2":
            deposit(customer, customers)
        elif choice == "3":
            withdraw(customer, customers)
        elif choice == "4":
            transfer(customer, customers)
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Please choose from the menu above.")

# main function
def main():
    customers = load_customers()
    user = login(customers)
    main_menu(user, customers)

if __name__ == "__main__":
    main()
