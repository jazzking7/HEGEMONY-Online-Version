from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "hasdasdasdawg"

@app.route("/")
def main():
    return render_template('main.html')

@app.route("/main_menu")
def main_menu():
    return render_template("main_menu.html")

@app.route("/createLobby")
def createLobby():
    return render_template("createLobby.html")

@app.route("/gameLobby")
def gameLobby():
    return render_template("gameLobby.html")

@app.route("/changeSettings")
def changeSettings():
    return render_template("lobbySettings.html")

@app.route("/startGameBtn")
def startGameBtn():
    return render_template("startGameBtn.html")

@app.route("/gameMap")
def gameMap():
    return render_template('gameMap.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)