from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send
from string import ascii_uppercase
from mission_distributor import *
from game_state_manager import *
from skill_distributor import *

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contains all lobbies
players = {}
lobbies = {}
SES = setup_event_scheduler()
MDIS = Mission_Distributor()
EGT = End_game_tracker()
SDIS = Skill_Distributor()

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
    sid = request.sid
    print('Client disconnected with socket ID:', sid)

    # Player not even connected to a lobby
    if not sid in players:
        return

    # Player is connected to a lobby
    username = players[sid]['username']
    lobby_id = players[sid]['lobby_id']
    
    # delete player and leave lobby
    del players[sid]
    leave_room(lobby_id)

    # get lobby if not none
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]

    # if game started, set player with sid to dead
    if lobby['game_started']:
        # disconnect user
        gsm = lobby['gsm']
        gsm.players[sid].connected = False
        gsm.server.emit('display_new_notification', {'msg': f'Player {gsm.players[sid].name} is disconnected.'}, room=gsm.lobby)

    # remove sid from lobby own list of players NOT FROM GSM
    lobby['players'].remove(sid)

    print(lobby)
    if len(lobby['players']) == 0:
        # check if game started
        if lobby['game_started']:
            gsm = lobby['gsm']
            # stop the game thread
            gsm.GES.halt_events()
        del lobbies[lobby_id]

        return
    
    if lobby['host'] == sid:
        lobby['host'] = random.choice(lobby['players'])
        socketio.emit('update_lobby', {"event": "change_host", "target": lobby['host']}, room=lobby_id)
    socketio.emit('update_lobby', {"event": "disconnect", "target": username}, room=lobby_id)


### Main menu functions ###

@socketio.on('create_lobby')
def createLobby(data):
    print('create_lobby', data)
    sid = request.sid
    username = data.get('username')
    print(f'{username} is creating a lobby')    # TODO delete me
    lobby_code = generate_unique_code(5)
    players[request.sid] = {
        'username': username,
        'lobby_id': lobby_code
    }
    join_room(lobby_code)
    # TODO populate lobbies dict better
    lobbies[lobby_code] = {
        'host': sid,
        'players': [sid],
        'game_started': False
    }
    socketio.emit('lobby_created', room=sid)

    print(lobbies)

@socketio.on('join_lobby')
def joinLobby(data):
    print('join_lobby', data)
    sid = request.sid
    username = data.get('username')
    lobby_code = data.get('lobby_code')

    # Check if lobby exists
    if lobby_code not in lobbies:
        print(f"ERROR: The lobby {lobby_code} does not exist!")
        socketio.emit('error', {'msg': "Invalid lobby code!"}, room=sid)
        return
    
    # Get lobby
    lobby = lobbies[lobby_code]

    # Update username if username is already taken
    for pid in lobby['players']:
        if players[pid]['username'] == username:
            username += "_"
    
    # Add player
    players[sid] = {
        'username': username,
        'lobby_id': lobby_code
    }

    # Add player to lobby
    lobby['players'].append(sid)
    join_room(lobby_code)

    # Game started
    if lobby['game_started']:
        
        # Find disconnected player to replace
        gsm = lobby['gsm']
        pid_to_takeover = None
        for pid in gsm.players:
            if not gsm.players[pid].connected:
                pid_to_takeover = pid
        # Verify if there is a player
        if not pid_to_takeover:
            socketio.emit('error', {'msg': "Lobby full!"}, room=sid)
        # Verify if turn started for the player
        if pid_to_takeover == gsm.pids[gsm.GES.current_player]:
            socketio.emit('error', {'msg': "Not a good timing to join in!"}, room=sid)
        # Verify if player dead
        if not gsm.players[pid_to_takeover].alive:
            socketio.emit('error', {'msg': "No available spots!"}, room=sid)

        # takeover disconnected player
        if gsm.takeover_disconnected_player(sid, pid_to_takeover, username):
            socketio.emit('join_lobby_game', room=sid)
            gsm.GES.update_all_views_for_reconnected_player(sid)

    else:
        # Update lobby info
        socketio.emit('update_lobby', {"event": "join", "target": username}, room=lobby_code)
        socketio.emit('lobby_joined', room=sid)

### Lobby functions ###

@socketio.on('get_lobby_data')
def get_lobby_data():
    sid = request.sid
    if sid not in players:
        return
    lobby_id = players[sid]['lobby_id']
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]
    lobby_players = []
    for player_sid in lobby['players']:
        lobby_players.append(players[player_sid]['username'])
    out_data = {
        'host': lobby['host'],
        'lobby_id': lobby_id,
        'players': lobby_players
    }
    socketio.emit('lobby_data', out_data, room=sid)

