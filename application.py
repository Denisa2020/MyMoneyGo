import os
import sqlite3

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    """Show current balance, current month income, spending and savings and list of recent transactions"""

    balanceRows = db.execute("SELECT balance, currency from users WHERE id=:user_id", user_id=session["user_id"])
    currentBalance = balanceRows[0]["balance"]
    currency = balanceRows[0]["currency"]
    if currentBalance == 0 and currency == None:
        currency="EUR"
        return render_template("index.html", holdings=None, currentBalance=currentBalance, currency=currency, income=0, expenditure=0, savings=0)

    else:
        rows = db.execute("SELECT category, currency, SUM(amount) as amountTotal, transacted FROM transactions WHERE user_id=:user_id GROUP BY category", user_id=session["user_id"])

        holdings = []
        for row in rows:
            holdings.append({
                "category": row["category"],
                "currency": row["currency"],
                "amount": row["amountTotal"],
                "transacted": row["transacted"]
            })

        balanceRows = db.execute("SELECT balance, currency from users WHERE id=:user_id", user_id=session["user_id"])
        currentBalance = balanceRows[0]["balance"]
        currency = balanceRows[0]["currency"]

        incomeRows = db.execute("SELECT type, SUM(amount) as amountTotal from transactions WHERE user_id=:user_id AND type=:type", user_id=session["user_id"], type="Income")
        if incomeRows[0]["amountTotal"] == None:
            income = 0
        else:
            income = float(incomeRows[0]["amountTotal"])

        expenditureRows = db.execute("SELECT type, SUM(amount) as amountTotal from transactions WHERE user_id=:user_id AND type=:type", user_id=session["user_id"], type="Expenditure")
        if expenditureRows[0]["amountTotal"] == None:
            expenditure = 0
        else:
            expenditure = float(expenditureRows[0]["amountTotal"])

        savingsRows = db.execute("SELECT type, SUM(amount) as amountTotal from transactions WHERE user_id=:user_id AND type=:type", user_id=session["user_id"], type="Savings")
        if savingsRows[0]["amountTotal"] == None:
            savings = 0
        else:
            savings = float(savingsRows[0]["amountTotal"])*-1

        return render_template("index.html", holdings=holdings, currentBalance=currentBalance, currency=currency, income=income, expenditure=expenditure, savings=savings)

@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    """Add income to the balance"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        type="Income"
        category=request.form.get("category")
        currency=request.form.get("currency").upper()
        amount=float(request.form.get("amount"))


        # Ensure category and amount fields are valid
        if not category:
            return apology("invalid category, please resubmit", 403)
        elif not amount:
            return apology("invalid amount, please resubmit", 403)

        rows = db.execute("SELECT balance FROM users WHERE id=:id", id=session["user_id"])
        balance = float(rows[0]["balance"])
        updatedBalance = float(balance + amount)
        db.execute("UPDATE users SET balance=:balance WHERE id=:id", balance=updatedBalance, id=session["user_id"])
        db.execute("UPDATE users SET currency=:currency WHERE id=:id", currency=currency, id=session["user_id"])

        db.execute("INSERT INTO transactions (user_id, type, category, amount, currency) VALUES (?,?,?,?,?)", session["user_id"], type, category, amount, currency)
        flash("Income added!")
        # Redirect user to index page
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("income.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    rows = db.execute("SELECT * FROM transactions WHERE user_id=:user_id ORDER BY transacted DESC", user_id=session["user_id"])
    holdings = []

    for row in rows:
        holdings.append({
            "type": row["type"],
            "category": row["category"],
            "currency": row["currency"],
            "amount": row["amount"],
            "transacted": row["transacted"]
        })


    return render_template("history.html", holdings=holdings)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 401)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password")==request.form.get("re-typed-password"):
            return apology("Your passwords don't match", 403)

        # Ensure password field is completed
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password field is completed
        elif not request.form.get("re-typed-password"):
            return apology("must re-type password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) > 0:
            return apology("Sorry, this username already exists", 403)

        # Hash the new user's password
        username=request.form.get("username")
        password=request.form.get("password")
        hashed_password=generate_password_hash(password)

        # Insert the new user in the users table in the finance.db
        db.execute("INSERT INTO users(username,hash) VALUES(?,?)", username, hashed_password)

        # Redirect user to login page
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/expenditure", methods=["GET", "POST"])
@login_required
def expenditure():
    """Add an expenditure"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        rows = db.execute("SELECT balance FROM users WHERE id=:id", id=session["user_id"])
        balance = float(rows[0]["balance"])
        amount = float(request.form.get("amount"))

        if amount > balance:
            return apology("not enough balance for this expenditure", 403)

        else:
            type="Expenditure"
            category=request.form.get("category")
            amount=float(request.form.get("amount"))* -1
            currency=request.form.get("currency").upper()
            updatedBalance = float(balance + amount)
            db.execute("UPDATE users SET balance=:balance, currency=:currency WHERE id=:id", balance=updatedBalance, currency=currency, id=session["user_id"])

            db.execute("INSERT INTO transactions (user_id, type, category, amount, currency) VALUES (?,?,?,?,?)", session["user_id"], type, category, amount, currency)
            flash("Expenditure added!")
            if updatedBalance < 0:
                flash("Ups! You spent over your balance!")

            # Redirect user to index page
            return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("expenditure.html")

@app.route("/savings", methods=["GET", "POST"])
@login_required
def savings():
    """Add a savings amount"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        type="Savings"
        category="savings"
        amount=float(request.form.get("amount"))
        currency=request.form.get("currency").upper()

        rows = db.execute("SELECT balance FROM users WHERE id=:id", id=session["user_id"])
        balance = float(rows[0]["balance"])

        if amount > balance:
            return apology("sorry, you cannot save more than your current balance", 403)
        else:
            updatedBalance = float(balance - amount)
            db.execute("UPDATE users SET balance=:balance WHERE id=:id", balance=updatedBalance, id=session["user_id"])

        amount=amount*-1
        db.execute("INSERT INTO transactions (user_id, type, category, amount, currency) VALUES (?,?,?,?,?)", session["user_id"], type, category, amount, currency)
        flash("Congratulations! You added to your savings!")

        rows = db.execute("SELECT SUM(amount) as total_savings FROM transactions WHERE user_id=:user_id AND type=:type", user_id=session["user_id"], type="Savings")
        total_savings = (rows[0]["total_savings"])*-1

        # Redirect user to saved page
        return render_template("saved.html", currency=currency, amount=amount*-1, total_savings=total_savings)


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("savings.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
