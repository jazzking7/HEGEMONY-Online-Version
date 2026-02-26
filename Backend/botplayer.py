import string
import random

class Botplayer:

    def __init__(self, G):
        # identity

        name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        name = "Player_" + name
        while name in G.player_names:
            name = "Player_" + ''.join(
                random.choices(string.ascii_letters + string.digits, k=5)
            )
        self.name = name
        G.player_names.append(name)
        # status
        self.alive = True
        self.aliveBefore = True

        self.connected = True # Keep track if the player is connected
        self.hijacked = False

        # skill
        self.skill = None
        # ownership
        self.territories = []
        self.capital = None   # Name of the capital
        # battle stats
        self.temp_stats = None   # determine after deployment stage to prevent infinite growth
        self.industrial = 6
        self.infrastructure = 3
        self.infrastructure_upgrade = 0
        self.min_roll = 1
        # hidden resources
        self.stars = 0
        self.reserves = 0
        self.s_city_amt = 0  # city amount to settle in innerAsync actions
        self.m_city_amt = 0  # megacity amount to settle in innerAsync actions
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
        # summit
        self.num_summit = 2
        self.num_global_cease = 1
        # status monitoringg
        self.total_troops = 0
        # Player Power Index
        self.PPI = 0
        # number of leylines controlled by player
        self.numLeylines = 0

        self.con_amt = 0    # keep counts of how many territories the player has conquered during a turn

        # keep track of how many exploration made
        self.land_explored = []
        self.sunken_cost = 0

        # 
        self.isBot = True