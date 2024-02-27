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
        self.temp_stats = None
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

    def get_player_industrial_level(self, player):
        lvl = 0
        c_amt = self.map.count_cities(player.territories)
        if c_amt == 3:
            lvl += 1
        elif c_amt > 3:
            lvl += 1 + (c_amt-3)//2
        for trty in self.map.territories:
            if trty.name in player.territories and trty.isMegacity:
                lvl += 1
        return lvl

    def get_player_infra_level(self, player):
        lvl = 0
        for trty in self.map.territories:
            if trty in player.territories and trty.isTransportcenter:
                lvl += 1
        lvl += player.infrastructure_upgrade
        return lvl

    def get_player_battle_stats(self, player):

        # get industrial level
        stats = []
        stats.append(self.get_player_industrial_level(player)+6)
        stats.append(self.get_player_infra_level(player)+3)
        return stats

    def handle_battle(self, data):
        # Load territories involved
        t1, t2 = data['choice']
        
        # Identify opponents
        atk_p, def_p, a_pid, d_pid = None, None, None, None

        # TEMP TO BE ADJUSTED WHEN IN ALLIANCE
        for player in self.players:
            if t1 in self.players[player].territories:
                atk_p = self.players[player]
                a_pid = player
            if t2 in self.players[player].territories:
                def_p = self.players[player]
                d_pid = player       

        # Identify territories
        trty_atk = self.map.get_trty(t1)
        trty_def = self.map.get_trty(t2)

        # Compute participating forces
        atk_amt = int(data['amount'])
        def_amt = trty_def.troops

        # Compute player battle stats
        atk_stats = atk_p.temp_stats
        def_stats = self.get_player_battle_stats(def_p)

        # Simulate battle and get result
        result = self.simulate_attack(atk_amt, def_amt, atk_stats, def_stats)

        # Remove troops from attacking territory
        trty_atk.troops -= atk_amt
        self.server.emit('update_trty_display', {t1:{'troops': trty_atk.troops}}, room=self.lobby)
        
        # attacker wins
        if result[0] > 0:

            trty_def.troops = result[0]
            self.server.emit('update_trty_display', {t2:{'troops': trty_def.troops}}, room=self.lobby)

            atk_p.territories.append(t2)
            self.server.emit('update_player_list', {'list': atk_p.territories}, room=a_pid)
            self.server.emit('update_trty_display', {t2:{'color': atk_p.color}}, room=self.lobby)
            def_p.territories.remove(t2)
            self.server.emit('update_player_list', {'list': def_p.territories}, room=d_pid)

        # defender wins
        else:

            trty_def.troops = result[1]
            self.server.emit('update_trty_display', {t2:{'troops': trty_def.troops}}, room=self.lobby)

        

    def simulate_attack(self, atk_amt, def_amt, atk_stats, def_stats):
        
        # Troop amount
        a_troops = atk_amt
        d_troops = def_amt

        # Max stats
        a_maxv, a_maxt = atk_stats[0], atk_stats[1]
        d_maxv, d_maxt = def_stats[0], def_stats[1] - 1

        # Adjust stats
        a_maxt = a_troops if a_troops < a_maxt else a_maxt
        d_maxt = d_troops if d_troops < d_maxt else d_maxt

        print(a_troops, d_troops)

        # Starts simulation
        while(a_troops > 0 and d_troops > 0):

            a_rolls = sorted([random.randint(1, a_maxv) for _ in range(a_maxt)], reverse=True)
            d_rolls = sorted([random.randint(1, d_maxv) for _ in range(d_maxt)], reverse=True)

            max_dmg = len(d_rolls) if len(d_rolls) < len(a_rolls) else len(a_rolls)

            for i in range(max_dmg):
                if a_rolls[i] > d_rolls[i]:
                    d_troops -= 1
                else:
                    a_troops -= 1
            
            a_maxt = a_troops if a_troops < a_maxt else a_maxt
            d_maxt = d_troops if d_troops < d_maxt else d_maxt

            print(a_rolls, d_rolls)
            print(a_troops, d_troops)

        return [a_troops, d_troops]

