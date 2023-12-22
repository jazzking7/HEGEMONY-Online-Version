from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contains all lobbies
lobbies = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in lobbies:
            break
    return code

@socketio.on('connect')
def connect(auth):
    print('Client connected with socket ID:', request.sid)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected with socket ID:', request.sid)

@socketio.on('joinLobby')
def joinLobby(data):
    lobby_code = data.get('lobby_code')
    username = data.get('username')
    if lobby_code not in lobbies:
        print(f"ERROR: The lobby {lobby_code} does not exist!")
        socketio.emit('errorPopup', {'msg': "Invalid lobby code!"}, room=request.sid)
        return
    lobby = lobbies[lobby_code]
    if lobby['numPlayersIn'] + 1 > lobby['maxPlayers']:
        print(f"ERROR: The lobby {lobby_code} is full!")
        socketio.emit('errorPopup', {'msg': "The lobby is full!"}, room=request.sid)
        return
    if username in lobby['players']:
        username += "_|"
    join_room(lobby_code)
    lobby['players'].append(username)
    lobby['numPlayersIn'] += 1
    socketio.emit('gameLobby', lobbies[lobby_code], room=lobby_code)

@socketio.on('createLobby')
def createLobby(data):
    print(f'{data.get("username")} is creating a lobby')
    socketio.emit('createLobby', data, room=request.sid)

@socketio.on('lobbyCreation')
def lobbyCreation(data):
    print(data)
    allianceOn = data.get('allianceOn') == "yes"
    # Create lobby
    lobby_code = generate_unique_code(5)
    lobbies[lobby_code] = {
        'lobby_code': lobby_code,
        'host': request.sid,
        'players': [data.get('username')],
        'maxPlayers': int(data.get('maxPlayers')),
        'numPlayersIn': 1,
        'allianceOn': allianceOn}
    join_room(lobby_code)
    socketio.emit('gameLobby', lobbies[lobby_code], room=lobby_code)
    # Display setting panel to host only
    socketio.emit('lobbySettings', {'lobby': lobby_code}, room=lobbies[lobby_code]['host'])

@socketio.on('changeSettings')
def changeSettings(data):
    lobby_code = data.get('lobby')
    lobby = lobbies[lobby_code]
    numP = int(data.get('numPlayers'))
    ally = data.get('allianceMode') == "yes"
    if numP < lobby['numPlayersIn']:
        socketio.emit('errorPopup', {'msg': "Invalid player number!"}, room=lobby['host'])
        return
    lobby['maxPlayers'] = numP
    lobby['allianceOn'] = ally
    socketio.emit('gameLobby', lobbies[lobby_code], room=lobby_code)
    # Display setting panel to host only
    socketio.emit('lobbySettings', {'lobby': lobby_code}, room=lobbies[lobby_code]['host'])


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
