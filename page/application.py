from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_file
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.hash import pbkdf2_sha256

from helpers import *

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

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///note.db")
ID = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("Log.html", error="Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("Log.html", error="Must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))


        # ensure username exists and password is correct
        if len(rows) != 1 or not pbkdf2_sha256.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("Log.html", error="Invalid username or password")
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("home"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("Log.html")

@app.route("/logout")
def logout():
    """Log user out."""

    #forget any user_id
    session.clear()
    
    #redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":
        user = db.execute("SELECT * FROM users")
        if not request.form.get("username"):
            return render_template("register.html",error="Missing username")
        if not request.form.get("password"):
            return render_template("register.html",error="Missing password")
        if request.form.get("password") != request.form.get("Password_confirmation"):
            return render_template("register.html",error="Password must be the same")
        if request.form.get("username") in user[0]["username"]:
            return render_template("register.html",error="User already register")
        hash = pbkdf2_sha256.hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)
        return redirect(url_for("login"))
    else:
        return render_template("register.html")
    

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])
    name = user[0]["username"]
    if request.method == "POST":
            db.execute("INSERT INTO notes (username, note) VALUES (:name, :note)", name=name, note=request.form.get("note"))
    return render_template("home.html", username=name)
    
@app.route("/notes", methods=["GET","POST"])
@login_required
def notes():
    user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])
    name = user[0]["username"]
    notes = db.execute("SELECT * FROM notes WHERE username=:name", name = name)
    if request.method == "POST":
        if request.form.get("id") == None:
            return "falta id"
        if request.form.get("chooseone") == "delete":
            id = request.form.get("id")
            ids = db.execute("SELECT note FROM notes WHERE id=:id",id=id)
            if ids != None:
                db.execute("DELETE FROM notes WHERE id=:id", id=id)
                notes = db.execute("SELECT * FROM notes WHERE username=:name", name = name)
                return render_template("notes.html",name=name, notes=notes)
        if request.form.get("chooseone") == "edit":
            id = request.form.get("id")
            note = db.execute("SELECT * FROM notes WHERE username=:name", name = name)
            note = note[0]["note"]
            text = db.execute("SELECT note FROM notes WHERE id=:id", id=id)
            db.execute("DELETE FROM notes WHERE id=:id", id=id)
            return render_template("home.html", note=text[0]["note"])
        if request.form.get("chooseone") == "download":
            id = request.form.get("id")
            note =  db.execute("SELECT * FROM notes WHERE id=:id", id=id)
            note = note[0]["note"]
            text = open('note.txt', 'w')
            text.write(note)
            text.close()
            return send_file("note.txt")
    return render_template("notes.html",name=name, notes=notes)
    
@app.route("/movil", methods=["GET","POST"])
def movil():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("indexMovil.html", error="Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("indexMovil.html", error="Must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))


        # ensure username exists and password is correct
        if len(rows) != 1 or not pbkdf2_sha256.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("indexMovil.html", error="Invalid username or password")
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("NoteMovil"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("indexMovil.html")
    
@app.route("/NoteMovil", methods=["GET","POST"])
def NoteMovil():
    if request.method == "POST":
        user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])
        name = user[0]["username"]
        if request.form.get("note") != None:
            db.execute("INSERT INTO notes (username, note) VALUES (:name, :note)", name=name, note=request.form.get("note"))
    return render_template("noteMovil.html")
    
    
@app.route("/load", methods=["GET","POST"])
def load():
    user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])
    name = user[0]["username"]
    notes = db.execute("SELECT * FROM notes WHERE username=:name", name = name)
    if request.method == "POST":
        if not request.form.get("id"):
            note =  db.execute("SELECT * FROM notes WHERE username=:name", name = name)
            return render_template("load.html", notes=notes, error="Must provide id")
        id = request.form.get("id")
        note = db.execute("SELECT * FROM notes WHERE username=:name", name = name)
        note = note[0]["note"]
        text = db.execute("SELECT note FROM notes WHERE id=:id", id=id)
        db.execute("DELETE FROM notes WHERE id=:id", id=id)
        return render_template("noteMovil.html", text=text[0]["note"])
    return render_template("load.html", notes=notes)
    
@app.route("/extention")
def extention():
    return render_template("ext.html")
    
@app.route("/contact")
def contact():
    return render_template("contac.html")
    
@app.route("/change", methods=["GET","POST"])
def change():
    if request.method == "POST":
        user = db.execute("SELECT * FROM users")
        if not request.form.get("username"):
            return render_template("change.html",error="Missing username")
        if not request.form.get("password"):
            return render_template("change.html",error="Missing password")
        if request.form.get("password") != request.form.get("password_confirmation"):
            return render_template("change.html",error="Password must be the same")
        if request.form.get("username") in user[0]["username"]:
            hash = pbkdf2_sha256.hash(request.form.get("password"))
            db.execute("UPDATE users SET hash=:hash WHERE username=:username", username=request.form.get("username"), hash=hash)
        return redirect(url_for("login"))
    else:
        return render_template("change.html")

@app.route("/about")
def about():
    return render_template("about.html")