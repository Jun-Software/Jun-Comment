import redis
from flask import *
from datetime import timedelta
import os
from pysmx.SM3 import SM3

# Hash function
def sm3_hash(data: str):
    s = SM3()
    s.update(data)
    return str(s.hexdigest())

# Create server
app = Flask(__name__)

# Load envrion
redis_host = str(os.getenv("REDIS_HOST"))
redis_port = str(os.getenv("REDIS_PORT"))
redis_password = str(os.getenv("REDIS_PASSWORD"))

# Connect redis database
db = redis.Redis(host = redis_host,
                port = redis_port,
                password = redis_password,
                decode_responses = True)

# Load message data from redis database
messages = []
message = db.get("message")
if message is not None:
    message = message.split(";")
    message.remove('')
    for i in message:
        m = i.split(':')
        messages.append({'username': str(m[0]), 'message': str(m[1])})
else:
    message = ""


# The master page
@app.route("/")
def index():
    return redirect("/comment")
        
# The comment page
@app.route("/comment", methods = ["GET", "POST"])
def chat():
    if request.method == "GET":
        # If user is online, render the html page file.
        return render_template("comment.html", messages = messages)
    elif request.method == "POST":
        # Get "message" data from request for send message
        username = request.values.get("username")
        mess = request.values.get("message")
        if mess is None:
            return redirect("/")
        if len(mess) > 1000:
            return "The message is too long."
        if ':' in mess or ';' in mess:
            return "The message contains special characters."
        global message
        message = str(message) + str(username) + ":" + str(mess) + ";"
        messages.append({"username": str(username), "message": str(mess)})
        db.set("message", message)
        return redirect("/comment")
