# final project application!
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from helpers import *

import os
import re
from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue
import string

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///CEID.db")


@app.route("/")
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    elif request.method == "POST":
        if not request.form.get("general_search"):
            return apology("must enter item to search")
            
        s = request.form.get("general_search") + "%"
    
        return redirect(url_for("general_search"))
    
    return apology("index failed")

    
@app.route("/general_search", methods=["GET", "POST"])
@login_required
def general_search():
    """Allows users to search generally."""
    if request.method == "GET":
        return render_template("general_search.html")
    
    elif request.method == "POST":
        if not request.form.get("general_search"):
            return apology("must enter supply to search")
            
        supply = request.form.get("general_search")

        # search in entire database for the supply
        rows = db.execute("SELECT * FROM supplies WHERE name LIKE :name", name = supply)
        
        #set which image link to pass in
        section = rows[0]["section"]
        if section == "Arts and Crafts Bench":
            image_link = "http://i.imgur.com/0H31SF1.jpg";
        elif section == "Circuit Pieces Cabinets":
            image_link = "http://i.imgur.com/n1zAUWo.jpg";
        elif section == "Sewing Station":
            image_link = "http://i.imgur.com/L97GSc0.jpg";
        elif section == "Computer Station":
            image_link = "http://i.imgur.com/N5k9Q8f.jpg";
        elif section == "Handtools Station":
            image_link = "http://i.imgur.com/Ym5KWFI.jpg";
        elif section == "Wires and Whatnot":
            image_link = "http://i.imgur.com/1h3nDzx.jpg";
        elif section == "3D Printers":
            image_link = "http://i.imgur.com/HVYEVFI.jpg";
        
        # if nothing comes up, return apology
        if not rows:
            return apology("supply not found")
            
        return render_template("general_search.html", rows = rows, image_link = image_link)
        
@app.route("/advanced_search", methods=["GET", "POST"])
@login_required
def advanced_search():
    """Allows users to search within specific sections."""
    if request.method == "GET":
        #if arrive straight from index, display ALL supplies in that section
        #how to pass in which section you came from?
        section = "section_1"
        rows = db.execute("SELECT * FROM supplies WHERE section = :section", section = section)
        
        #set which image link to pass in
        if section == "section_1":
            image_link = "http://i.imgur.com/0H31SF1.jpg";
        elif section == "section_2":
            image_link = "http://i.imgur.com/n1zAUWo.jpg";
        elif section == "section_3":
            image_link = "http://i.imgur.com/L97GSc0.jpg";
        elif section == "section_4":
            image_link = "http://i.imgur.com/N5k9Q8f.jpg";
        elif section == "section_5":
            image_link = "http://i.imgur.com/Ym5KWFI.jpg";
        elif section == "section_6":
            image_link = "http://i.imgur.com/1h3nDzx.jpg";
        elif section == "section_7":
            image_link = "http://i.imgur.com/HVYEVFI.jpg";
            
        return render_template("advanced_search.html", image_link = image_link, section = section, rows = rows)
    
    elif request.method == "POST":
        if not request.form.get("advanced_search"):
            section = request.form.get("section")
            rows = db.execute("SELECT * FROM supplies WHERE section = :section", section = section)
            
        elif not request.form.get("section"):
            return apology("must enter section to search")
            
            supply = request.form.get("advanced_search")
            section = request.form.get("section")
        
            rows = db.execute("SELECT * FROM supplies WHERE name = :name AND section = :section", name = supply, section = section)
        
        #set which image link to pass in
        if section == "Arts and Crafts Bench":
            image_link = "http://i.imgur.com/0H31SF1.jpg";
        elif section == "Circuit Pieces Cabinets":
            image_link = "http://i.imgur.com/n1zAUWo.jpg";
        elif section == "Sewing Station":
            image_link = "http://i.imgur.com/L97GSc0.jpg";
        elif section == "Computer Station":
            image_link = "http://i.imgur.com/N5k9Q8f.jpg";
        elif section == "Handtools Station":
            image_link = "http://i.imgur.com/Ym5KWFI.jpg";
        elif section == "Wires and Whatnot":
            image_link = "http://i.imgur.com/1h3nDzx.jpg";
        elif section == "3D Printers":
            image_link = "http://i.imgur.com/HVYEVFI.jpg";
        else:
            #render apology image
            image_link = "http://i.imgur.com/tynvif9.jpg";
            
        return render_template("advanced_search.html", image_link = image_link, section = section, rows = rows)
    

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
# if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("must provide username")
        
        # ensure username exists
        existing = db.execute("SELECT * FROM users WHERE username = :username", username = username)
        if len(existing) == 0:
            return apology("username does not exist")
        
        # check if old password was submitted
        elif not request.form.get("old_password"):
            return apology("must provide old password")
        
        # check if old password is indeed that user's old password
        elif not pwd_context.verify(request.form.get("old_password"), existing[0]["hash"]):
            return apology("old password was incorrect")
            
        # ensure password was submitted
        elif not request.form.get("new_password") or not request.form.get("confirm_password"):
            return apology("must provide new password and confirm password")

        # ensure passwords match
        elif request.form.get("new_password") != request.form.get("confirm_password"):
            return apology("password and confirmation do not match")
            
        # hash password
        password = request.form.get("new_password")
        Hash = pwd_context.encrypt(password)
        # verify (what does verify give you?)
        ok = pwd_context.verify(password, Hash)

        # add user to db
        if ok == True:
            db.execute("UPDATE users SET hash = :h WHERE username = :username", h = Hash, username = username)
            
            # query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

            # remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # redirect user to home page
            return redirect(url_for("index"))
        else:
            return apology("Incorrect old password")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")
        

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
        # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("must provide username")
        
        # ensure username doesn't already exist
        existing = db.execute("SELECT * FROM users WHERE username = :name", name = username)
        if len(existing) != 0:
            return apology("username unavailable. choose another")

        # ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirm_password"):
            return apology("must provide password and confirm password")

        # ensure passwords match
        elif request.form.get("password") != request.form.get("confirm_password"):
            return apology("password and confirmation do not match")
        
        # ensure security question and answer were submitted
        elif not request.form.get("security_q") or not request.form.get("answer"):
            return apology("must enter security question and answer")
            
        # hash password
        password = request.form.get("password")
        Hash = pwd_context.encrypt(password)
        # verify (what does verify give you?)
        ok = pwd_context.verify(password, Hash)
        
        
        # add user to db
        if ok == True:
            db.execute("INSERT INTO users(username, hash, security_Q, answer) VALUES (:username, :h, :Q, :A)", username = username, h = Hash, Q = request.form.get("security_q"), A = request.form.get("answer"))
            
            # query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

            # remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # redirect user to home page
            return redirect(url_for("index"))
        else:
            return apology("ok was False!!!")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
        

