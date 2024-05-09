import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def home():
    """Show portfolio of planners"""

    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE name = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/planners")

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
    # forget any user id
    session.clear()

    # if POST
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        elif not confirmation:
            return apology("must confirm password")

        elif password != confirmation:
            return apology("passwords do not match")

        # see if user does not already exist
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)
        if len(rows) != 0:
            return apology("user already exists")

        # remember user in database
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (name, hash) VALUES (?, ?)", username, hash)

        # query database for new user
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # if GET
    else:
        return render_template("register.html")



@app.route("/planners", methods=["GET", "POST"])
@login_required
def planners():
    """Show portfolio of planners"""
    if request.method == "POST":
        filter = request.form.get("filter")
        
        if not filter:
            return redirect("/planners")

        exercises = db.execute(
            "SELECT * FROM exercises WHERE user_id = ? AND day_week = ?", session["user_id"], filter
        )

        return render_template("planners.html", exercises=exercises)
    
    else:
        exercises = db.execute(
            "SELECT * FROM exercises WHERE user_id = ? ORDER BY day_week", session["user_id"])

        return render_template("planners.html", exercises=exercises)



@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    
    if request.method == "POST":

        delete = request.form.get("delete")

        db.execute(
            "DELETE FROM exercises WHERE id = ?", delete
        )

        return redirect("/planners")
    
    else:
        exercises = db.execute(
            "SELECT * FROM exercises WHERE user_id = ? ORDER BY day_week", session["user_id"])

        return render_template("delete.html", exercises=exercises)


@app.route("/add_planner", methods=["GET", "POST"])
@login_required
def add_planner():
    if request.method == "POST":
        day = request.form.get("day_of_week")
        if not day:
            return apology("must provide day")
        muscle = request.form.get("muscle")
        if not muscle:
            return apology("must provide muscle")
        exercise = request.form.get("exercise")
        if not exercise:
            return apology("must provide exercise")
        sets = request.form.get("sets")
        if not sets or not sets.isdigit():
            return apology("must provide a positive number of sets")
        reps = request.form.get("reps")
        if not reps or not reps.isdigit():
            return apology("must provide a positive number of repetitions")

        db.execute("INSERT INTO exercises (user_id, day_week, muscle, exercise, sets, reps) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], day, muscle, exercise, sets, reps)

        return redirect("/planners")

    else:
        return render_template("add_planner.html")


