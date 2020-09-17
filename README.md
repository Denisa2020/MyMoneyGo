Sample Money Balance Application: MyMoneyGo
MyMoneyGo is a simple app created using Python, HTML, CSS, Bootstrap and SQL.

Purpose
Keeping track of income, expenditures and savings.

Usage

Register as a new user:
    - selected username will be checked against users database and a message will be displayed if the username already exists;
    - password needs to be minimum 8 characters and include at least one uppercase and lowercase letter and one number.
![Register](/screenshots/Register.png?raw=true "Register")

Log in

Add income
![Add income](/screenshots/Add_income.png?raw=true "Add income")

Income added
![Income_added](/screenshots/Income_added.png?raw=true "Income_added")

Add expenditure
![Add expenditure](/screenshots/Add_expenditure.png?raw=true "Add expenditure")

Expenditure added
![Expenditure_added](/screenshots/Expenditure_added.png?raw=true "Expenditure_added")

Add savings
![Add savings](/screenshots/Add_savings.png?raw=true "Add savings")

Savings added
![Savings_added](/screenshots/Savings_added.png?raw=true "Savings_added")

Index page (new user):
    - shows 0 balance, 0 savings, 0 expenditure, 0 income
    - summary shows no transactions
    - there are links to add savings, expenditure, income, view history
![Index new user](/screenshots/Index_new_user.png?raw=true "Index new user")

Index page(existing user with previous transactions:
    - shows current balance, current savings, current expenditure, current income
    - summary shows all previous transactions grouped by category
    - there are links to add savings, expenditure, income, view history
![Index](/screenshots/Index.png?raw=true "Index")

History page shows all itemized previous transactions in descending order by date.
![History](/screenshots/History.png?raw=true "History")

History for new user is blank
![History new user](/screenshots/History_new_user.png?raw=true "History new user")

When the user tries to add expenditure higher than the remaining balance, an error message is displayed
![Expenditure over balance](/screenshots/Expenditure_over_balance.png?raw=true "Expenditure_over_balance")

When the user tries to add savings higher than the remaining balance, an error message is displayed
![Savings over balance](/screenshots/Savings_over_balance.png?raw=true "Savings_over_balance")

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

