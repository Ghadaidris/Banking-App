import csv
import os
from datetime import datetime  ## for transaction timestamps

# the classes

class Account:
    def __init__(self, balance=0, active=True, overdraft_count=0):
        self.balance = float(balance)
        self.active = active
        self.overdraft_count = int(overdraft_count)  ## keep track of overdrafts per account

class CheckingAccount(Account):
    pass  ## checking account class, inherits from Account

class SavingsAccount(Account):
    pass  ## savings account class, inherits from Account

class Customer:
    def __init__(self, id, first_name, last_name, password, checking, savings, active, overdraft_count):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        ## we pass the objects to the classes
        self.checking = CheckingAccount(checking, active, overdraft_count)
        self.savings = SavingsAccount(savings, active, overdraft_count)


def parse_balance(value):  ## this function makes sure empty or false values become 0
    if value is None:
        return 0.0
    s = str(value).strip()  ## convert value to string and remove spaces
    if s.lower() == "false" or s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


# Load Customers from CSV

def load_customers(filename="bank.csv"):
    customers = {}  ## holds all our customers
    ## if the file doesn't exist, create it
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "first_name", "last_name", "password", "checking", "savings", "active", "overdraft_count"])
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
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


## save customers to csv

def save_customers(customers, filename="bank.csv"):
    fieldnames = ["id", "first_name", "last_name", "password", "checking", "savings", "active", "overdraft_count"]
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
                "active": str(custom.checking.active),
                "overdraft_count": custom.checking.overdraft_count
            })


## log transaction to CSV

def log_transaction(customer_id, transaction_type, amount, account_type, target_id=None):
    ## create transactions.csv if it doesn't exist
    filename = "transactions.csv"
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="") as f:
        fieldnames = ["timestamp", "customer_id", "type", "amount", "account", "target_id"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": customer_id,
            "type": transaction_type,
            "amount": amount,
            "account": account_type,
            "target_id": target_id or ""
        })


## create new account

def create_account(customers):
    print("--- Create New Account ---")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")

    ## generate new ID
    if customers:
        new_id = max(int(cid) for cid in customers.keys()) + 1
    else:
        new_id = 10001

    ## ask which accounts to open
    open_checking = input("Do you want to open a Checking Account? (y/n): ").lower()
    checking = 0.0
    checking_active = True if open_checking == "y" else False

    open_savings = input("Do you want to open a Savings Account? (y/n): ").lower()
    savings = 0.0
    savings_active = True if open_savings == "y" else False

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

    new_customer.checking.active = checking_active
    new_customer.savings.active = savings_active

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
    while True:
        acct = input("Deposit to (checking/savings): ").strip().lower()
        if acct in ("checking", "savings"):
            break
        print("Please type 'checking' or 'savings'.")

    amount_str = input("Amount to deposit: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    if acct == "checking":
        customer.checking.balance += amount
    else:
        customer.savings.balance += amount

    print(f"Deposited {amount:.2f} to your {acct}.")
    print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")

    save_customers(customers, filename)
    log_transaction(customer.id, "deposit", amount, acct)  ## log deposit


# withdraw function

def withdraw(customer, customers, filename="bank.csv"):
    print("--- Withdraw ---")
    while True:
        acct = input("Withdraw from (checking/savings): ").strip().lower()
        if acct in ("checking", "savings"):
            break
        print("Please type 'checking' or 'savings'.")

    amount_str = input("Amount to withdraw: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    account = customer.checking if acct == "checking" else customer.savings

    if account.balance < 0 and amount > 100:
        print("Cannot withdraw more than $100 when account balance is negative.")
        return
    if amount > 100:
        print("Cannot withdraw more than $100 in one transaction.")
        return

    account.balance -= amount

    if account.balance < 0:
        account.overdraft_count += 1
        account.balance -= 35
        print(f"Overdraft! You are charged $35. New balance: {account.balance:.2f}")
        if account.overdraft_count > 2:
            account.active = False
            print(f"Your {acct} account has been deactivated due to multiple overdrafts.")
    else:
        print(f"Withdrawn {amount:.2f} from your {acct}. New balance: {account.balance:.2f}")

    save_customers(customers, filename)
    log_transaction(customer.id, "withdraw", amount, acct)  ## log withdraw


# transfer function

def transfer(customer, customers, filename="bank.csv"):
    print("--- Transfer Money ---")
    while True:
        transfer_type = input("Transfer to (checking/savings/another customer): ").strip().lower()
        if transfer_type in ("checking", "savings", "another customer"):
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

    ## transfer between own accounts
    if transfer_type in ("checking", "savings"):
        from_account = customer.savings if transfer_type == "checking" else customer.checking
        to_account = customer.checking if transfer_type == "checking" else customer.savings

        if from_account.balance < 0 and amount > 100:
            print("Cannot transfer more than $100 when account balance is negative.")
            return
        if amount > 100:
            print("Cannot transfer more than $100 in one transaction.")
            return

        from_account.balance -= amount
        to_account.balance += amount

        if from_account.balance < 0:
            from_account.overdraft_count += 1
            from_account.balance -= 35
            print(f"Overdraft! You are charged $35. New balance: {from_account.balance:.2f}")
            if from_account.overdraft_count > 2:
                from_account.active = False
                print(f"Your {('savings' if transfer_type=='checking' else 'checking')} account has been deactivated due to multiple overdrafts.")

        print(f"Transferred {amount:.2f} from {('savings' if transfer_type == 'checking' else 'checking')} to {transfer_type}.")
        print(f"New balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")
        log_transaction(customer.id, "transfer", amount, transfer_type)  ## log transfer

    ## transfer to another customer
    else:
        target_id = input("Enter the ID of the customer to transfer to: ").strip()
        if target_id not in customers:
            print("Customer ID not found.")
            return

        target_customer = customers[target_id]

        from_account_choice = input("Withdraw from (checking/savings): ").strip().lower()
        if from_account_choice not in ("checking", "savings"):
            print("Invalid choice.")
            return

        from_account = customer.checking if from_account_choice == "checking" else customer.savings

        if from_account.balance < 0 and amount > 100:
            print("Cannot transfer more than $100 when account balance is negative.")
            return
        if amount > 100:
            print("Cannot transfer more than $100 in one transaction.")
            return

        from_account.balance -= amount
        to_account_choice = input(f"Deposit to target's account (checking/savings): ").strip().lower()
        if to_account_choice not in ("checking", "savings"):
            print("Invalid choice.")
            return

        to_account = target_customer.checking if to_account_choice == "checking" else target_customer.savings
        to_account.balance += amount

        if from_account.balance < 0:
            from_account.overdraft_count += 1
            from_account.balance -= 35
            print(f"Overdraft! You are charged $35. New balance: {from_account.balance:.2f}")
            if from_account.overdraft_count > 2:
                from_account.active = False
                print(f"Your {from_account_choice} account has been deactivated due to multiple overdrafts.")

        print(f"Transferred {amount:.2f} from your {from_account_choice} to {target_customer.first_name}'s {to_account_choice}.")
        print(f"Your balances => Checking: {customer.checking.balance:.2f}, Savings: {customer.savings.balance:.2f}")
        log_transaction(customer.id, "transfer_to_customer", amount, from_account_choice, target_id)  ## log transfer to other customer

    save_customers(customers, filename)


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
            print(f"Checking: {customer.checking.balance}, Savings: {customer.savings.balance}")
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
            print("Please choose from the menu above")


# main program

def main():
    customers = load_customers()
    user = login(customers)
    main_menu(user, customers)


if __name__ == "__main__":
    main()
