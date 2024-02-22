# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
from game_map import *
from event_scheduler import *

class Player:

    def __init__(self, name, G):
        # identity
        self.name = name
        # status
        self.alive = True
        # agenda
        self.mission = None
        # skill
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
        # deployment
        self.deployable_amt = 0
        # economy
        self.cumulative_gdp = 0

class Game_State_Manager:

    def __init__(self, mapName, player_list, setup_events, server, lobby):

        # Number of players and players are related
        self.players = {}
        self.pids = []
        for player in player_list:
            self.pids.append(player['sid'])
            self.players[player['sid']] = Player(player['name'], self)

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
        
        # SELECTION TRACKER
        self.aval_choices = []
        self.made_choices = []
        self.selected = True

        # color options
        self.color_options = []
        # skill options
        self.skill_options = [
            "Sturdy_As_Steel",
            "Usurper",
            "Air_Superiority",
            "Divine_Punishment",
            "Industrial_Revolution",
            "Zealous_Expansion",
            "Mass_Mobilization",
            "Handler_of_Wheel_of_Fortune",
            "Laplace_Demon",
            "Necromancer",
            "Ares_Blessing",
            "Dictator"
        ]

        # server
        self.server = server
        self.lobby = lobby

        # EVENT SCHEDULERS
        self.setup_scheduler = setup_events
        self.turn_loop_scheduler = turn_loop_scheduler()
    
    def run_setup_events(self,):
        time.sleep(3)
        for event in self.setup_scheduler:
            event.executable(self)
    
    def run_turn_scheduler(self,):
        self.turn_loop_scheduler.run_turn_loop(self)

    def shuffle_players(self, ):
        random.shuffle(self.pids)
        shuffled_dict = {key: self.players[key] for key in self.pids}
        self.players = shuffled_dict
        for player in self.players:
            self.server.emit('update_player_info', room=player)

    def signal_view_clear(self,):
        for player in self.players:
            self.server.emit('clear_view', room=player)

    def get_deployable_amt(self, player):
        bonus = 0
        t_score = 0
        p = self.players[player]
        for trty in p.territories:
            t = self.map.get_trty(trty)
            if t.isCapital:
                bonus += 1
            if t.isCity:
                t_score += 2
            if t.isMegacity:
                bonus += 1
            if t.isTransportcenter:
                bonus += 2
            t_score += 1
        bonus += self.map.get_continental_bonus(p.territories)
        if t_score < 9:
            return bonus + 3
        return bonus + t_score//3

