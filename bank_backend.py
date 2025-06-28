import json
import os

ACCOUNTS_FILE = "accounts.json"

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

    def withdraw_amount(self, amount):
        if self.acc_type == 'S' and self.deposit - amount < 500:
            return False
        if self.acc_type == 'C' and self.deposit - amount < 1000:
            return False
        self.deposit -= amount
        return True
