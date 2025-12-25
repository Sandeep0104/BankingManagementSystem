# Interview Questions & Answers: Banking Management System

## Project Overview
**Q1: Can you briefly describe your Banking Management System project?**
**Answer:** "This is a desktop-based application built using Python. It serves as a simulation of a core banking system allowing users to perform operations like creating accounts, depositing and withdrawing money, checking balances, and modifying account details. I used `Tkinter` for the Graphical User Interface (GUI) and a JSON file system for persistent data storage."

**Q2: What is the architecture of your application?**
**Answer:** "The application follows a modular design separating the frontend and backend:
- **Frontend (`bank_ui.py`):** Built with `Tkinter`, it handles all user interactions, input forms, and alerts.
- **Backend (`bank_backend.py`):** Contains the core logic. It defines the `Account` class for object-oriented data handling and functions to read/write data to `accounts.json`."

---

## Technical Implementation (Python & Data)

**Q3: Why did you use JSON for database storage instead of SQL?**
**Answer:** "For this specific project scope, JSON was chosen for its simplicity and ease of setup. It allows for quick serialization of Python objects (dictionaries) to a text format without needing a separate database server. However, for a production-scale app, I would migrate to an SQL database (like SQLite or PostgreSQL) to handle concurrency, relationships, and data integrity better."

**Q4: How do you handle data persistence?**
**Answer:** "I use the built-in `json` module. The `load_accounts()` function reads the `accounts.json` file and converts the JSON array into a list of Python dictionaries. The `save_accounts()` function does the reverse, writing the current state of accounts back to the file. This ensures data is not lost when the application closes."

**Q5: Explain the Object-Oriented nature of your project.**
**Answer:** "I created an `Account` class in `bank_backend.py` to encapsulate account-related data (account number, name, type, balance) and behaviors.
- **Encapsulation:** methods like `deposit_amount` and `withdraw_amount` handle logic internally.
- **Validation:** usage of `staticmethod` `from_dict` to instantiate objects from stored data."

---

## Logic & Algorithms

**Q6: How did you handle specific validations, like minimum balance?**
**Answer:** "Validations are handled in the `submit` logic of the UI and the `withdraw_amount` method in the backend.
- **Creation:** I check if the initial deposit meets the threshold (500 for Savings 'S', 1000 for Current 'C').
- **Withdrawal:** Before deducting money, the system checks if the remaining balance would fall below the minimum required limit for that account type. If it does, the transaction is rejected."

**Q7: How does your search/update logic work?**
**Answer:** "Since the data is small, I load all accounts into a list and iterate through it to find a match by `acno` (Account Number).
- **Search:** Linear search (O(n)).
- **Update:** Once the matching object is found and modified, the entire list is written back to the JSON file to save the changes."

---

## GUI (Tkinter)

**Q8: What challenges did you face with Tkinter?**
**Answer:** "One challenge was managing multiple windows. I used `Toplevel()` to create independent windows for forms (like Deposit or New Account) so they don't block the main application loop but still function as separate dialogs. I also had to carefully manage data types, converting `Entry` widget string outputs to `int` for calculations."

**Q9: How do you handle errors in the UI?**
**Answer:** "I implemented `try-except` blocks around user input handling. If a user enters non-numeric data for an amount or an invalid code, the application catches the exception and uses `messagebox.showerror` to display a user-friendly alert instead of crashing."

---

## Future Improvements

**Q10: If you had more time, what features would you add?**
**Answer:**
1.  **Authentication:** Add a login system for admins and users.
2.  **Database:** Migrate from JSON to SQLite for reliability.
3.  **Concurrency:** Handle multiple users accessing data simultaneously (locking).
4.  **Transaction History:** Instead of just updating the balance, verify a separate ledger of transactions to show a statement."
