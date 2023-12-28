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

@socketio.on('updateLobbyInfo')
def updateLobbyInfo(data):
    lobby_code = data.get('lobby')
    socketio.emit('gameLobby', {**lobbies[lobby_code], **{'isHost': request.sid == lobbies[lobby_code]['host']}}, room=request.sid)

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
    lobby['player_sids'][username] = request.sid
    lobby['numPlayersIn'] += 1
    print(lobby)
    socketio.emit('updateLobbyInfo', {"lobby": lobby_code}, room=lobby_code)

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
        'player_sids': {data.get('username'): request.sid},
        'maxPlayers': int(data.get('maxPlayers')),
        'numPlayersIn': 1,
        'allianceOn': allianceOn}
    print(lobbies[lobby_code])
    join_room(lobby_code)
    socketio.emit('updateLobbyInfo', {"lobby": lobby_code}, room=lobby_code)

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
    socketio.emit('updateLobbyInfo', {"lobby": lobby_code}, room=lobby_code)

@socketio.on('START_GAME')
def startGame(data):
    lobby_code = data.get('lobby')
    lobby = lobbies[lobby_code]
    if lobby['numPlayersIn'] < 5:
        socketio.emit('errorPopup', {'msg': "Not enough players!"}, room=lobby['host'])
        return
    # BACKEND GAME START SEQUENCES
    socketio.emit('gameView', data, room=lobby_code)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