@socketio.on('start_game')
def startGame(data):
    sid = request.sid
    lobby_id = players[sid]['lobby_id']
    lobby = lobbies[lobby_id]

    # Safeguard
    if lobby['host'] != sid:
        socketio.emit('error', {'msg': "Only the host can start the game!"}, room=sid)
        return
    if len(lobby['players']) < 1:   # TODO testing only - setup a constant
        socketio.emit('error', {'msg': "Not enough players!"}, room=sid)
        return
    
    # Setup lobby settings ## TO BE UPDATED
    lobby['game_started'] = True
    lobby['alliance'] = data.get('alliance')
    lobby['turn_time'] = int(data.get('turn_time'))
    lobby['setup_mode'] = "all_manuel"
    print(lobby)

    # TEMP START GAME SEQUENCE | FOR TESTING ONLY
    lobby['waitlist'] = []
    lobby['map_name'] = '88world' # MAP NAME
    player_list = [{'sid': pid, 'name': players[pid]['username']} for pid in lobby['players'] ]
    lobby['gsm'] = Game_State_Manager(lobby['map_name'], player_list, SES.get_event_scheduler(lobby['setup_mode']), socketio, lobby_id)
    lobby['gsm'].Mdist = MDIS
    lobby['gsm'].egt = EGT
    lobby['gsm'].SDIS = SDIS

    socketio.emit('game_started', room=lobby_id)

    # MAIN ENTRY POINT
    lobby['gsm'].GES.main_flow.start()
    print("GAME LAUNCHED")

### Game functions ###

## SET UP 
@socketio.on('get_game_settings')
def get_game_settings():
    sid = request.sid
    if sid not in players:
        return
    lobby_id = players[sid]['lobby_id']
    if lobby_id is None:
        return
    lobby = lobbies[lobby_id]
    lobby_map = lobby['gsm'].map
    # FILL IN MAP CHOSEN
    socketio.emit('game_settings',
     {'map': lobby['map_name'], 
    'tnames': lobby_map.tnames, 
    'tneighbors': lobby_map.tneighbors,
    'landlocked': lobby_map.landlocked}, room=sid)

@socketio.on('send_color_choice')
def update_color_choice(data):
    color = data.get('choice')
    gsm = lobbies[players[request.sid]['lobby_id']]['gsm']
    if color not in gsm.made_choices:
        gsm.made_choices.append(color)
        gsm.aval_choices.remove(color)
        socketio.emit('color_picked', {'option': color}, room=players[request.sid]['lobby_id'])
        socketio.emit('clear_view', room=request.sid)
        # CM
        gsm.players[request.sid].color = color
        gsm.GES.selected += 1
    else:
        socketio.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': gsm.aval_choices}, room=request.sid)

@socketio.on('send_dist_choice')
def update_dist_choice(data):
    dist = data.get('choice')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].territories = gsm.aval_choices[dist]
    del gsm.aval_choices[dist]
    # CM
    socketio.emit('update_player_territories', {'list': gsm.players[pid].territories}, room=pid)
    for trty in gsm.players[pid].territories:
        socketio.emit('update_trty_display', {trty: {'color': gsm.players[pid].color, 'troops': 1}}, room=gsm.lobby)
    gsm.GES.selected += 1

@socketio.on('send_capital_choice')
def update_player_capital(data):
    tid = data.get('tid')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if tid in gsm.players[pid].territories:
        # CM
        gsm.players[pid].capital = gsm.map.territories[tid].name
        gsm.map.territories[tid].isCapital = True
        socketio.emit('update_trty_display', {tid: {'isCapital': True, 'capital_color': gsm.players[pid].color}}, room=gsm.lobby)
        socketio.emit('settle_result', {'resp': True}, room=pid)
        gsm.GES.selected += 1
        return
    socketio.emit('settle_result', {'resp': False}, room=pid)

@socketio.on('send_city_choices')
def update_player_city(data):
    choices = data.get('choice')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for c in choices:
        if c not in gsm.players[pid].territories:
            socketio.emit('settle_result', {'resp': False}, room=pid)
            return
    # CM
    for trty in choices:
        gsm.map.territories[trty].isCity = True
        socketio.emit('update_trty_display', {trty: {'hasDev': 'city'}}, room=gsm.lobby)
    gsm.GES.selected += 1
    socketio.emit('settle_result', {'resp': True}, room=pid)

