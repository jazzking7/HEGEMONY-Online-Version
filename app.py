from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hasdasdasdawg"
socketio = SocketIO(app)

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)
        if join != False and not code:
            return render_template("home.html", error="Please enter a lobby code.", code=code, name=name)
        room = code
        if create != False:
            return redirect(url_for("gameWindow"))
    return render_template("home.html")

@app.route("/gameWindow")
def gameWindow():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)