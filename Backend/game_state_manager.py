# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
from game_map import *

class Player:

    def __init__(self, name, sid, G):
        # identity
        self.name = name
        self.sid = sid
        # status
        self.alive = True
        # agenda
        self.mission = None
        # skill
        self.hasSkill = False
        self.skill = None
        # ownership
        self.territories = []
        self.capital = None
        # battle stats
        self.industrial = 6
        self.infrastructure = 3
        self.infrastructure_upgrade = 0
        # hidden resources
        self.stars = 0
        self.reserves = 0
        # alliance
        self.hasAllies = False
        self.allies = []
        self.ally_socket = None
        # turn
        self.conquered = False
        self.game = G
        # visuals
        self.color = None
        self.insignia = None
        # puppet state
        self.puppet = False
        self.master = None
        self.vassals = []
        # economy
        self.cumulative_gdp = 0

class Event:
    def __init__(self, name, event, duration):
        self.name = name
        self.event = event
        self.event_duration = duration

class Game_State_Manager:

    def __init__(self, mapName, player_list, events):

        # Number of players and players are related
        self.player_list = player_list

        # Map
        self.map = Map(mapName)
        self.total_troops = len(self.map.territories)

        # turn counter
        self.turn = 0
        self.stage = 0

        # max number of allies allowed in an alliance
        self.max_allies = 2
        
        # loop elements update on async
        self.curr_reinforcer = None
        self.curr_conqueror = None
        
        # EVENT SCHEDULERS
        self.round = 0
        self.current_event = None
        self.events = []
        for event in events

    def distribute_missions():
            lobby = lobbies[ players[request.sid]['lobby_id'] ]
            if request.sid not in lobby['waitlist']:
                lobby['waitlist'].append(request.sid)
                print(request.sid, " ready to play")
            if len(lobby['waitlist']) == len(lobby['players']):
                print("Mission Sent")
                for player in lobby['waitlist']:
                    continents = ['Pannotia', 'Zealandia', 'Baltica', 'Rodinia', 'Kenorland', 'Kalahari']
                    socketio.emit('get_mission', {'msg': f'Mission: capture {random.choice(continents)}'}, room=player)
                lobby['waitlist'] = []

    def start_color_distribution():
        lobby = lobbies[ players[request.sid]['lobby_id'] ]
        if request.sid not in lobby['waitlist']:
            lobby['waitlist'].append(request.sid)
            print(request.sid, " ready to choose")
        if len(lobby['waitlist']) == len(lobby['players']):
            time.sleep(10)
            with open('Setting_Options/colorOptions.json') as file:
                color_options = json.load(file)
            for player in lobby['waitlist']:
                socketio.emit('choose_color', {'msg': 'Choose a color to represent your country', 'options': color_options}, room=player)
            lobby['waitlist'] = []
    
    def start_territorial_distribution():
        return
    
    def start_capital_settlement():
        return
    
    def start_city_settlement():
        return
    
    def start_initial_deployment():
        return
    
    def start_skill_choosing():
        return