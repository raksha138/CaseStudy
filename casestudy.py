import csv
import threading
import time

# a lock for thread safety
balance_lock = threading.Lock()

# Customer class 
class Customer:
    def __init__(self, customer_id, name, account_balance, account_type):
        self.customer_id = customer_id
        self.name = name
        self.account_balance = account_balance
        self.account_type = account_type
        self.transaction_history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        with balance_lock:
            self.account_balance += amount
            self.transaction_history.append(f"Deposited: Rs{amount}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        with balance_lock:
            if self.account_balance >= amount:
                self.account_balance -= amount
                self.transaction_history.append(f"Withdrew: Rs{amount}")
            else:
                raise ValueError("Insufficient balance.")

    def view_transaction_history(self):
        return self.transaction_history

    def apply_interest(self, interest_rate):
        if self.account_type.lower() == "savings":
            with balance_lock:
                interest = self.account_balance * (interest_rate / 100)
                self.account_balance += interest
                self.transaction_history.append(f"Interest applied: Rs{interest:.2f}")

# Function to read customer data from a file
def load_customers(file_path):
    customers = {}
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customer = Customer(
                    customer_id=int(row['CustomerID']),
                    name=row['Name'],
                    account_balance=float(row['AccountBalance']),
                    account_type="savings"  # Assuming all accounts are savings for this example
                )
                customers[customer.customer_id] = customer
    except FileNotFoundError:
        print("Error: Data file not found.")
    except Exception as e:
        print(f"Error: {e}")
    return customers

# Function to periodically apply interest
def periodic_interest_application(customers, interest_rate, interval):
    while True:
        for customer in customers.values():
            customer.apply_interest(interest_rate)
        time.sleep(interval)

# Main program
def main():
    file_path = 'Data.csv'
    customers = load_customers(file_path)

    if not customers:
        print("No customers loaded. Exiting.")
        return

    # Start a daemon thread for periodic interest application
    interest_thread = threading.Thread(
        target=periodic_interest_application, 
        args=(customers, 5, 10),  # Applying 5% interest every 10 seconds
        daemon=True
    )
    interest_thread.start()

    # Simulate user interaction
    while True:
        print("\n--- Banking System ---")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. View Transaction History")
        print("4. View Account Balance")
        print("5. Exit")

        try:
            choice = int(input("Enter your choice: "))

            if choice == 5:
                print("Exiting banking system. Goodbye!")
                break

            customer_id = int(input("Enter Customer ID: "))
            if customer_id not in customers:
                print("Invalid Customer ID.")
                continue

            customer = customers[customer_id]

            if choice == 1:
                amount = float(input("Enter deposit amount: Rs"))
                customer.deposit(amount)
                print("Deposit successful.")
            elif choice == 2:
                amount = float(input("Enter withdrawal amount: Rs"))
                customer.withdraw(amount)
                print("Withdrawal successful.")
            elif choice == 3:
                history = customer.view_transaction_history()
                print("Transaction History:")
                for record in history:
                    print(record)
            elif choice == 4:
                print(f"Account Balance: Rs{customer.account_balance:.2f}")
            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
