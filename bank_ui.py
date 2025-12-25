import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from bank_backend import Account, load_accounts, save_accounts, transfer_funds, get_account_transactions

# Set Theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("550x500")
        self.create_main_menu()

    def create_main_menu(self):
        # Using a Frame for better centering and layout
        self.menu_frame = ctk.CTkFrame(self.root)
        self.menu_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.menu_frame, text="BANK MANAGEMENT SYSTEM", font=("Roboto Medium", 20)).pack(pady=20)
        
        buttons = [
            ("New Account", self.new_account),
            ("Deposit", self.deposit),
            ("Withdraw", self.withdraw),
            ("Fund Transfer", self.fund_transfer),
            ("Balance Enquiry", self.balance_enquiry),
            ("Transaction History", self.transaction_history),
            ("All Accounts", self.list_accounts),
            ("Modify Account", self.modify_account),
            ("Delete Account", self.delete_account),
            ("Exit", self.root.quit)
        ]
        
        for (text, command) in buttons:
            ctk.CTkButton(self.menu_frame, text=text, width=200, command=command).pack(pady=5)

    def new_account(self):
        self.popup_account_form("Create Account")

    def popup_account_form(self, title, existing=None):
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("350x450")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Account No").pack(pady=(20, 5))
        acno_entry = ctk.CTkEntry(win)
        acno_entry.pack()

        ctk.CTkLabel(win, text="Name").pack(pady=5)
        name_entry = ctk.CTkEntry(win)
        name_entry.pack()

        ctk.CTkLabel(win, text="Account Type (C/S)").pack(pady=5)
        type_entry = ctk.CTkEntry(win)
        type_entry.pack()

        ctk.CTkLabel(win, text="Deposit").pack(pady=5)
        deposit_entry = ctk.CTkEntry(win)
        deposit_entry.pack()

        if existing:
            acno_entry.insert(0, existing["acno"])
            acno_entry.configure(state="disabled")
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
                    raise ValueError("Invalid account type (C/S)")
                if (acc_type == "S" and deposit < 500) or (acc_type == "C" and deposit < 1000):
                    raise ValueError("Minimum deposit not met (S:500, C:1000)")
                
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

        ctk.CTkButton(win, text="Submit", command=submit).pack(pady=20)

    def deposit(self):
        self.transaction_window("Deposit")

    def withdraw(self):
        self.transaction_window("Withdraw")

    def transaction_window(self, action):
        win = ctk.CTkToplevel(self.root)
        win.title(action)
        win.geometry("300x300")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Account No").pack(pady=(20, 5))
        acno_entry = ctk.CTkEntry(win)
        acno_entry.pack()

        ctk.CTkLabel(win, text="Amount").pack(pady=5)
        amount_entry = ctk.CTkEntry(win)
        amount_entry.pack()

        def submit():
            try:
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
            except ValueError:
                 messagebox.showerror("Error", "Invalid Input")

        ctk.CTkButton(win, text="Submit", command=submit).pack(pady=20)

    def balance_enquiry(self):
        self.simple_input_window("Balance Enquiry", self.show_balance)

    def modify_account(self):
        self.simple_input_window("Modify Account", self.modify_form)

    def delete_account(self):
        self.simple_input_window("Delete Account", self.delete_confirm)

    def fund_transfer(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Fund Transfer")
        win.geometry("350x400")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="From Account No").pack(pady=(20, 5))
        from_entry = ctk.CTkEntry(win)
        from_entry.pack()

        ctk.CTkLabel(win, text="To Account No").pack(pady=5)
        to_entry = ctk.CTkEntry(win)
        to_entry.pack()

        ctk.CTkLabel(win, text="Amount").pack(pady=5)
        amount_entry = ctk.CTkEntry(win)
        amount_entry.pack()

        def submit():
            try:
                from_acno = int(from_entry.get())
                to_acno = int(to_entry.get())
                amount = int(amount_entry.get())
                
                success, msg = transfer_funds(from_acno, to_acno, amount)
                if success:
                    messagebox.showinfo("Success", msg)
                    win.destroy()
                else:
                    messagebox.showerror("Error", msg)
            except ValueError:
                messagebox.showerror("Error", "Invalid input")

        ctk.CTkButton(win, text="Transfer", command=submit).pack(pady=20)

    def transaction_history(self):
        self.simple_input_window("Transaction History", self.show_history)

    def show_history(self, acno, win):
        transactions = get_account_transactions(acno)
        if not transactions:
            messagebox.showinfo("Info", "No transactions found for this account")
            win.destroy()
            return
            
        win.destroy()
        hist_win = ctk.CTkToplevel(self.root)
        hist_win.title(f"History: {acno}")
        hist_win.geometry("500x400")
        hist_win.attributes("-topmost", True)
        
        # Use CTkTextbox for scrollable text
        text = ctk.CTkTextbox(hist_win, width=460, height=360)
        text.pack(pady=20, padx=20)
        
        text.insert(tk.END, f"Transaction History for Account {acno}\n")
        text.insert(tk.END, "-"*60 + "\n")
        
        for t in transactions:
            line = f"{t['timestamp']} | {t['type']} | {t['amount']}"
            if t['related_acno']:
                line += f" | Ref: {t['related_acno']}"
            text.insert(tk.END, line + "\n")
        text.configure(state="disabled") # Make read-only

    def list_accounts(self):
        accounts = load_accounts()
        win = ctk.CTkToplevel(self.root)
        win.title("All Accounts")
        win.geometry("500x400")
        win.attributes("-topmost", True)
        
        text = ctk.CTkTextbox(win, width=460, height=360)
        text.pack(pady=20, padx=20)
        
        for acc in accounts:
            text.insert(tk.END, f"{acc['acno']} | {acc['name']} | {acc['type']} | {acc['deposit']}\n")
        text.configure(state="disabled")

    def simple_input_window(self, title, callback):
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("300x200")
        win.attributes("-topmost", True)
        
        ctk.CTkLabel(win, text="Account No").pack(pady=(30, 10))
        acno_entry = ctk.CTkEntry(win)
        acno_entry.pack()

        def submit():
            try:
                acno = int(acno_entry.get())
                callback(acno, win)
            except:
                messagebox.showerror("Error", "Invalid input")

        ctk.CTkButton(win, text="Submit", command=submit).pack(pady=20)

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
    # Initialize CTk instead of Tk
    root = ctk.CTk()
    app = BankApp(root)
    root.mainloop()
