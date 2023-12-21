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

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)