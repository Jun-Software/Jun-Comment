import redis
from flask import *
import os
from pysmx.SM3 import SM3

def sm3_hash(data: str):
    s = SM3()
    s.update(data)
    return str(s.hexdigest())

app = Flask(__name__)

redis_host = str(os.getenv("REDIS_HOST"))
redis_port = str(os.getenv("REDIS_PORT"))
redis_password = str(os.getenv("REDIS_PASSWORD"))
app.config['SECRET_KEY'] = str(os.getenv("SESSION_KEY"))

db = redis.Redis(host = redis_host,
                port = redis_port,
                password = redis_password,
                decode_responses = True)

messages = []
message = db.get("message")
if message is not None:
    temp = message.split(";")
    temp.remove('')
    for i in temp:
        m = i.split(':')
        messages.append({'username': str(m[0]), 'message': str(m[1])})
else:
    message = ""

users = []
user = db.get("user")
if user is not None:
    temp = user.split(";")
    temp.remove('')
    for i in temp:
        u = i.split(':')
        users.append({'username': str(u[0]), 'password': str(u[1])})
else:
    user = ""
    
invites = []
invite = db.get("invite")
if user is not None:
    temp = invite.split(";")
    temp.remove('')
    for i in temp:
        invites.append(i)
else:
    invite = ""

@app.route("/")
def index():
    if session.get('login') is None or session.get('login') == False:
        return redirect('/login')
    return redirect("/chat")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if session.get('login') == True:
        return redirect('/chat')
    if request.method == "GET":
        inv = request.values.get("invite")
        if inv is None:
            return 404, '<html lang="en"><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p></body></html>'
        global invites
        if inv not in invites:
            return "邀请码错误！"
        return render_template("login.html")
    elif request.method == "POST":
        Type = request.values.get("type")
        username = request.values.get("username")
        password = request.values.get("password")
        global user
        global users
        if Type == 'register':
            if username is None or password is None:
                return redirect("/")
            if len(username) > 20:
                return "The username is too long."
            if ':' in username or ';' in username:
                return "The username contains special characters."
            user = str(user) + str(username) + ":" + str(sm3_hash(password)) + ";"
            users.append({"username": str(username), "password": str(sm3_hash(password))})
            db.set("user", user)
            session['login'] = True
            session['username'] = username
            return redirect("/chat")
        elif Type == 'login':
            for u in users:
                if u['password'] == sm3_hash(password) and u['username'] == username:
                    session['login'] = True
                    session['username'] = username
                    return redirect('/chat')
            return "The username or password do not match."

@app.route("/chat", methods = ["GET", "POST"])
def chat():
    if session.get('login') is None or session.get('login') == False:
        return redirect('/login')
    if request.method == "GET":
        return render_template("chat.html", username = session.get('username'))
    elif request.method == "POST":
        username = session.get("username")
        mess = request.values.get("message")
        if mess is None:
            return redirect("/")
        if len(mess) > 1000:
            return "The message is too long."
        if ':' in mess or ';' in mess:
            return "The message contains special characters."
        global message
        global messages
        message = str(message) + str(username) + ":" + str(mess) + ";"
        messages.append({"username": str(username), "message": str(mess)})
        db.set("message", message)
        return redirect("/chat")

@app.route('/api')
def api():
    return render_template("api.html", messages = messages)
