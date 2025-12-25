import json
import os
import datetime

ACCOUNTS_FILE = "accounts.json"
TRANSACTIONS_FILE = "transactions.json"

def load_transactions():
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    with open(TRANSACTIONS_FILE, "r") as f:
        return json.load(f)

def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

def log_transaction(acno, trans_type, amount, related_acno=None):
    transactions = load_transactions()
    transaction = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acno": acno,
        "type": trans_type,
        "amount": amount,
        "related_acno": related_acno
    }
    transactions.append(transaction)
    save_transactions(transactions)

def get_account_transactions(acno):
    transactions = load_transactions()
    return [t for t in transactions if t["acno"] == acno]

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

class Account:
    def __init__(self, acno, name, acc_type, deposit):
        self.acno = acno
        self.name = name
        self.acc_type = acc_type.upper()
        self.deposit = deposit

    def to_dict(self):
        return {
            "acno": self.acno,
            "name": self.name,
            "type": self.acc_type,
            "deposit": self.deposit
        }

    @staticmethod
    def from_dict(data):
        return Account(data["acno"], data["name"], data["type"], data["deposit"])

    def deposit_amount(self, amount):
        self.deposit += amount
        log_transaction(self.acno, "DEPOSIT", amount)

    def withdraw_amount(self, amount):
        if self.acc_type == 'S' and self.deposit - amount < 500:
            return False
        if self.acc_type == 'C' and self.deposit - amount < 1000:
            return False
        self.deposit -= amount
        log_transaction(self.acno, "WITHDRAW", amount)
        return True

def transfer_funds(from_acno, to_acno, amount):
    accounts = load_accounts()
    from_acc_data = None
    to_acc_data = None
    
    for acc in accounts:
        if acc["acno"] == from_acno:
            from_acc_data = acc
        elif acc["acno"] == to_acno:
            to_acc_data = acc
            
    if not from_acc_data or not to_acc_data:
        return False, "One or both accounts not found"
        
    from_acc = Account.from_dict(from_acc_data)
    
    # Check balance logic directly on from_acc similar to withdraw
    if from_acc.acc_type == 'S' and from_acc.deposit - amount < 500:
        return False, "Insufficient balance (Min 500)"
    if from_acc.acc_type == 'C' and from_acc.deposit - amount < 1000:
        return False, "Insufficient balance (Min 1000)"
        
    # Perform Transfer
    from_acc.deposit -= amount
    
    # Update to_acc manually to avoid object re-creation issues or just update dict
    # But using Account object is cleaner if we want to use its methods.
    # We need to update the dictionaries in the list.
    
    from_acc_data["deposit"] -= amount
    to_acc_data["deposit"] += amount
    
    save_accounts(accounts)
    
    # Log for both
    log_transaction(from_acno, "TRANSFER_SENT", amount, to_acno)
    log_transaction(to_acno, "TRANSFER_RECEIVED", amount, from_acno)
    
    return True, "Transfer Successful"