@socketio.on('settle_cities')
def settle_new_cities(data):
    choices = data.get('choice')
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for trty in choices:
        if gsm.map.territories[trty].isCity:
            socketio.emit('update_settle_status', {'msg':'EXISTING CITY AMONG CHOSEN TERRITORIES!'}, room=pid)
            return
        if gsm.map.territories[trty].isDeadZone:
            socketio.emit('update_settle_status', {'msg':'CANNOT BUILD ON RADIOACTIVE ZONE!'}, room=pid)
            return
        
    if gsm.in_ice_age:
        if gsm.players[pid].skill:
            if gsm.players[pid].skill.name != 'Realm_of_Permafrost':
                return
            elif not gsm.players[pid].skill.active:
                return

    # CM
    for trty in choices:
        gsm.map.territories[trty].isCity = True
        socketio.emit('update_trty_display', {trty: {'hasDev': 'city'}}, room=gsm.lobby)

    gsm.update_TIP(pid)
    gsm.get_SUP()
    gsm.update_global_status()
    gsm.signal_MTrackers('indus')

    gsm.players[pid].s_city_amt = 0
    gsm.players[pid].stars -= len(choices)*3
    gsm.update_private_status(pid)

@socketio.on('send_troop_update')
def update_troop_info(data):
    choice = data.get('choice')
    amount = int(data.get('amount'))
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if choice not in gsm.players[pid].territories:
        socketio.emit('troop_result', {'resp': False}, room=pid)
        return
    t = gsm.map.territories[choice]
    t.troops += amount
    gsm.players[pid].total_troops += amount
    gsm.players[pid].deployable_amt -= amount
    print(f"Player has {gsm.players[pid].deployable_amt } deployable amount")
    # CM
    socketio.emit('troop_addition_display', {
                            f'{choice}': {'tid': choice, 'number': amount},
                        }, room=gsm.lobby)
    socketio.emit('update_trty_display',{choice:{'troops':t.troops}}, room=gsm.lobby)
    gsm.update_LAO(pid)

    gsm.update_player_stats()
    gsm.get_SUP()
    gsm.update_global_status()

    gsm.signal_MTrackers('popu')

    if gsm.players[pid].deployable_amt > 0:
        socketio.emit('troop_deployment', {'amount': gsm.players[pid].deployable_amt}, room=pid)
    else:
        if gsm.GES.current_event == None:
            # show only for initial deployment
            socketio.emit('troop_result', {'resp': True}, room=pid)
            gsm.GES.selected += 1

@socketio.on('send_skill_choice')
def update_skill_choice(data):
    skill = data.get('choice')
    gsm = lobbies[players[request.sid]['lobby_id']]['gsm']
    # initiate skill
    gsm.players[request.sid].skill = gsm.SDIS.initiate_skill(skill, request.sid, gsm)
    # CM
    gsm.GES.selected += 1
    return

