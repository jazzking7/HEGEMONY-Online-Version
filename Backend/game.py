# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
from map import *

class Player:

    def __init__(self, name, sid, G):
        self.name = name
        self.mission = None
        self.territories = []
        self.industrial = 6
        self.infrastructure = 3
        self.infrastructure_upgrade = 0
        self.stars = 0
        self.reserves = 0
        self.skill = None
        self.hasAllies = False
        self.allies = []
        self.ally_socket = None
        self.alive = True
        self.capital = None
        self.conquered = False
        self.game = G
        self.sid = sid
        # visuals
        self.color = None
        self.insignia = None
        # skills
        self.hasSkill = False
        self.skill = None
        # puppet state
        self.puppet = False
        self.master = None
        self.vassals = []
        # economy
        self.cumulative_gdp = 0

class Game:

    def __init__(self, mapName, player_list):
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
        # for skills
        self.round = 0

g = Game("MichaelMap1", ["player1", "player2"])
print(g.map.conts)
