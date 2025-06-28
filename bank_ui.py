import tkinter as tk
from tkinter import messagebox
from bank_backend import Account, load_accounts, save_accounts

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("500x400")
        self.create_main_menu()

    def create_main_menu(self):
        tk.Label(self.root, text="BANK MANAGEMENT SYSTEM", font=("Helvetica", 16)).pack(pady=20)
        buttons = [
            ("New Account", self.new_account),
            ("Deposit", self.deposit),
            ("Withdraw", self.withdraw),
            ("Balance Enquiry", self.balance_enquiry),
            ("All Accounts", self.list_accounts),
            ("Modify Account", self.modify_account),
            ("Delete Account", self.delete_account),
            ("Exit", self.root.quit)
        ]
        for (text, command) in buttons:
            tk.Button(self.root, text=text, width=25, command=command).pack(pady=5)

    def new_account(self):
        self.popup_account_form("Create Account")

    def popup_account_form(self, title, existing=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x300")

        tk.Label(win, text="Account No").pack()
        acno_entry = tk.Entry(win)
        acno_entry.pack()

        tk.Label(win, text="Name").pack()
        name_entry = tk.Entry(win)
        name_entry.pack()

        tk.Label(win, text="Account Type (C/S)").pack()
        type_entry = tk.Entry(win)
        type_entry.pack()

        tk.Label(win, text="Deposit").pack()
        deposit_entry = tk.Entry(win)
        deposit_entry.pack()

        if existing:
            acno_entry.insert(0, existing["acno"])
            acno_entry.config(state="disabled")
            name_entry.insert(0, existing["name"])
            type_entry.insert(0, existing["type"])
            deposit_entry.insert(0, existing["deposit"])

        def submit():
            try:
                acno = int(acno_entry.get())
                name = name_entry.get()
                acc_type = type_entry.get().upper()
                deposit = int(deposit_entry.get())
                if acc_type not in ("S", "C"):
                    raise ValueError("Invalid account type")
                if (acc_type == "S" and deposit < 500) or (acc_type == "C" and deposit < 1000):
                    raise ValueError("Minimum deposit not met")
                accounts = load_accounts()
                if existing:
                    for acc in accounts:
                        if acc["acno"] == acno:
                            acc["name"] = name
                            acc["type"] = acc_type
                            acc["deposit"] = deposit
                            break
                    msg = "Account modified."
                else:
                    if any(acc["acno"] == acno for acc in accounts):
                        raise ValueError("Account number exists")
                    acc = Account(acno, name, acc_type, deposit)
                    accounts.append(acc.to_dict())
                    msg = "Account created."
                save_accounts(accounts)
                messagebox.showinfo("Success", msg)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Submit", command=submit).pack(pady=10)

    def deposit(self):
        self.transaction_window("Deposit")

    def withdraw(self):
        self.transaction_window("Withdraw")

    def transaction_window(self, action):
        win = tk.Toplevel(self.root)
        win.title(action)
        win.geometry("250x200")

        tk.Label(win, text="Account No").pack()
        acno_entry = tk.Entry(win)
        acno_entry.pack()

        tk.Label(win, text="Amount").pack()
        amount_entry = tk.Entry(win)
        amount_entry.pack()

        def submit():
            acno = int(acno_entry.get())
            amount = int(amount_entry.get())
            accounts = load_accounts()
            for acc in accounts:
                if acc["acno"] == acno:
                    account = Account.from_dict(acc)
                    if action == "Deposit":
                        account.deposit_amount(amount)
                    else:
                        if not account.withdraw_amount(amount):
                            messagebox.showerror("Error", "Insufficient balance")
                            return
                    acc.update(account.to_dict())
                    save_accounts(accounts)
                    messagebox.showinfo("Success", f"{action} successful")
                    win.destroy()
                    return
            messagebox.showerror("Error", "Account not found")

        tk.Button(win, text="Submit", command=submit).pack(pady=10)

    def balance_enquiry(self):
        self.simple_input_window("Balance Enquiry", self.show_balance)

    def modify_account(self):
        self.simple_input_window("Modify Account", self.modify_form)

    def delete_account(self):
        self.simple_input_window("Delete Account", self.delete_confirm)

    def list_accounts(self):
        accounts = load_accounts()
        win = tk.Toplevel(self.root)
        win.title("All Accounts")
        text = tk.Text(win, width=60)
        text.pack()
        for acc in accounts:
            text.insert(tk.END, f"{acc['acno']} | {acc['name']} | {acc['type']} | {acc['deposit']}\n")

    def simple_input_window(self, title, callback):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("200x150")
        tk.Label(win, text="Account No").pack()
        acno_entry = tk.Entry(win)
        acno_entry.pack()

        def submit():
            try:
                acno = int(acno_entry.get())
                callback(acno, win)
            except:
                messagebox.showerror("Error", "Invalid input")

        tk.Button(win, text="Submit", command=submit).pack(pady=10)

    def show_balance(self, acno, win):
        accounts = load_accounts()
        for acc in accounts:
            if acc["acno"] == acno:
                messagebox.showinfo("Balance", f"Account: {acc['acno']}\nName: {acc['name']}\nBalance: {acc['deposit']}")
                win.destroy()
                return
        messagebox.showerror("Error", "Account not found")

    def modify_form(self, acno, win):
        accounts = load_accounts()
        for acc in accounts:
            if acc["acno"] == acno:
                win.destroy()
                self.popup_account_form("Modify Account", existing=acc)
                return
        messagebox.showerror("Error", "Account not found")

    def delete_confirm(self, acno, win):
        accounts = load_accounts()
        accounts = [acc for acc in accounts if acc["acno"] != acno]
        save_accounts(accounts)
        messagebox.showinfo("Success", "Account deleted.")
        win.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
