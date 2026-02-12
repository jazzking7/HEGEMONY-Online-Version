from flask import Flask, render_template, request, session, redirect, url_for, make_response

app = Flask(__name__)
app.config["SECRET_KEY"] = "hasdasdasdawg"

def no_cache(view):
    """Decorator to add no-cache headers to a response."""
    def no_cache_decorator(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    no_cache_decorator.__name__ = view.__name__
    return no_cache_decorator

@app.route("/")
@no_cache
def main():
    return render_template('main.html')

@app.route("/main_menu")
def main_menu():
    return render_template("main_menu.html")

@app.route("/lobby")
def lobby():
    return render_template("lobby.html")

@app.route("/game")
def gameMap():
    return render_template('game.html')

@app.route("/roll_simulator")
def rollSimulator():
    return render_template('roll_simulator.html')

@app.route("/game_rules")
def game_rules():
    return render_template('game_rules.html')

@app.route("/tutorials")
def tutorials():
    return render_template('tutorials.html')

if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8080, debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)