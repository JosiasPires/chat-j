import os
from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session
from flask_socketio import SocketIO, emit
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/uploads"
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
    db = sqlite3.connect("chat.db")
    cursor = db.cursor()
    user = cursor.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    print(user)
    if user:
        return "user already exists!"
    cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    db.commit()
    return redirect(url_for("auth", username=username, password=password), code=307)

@app.route("/auth", methods=["POST"])
def auth():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return "failure!"
    db = sqlite3.connect("chat.db")
    cursor = db.cursor()
    response = cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = response.fetchone()
    if not user:
        return "failure!"
    session["userId"] = user[0]
    session["username"] = user[1]
    if not user[3]:
        picturePath = "/static/user.png"
        cursor.execute("UPDATE user SET picturePath = ? WHERE id = ?", (picturePath, session["userId"]))
        db.commit()
    db.close()
    return redirect("/chat")

@app.route("/chat")
def chat():
    if not session.get("userId"):
        session.clear()
        return "failure!"
    db = sqlite3.connect("chat.db")
    cursor = db.cursor()
    messages = cursor.execute("SELECT username, content, datetime, picturePath FROM messages JOIN user ON user.id = messages.userId ORDER BY messages.id DESC").fetchall();
    db.close()
    return render_template("chat.html", messages=messages, userId=session["userId"], username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@socketio.on('sendMessage')
def handle_message(message):
    userId = session.get("userId")
    now = datetime.now()
    time = str(now.strftime("%d/%m/%Y %H:%M"))

    db = sqlite3.connect("chat.db")
    cursor = db.cursor()

    cursor.execute("INSERT INTO messages (userId, content, datetime) VALUES (?, ?, ?)", (userId, message, time))
    picturePath = cursor.execute("SELECT picturePath FROM user WHERE id = ?", (userId,)).fetchone()
    db.commit()
    db.close()
    emit('receiveMessage', {'userId': userId, 'picturePath': picturePath, 'username': session["username"], 'content': message, 'datetime': time}, broadcast=True)

@app.route("/uploadpicture", methods=["POST"])
def uploadpicture():
    picture = request.files["picture"]
    filename = secure_filename(picture.filename)
    picturePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    picture.save(picturePath)
    db = sqlite3.connect("chat.db")
    cursor = db.cursor()
    cursor.execute("UPDATE user SET picturePath = ? WHERE id = ?", (picturePath, session.get("userId")))
    db.commit()
    db.close()
    return redirect("/chat")