from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hasdasdasdawg"
socketio = SocketIO(app)

lobbies = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in lobbies:
            break
    return code

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

        lobby = code

        session["name"] = name

        # Create new lobby
        if create != False:
            return redirect(url_for("createLobby"))
        # Fail to join a lobby
        elif code not in lobbies:
            return render_template("home.html", error="Room does not exist", code=code, name=name)
        
        session["lobby"] = lobby

        return redirect(url_for("waitingLobby"))
    
    return render_template("home.html")

@app.route("/createLobby", methods=["POST", "GET"])
def createLobby():
    if request.method == "POST":
        numPlayers = int(request.form.get("numPlayers"))
        allianceOn = True if request.form.get("alliesOn") == "yes" else False

        # lobby created and stored in lobbies
        # a lobby is virtually created and identified by a 4-letter long code
        # the unique code serves as the channel number
        lobby = generate_unique_code(4)
        lobbies[lobby] = {"players": 0, "maxPlayer": numPlayers, "alliesAllowed": allianceOn, "pNames": []}

        session["lobby"] = lobby

        return redirect(url_for("waitingLobby"))
        
    return render_template("createLobby.html")

@app.route("/waitingLobby")
def waitingLobby():
    lobby = session.get("lobby")
    if lobby is None or session.get("name") is None or lobby not in lobbies:
        return redirect(url_for("home"))
    return render_template("waitingLobby.html", code=lobby, stats=lobbies[lobby])

@socketio.on('connect')
def connect(auth):
    name = session.get("name")
    lobby = session.get("lobby")
    if not lobby or not name:
        return
    if lobby not in lobbies:
        leave_room(lobby)
        return
    # Verified if max num of players reached
    if lobbies[lobby]["players"] >= lobbies[lobby]["maxPlayer"]:
        leave_room(lobby)
        return
    join_room(lobby)
    lobbies[lobby]["players"] += 1
    if name not in lobbies[lobby]["pNames"]:
        lobbies[lobby]["pNames"].append(name)

    socketio.emit('playerIn', lobbies[lobby]["pNames"])
    print(f"{name} joined lobby {lobby}")

@socketio.on('disconnect')
def disconnect():
    lobby = session.get("lobby")
    name = session.get("name")
    leave_room(lobby)
    
    if name in lobbies[lobby]["pNames"]:
        lobbies[lobby]["pNames"].remove(name)

    socketio.emit('playerOut', lobbies[lobby]["pNames"])
    print(f"{name} has left the room {lobby}")

    if lobby in lobbies:
        lobbies[lobby]["players"] -= 1
        if lobbies[lobby]["players"] <= 0:
            del lobbies[lobby]

@app.route("/gameWindow")
def gameWindow():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)