@socketio.on('send_battle_data')
def handle_battle(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.handle_battle(data)
    return

@socketio.on("get_reachable_trty")
def get_reachable_trty(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    reachable_trty = gsm.map.get_reachable_trty(data['choice'], gsm.players[pid].territories)
    socketio.emit('update_clickables', {'trtys': reachable_trty}, room=pid)

@socketio.on("terminate_conquer_stage")
def terminate_conquer_stage():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.GES.stage_completed = True

@socketio.on("terminate_rearrangement_stage")
def terminate_rearrangement_stage():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.GES.stage_completed = True

@socketio.on('send_rearrange_data')
def handle_rearrange_data(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    choices = data['choice']
    amount = int(data['amount'])
    t1 = gsm.map.territories[choices[0]]
    t2 = gsm.map.territories[choices[1]]
    t1.troops -= amount
    t2.troops += amount
    # CM
    socketio.emit('update_trty_display', {
        choices[0]: {'troops': t1.troops},
        choices[1]: {'troops': t2.troops}
    } , room=gsm.lobby)

@socketio.on('get_sep_auth')
def send_sep_auth():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    socketio.emit('receive_sep_auth', {'amt': gsm.players[pid].stars}, room=pid)

@socketio.on('get_reserves_amt')
def send_reserves_amt():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    socketio.emit('receive_reserves_amt', {'amt': gsm.players[pid].reserves}, room=pid)

@socketio.on("convert_reserves")
def convert_reserves(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        gsm.convert_reserves(int(data['amt']), pid)
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot convert reserves outside of your turn!'}, room=pid)
        socketio.emit('signal_show_btns', room=pid)

@socketio.on('upgrade_infrastructure')
def upgrade_infrastructure(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        gsm.upgrade_infrastructure(int(data['amt']), pid)
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot upgrade infrastructure outside of your turn!'}, room=pid)
        socketio.emit('signal_show_btns', room=pid)

@socketio.on('send_reserves_deployed')
def handle_reserves_deployment(data):
    choice = data['choice']
    amount = int(data['amount'])
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    t = gsm.map.territories[choice]
    t.troops += amount
    gsm.players[pid].total_troops += amount
    gsm.players[pid].reserves -= amount
    # CM
    socketio.emit('troop_addition_display', {
                            f'{choice}': {'tid': choice, 'number': amount},
                        }, room=gsm.lobby)
    socketio.emit('update_trty_display',{choice:{'troops':t.troops}}, room=gsm.lobby)
    gsm.update_LAO(pid)
    gsm.update_private_status(pid)

    gsm.update_player_stats()
    gsm.get_SUP()
    gsm.update_global_status()
    
    gsm.signal_MTrackers('popu')

    if gsm.players[pid].reserves > 0:
        socketio.emit('reserve_deployment', {'amount': gsm.players[pid].reserves}, room=pid)

@socketio.on('request_summit')
def handle_summit_request():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        if gsm.players[pid].num_summit > 0:
            gsm.GES.summit_requested = True
        else:
            socketio.emit('summit_failed', {'msg': "MAX AMOUNT OF SUMMIT LAUNCHED!"} ,room=pid)
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot launch summit outside of your turn!'}, room=pid)

@socketio.on('request_global_peace')
def handle_global_peace_request():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        if gsm.players[pid].num_summit > 0:
            gsm.GES.global_peace_proposed = True
        else:
            socketio.emit('summit_failed', {'msg': "MAX AMOUNT OF GLOBAL PEACE PROPOSED!"} ,room=pid)
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot launch summit outside of your turn!'}, room=pid)

@socketio.on('send_summit_choice')
def handle_summit_choice(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    opt = data['choice']
    if opt == 'y':
        gsm.GES.summit_voter['y'] += 1
    elif opt == 'n':
        gsm.GES.summit_voter['n'] += 1
    socketio.emit('s_voting_fb', {'opt': opt, 'name': gsm.players[pid].name}, room=gsm.lobby)
    gsm.GES.selected += 1

# ENTRY POINT FOR INNER ASYNC EVENTS
@socketio.on('send_async_event')
def handle_async_event(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        gsm.GES.handle_async_event(data, pid)
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot perform special operation outside of your turn!'}, room=pid)
        socketio.emit('signal_show_btns', room=pid)

# EXIT POINT FOR INNER ASYNC EVENTS
@socketio.on('signal_async_end')
def handle_async_end():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.GES.innerInterrupt = False
    print(f"{gsm.players[pid].name} has signal to end async action.")
    return

@socketio.on('add_click_sync')
def handle_add_click_sync(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for p in gsm.players:
        if p != pid:
            socketio.emit('add_tid_to_otherHighlight', data, room=p)

@socketio.on('remove_click_sync')
def handle_remove_click_sync(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for p in gsm.players:
        if p != pid:
            socketio.emit('remove_tid_from_otherHighlight', data, room=p)

@socketio.on('clear_otherHighlights')
def handle_clear_click_sync():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    for p in gsm.players:
        if p != pid:
            socketio.emit('clear_otherHighlight', room=p)

@socketio.on('get_skill_information')
def send_skill_information():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if gsm.players[pid].skill:
        gsm.players[pid].skill.update_current_status()

@socketio.on('signal_skill_usage')
def handle_skill_usage():
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    if pid == gsm.pids[gsm.GES.current_player]:
        if gsm.players[pid].skill:
            gsm.players[pid].skill.activate_effect()
    else:
        socketio.emit('display_new_notification',{'msg': 'Cannot activate skill outside your turn!'}, room=pid)

@socketio.on('build_free_cities')
def build_free_cities(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].skill.validate_and_apply_changes(data)

@socketio.on("strike_targets")
def strike_targets(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].skill.validate_and_apply_changes(data)

@socketio.on("send_battle_stats_AS")
def perform_paratrooper_attack(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].skill.validate_and_apply_changes(data)

@socketio.on('get_reachable_airspace')
def get_reachable_airspace(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    socketio.emit('receive_reachable_airspace', {'spaces': gsm.map.get_reachable_airspace(data['origin'])})

@socketio.on('send_corrupt_territory')
def handle_corrupt_territory(data):
    pid = request.sid
    gsm = lobbies[players[pid]['lobby_id']]['gsm']
    gsm.players[pid].skill.validate_and_apply_changes(data)

if __name__ == '__main__':
    # socketio.run(app, host='127.0.0.1', port=8081, debug=True)
    socketio.run(app, host='0.0.0.0', port=8081, debug=True)
