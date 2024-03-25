from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
import sqlite3
from datetime import datetime

app = Flask(__name__)

socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if session:
        return redirect("/chat")
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("form.html", action="auth")

@app.route("/signup")
def signup():
    return render_template("form.html", action="adduser")

@app.route("/adduser", methods=["POST"])
def adduser():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return "failure!"
    db = sqlite3.connect("test.db")
    cursor = db.cursor()
    cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    db.commit()
    return redirect(url_for("auth", username=username, password=password), code=307)

@app.route("/auth", methods=["POST"])
def auth():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return "failure!"
    db = sqlite3.connect("test.db")
    cursor = db.cursor()
    response = cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    if response.fetchone() is None:
        return "failure!"
    else:
        session["username"] = username
        return redirect("/chat")

@app.route("/chat")
def chat():
    if not session["username"]:
        return "failure!"
    db = sqlite3.connect("test.db")
    cursor = db.cursor()
    messages = cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    return render_template("chat.html", messages=messages, username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# @app.route("/sendmessage", methods=["POST"])
# def sendmessage():
#     username = session["username"]
#     now = datetime.now()
#     time = str(now.strftime("%d/%m/%Y %H:%M"))
#     content = request.form.get("content")

#     db = sqlite3.connect("test.db")
#     cursor = db.cursor()
#     cursor.execute("INSERT INTO messages (username, content, datetime) VALUES (?, ?, ?)", (username, content, time))
#     db.commit()
#     return redirect("/chat")

@socketio.on('sendMessage')
def handle_message(message):
    
    username = session.get("username")
    now = datetime.now()
    time = str(now.strftime("%d/%m/%Y %H:%M"))

    db = sqlite3.connect("test.db")
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (username, content, datetime) VALUES (?, ?, ?)", (username, message, time))
    db.commit()
    print({'username': username, 'content': message, 'datetime': time})
    emit('receiveMessage', {'username': username, 'content': message, 'datetime': time}, broadcast=True)
