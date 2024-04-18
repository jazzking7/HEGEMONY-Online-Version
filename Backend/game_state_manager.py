# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
from game_map import *
from general_event_scheduler import *
from elimination_tracker import *
from end_game_tracker import *

class Player:

    def __init__(self, name, G):
        # identity
        self.name = name
        # status
        self.alive = True
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
        self.stars = 9
        self.reserves = 0
        self.s_city_amt = 0
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
        # status monitoringg
        self.total_troops = 0

class Game_State_Manager:

    def __init__(self, mapName, player_list, setup_events, server, lobby):

        # Number of players and players are related
        self.players = {}
        self.pids = []
        self.oriPlayers = []
        for player in player_list:
            self.pids.append(player['sid'])
            self.oriPlayers.append(player['sid'])
            self.players[player['sid']] = Player(player['name'], self)
        
        # Map
        self.map = Map(mapName)
        self.total_troops = len(self.map.territories)

        # turn victory (for special authority acquisition)
        self.turn_victory = False

        # max number of allies allowed in an alliance
        self.max_allies = 2
        
        # SELECTION TRACKER
        self.aval_choices = []
        self.made_choices = []

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

        # EVENT SCHEDULER
        self.GES = General_Event_Scheduler(self, setup_events)

        # Mission
        self.Mdist = None
        self.MTrackers = {}

        # Elimination Tracker
        self.et = Elimination_tracker()
        # End game tracker
        self.egt = End_game_tracker()

        # Global status
        self.LAO = None
        self.MTO = None
        self.HIP = None
        self.TIP = None
        self.SUP = None

        # monitoring
        self.perm_elims = []
        self.miss_elims = []
        self.kill_logs = {}

    def signal_MTrackers(self, event_name):
        if event_name in self.MTrackers:
            self.MTrackers[event_name].event.set()

    def get_LAO(self,):
        LAO = None
        h_score = -100
        for p in self.players:
            if self.players[p].total_troops > h_score:
                h_score = self.players[p].total_troops
                LAO = p
            elif self.players[p].total_troops == h_score:
                LAO = None
        self.LAO = LAO
    
    def update_LAO(self, p):
        if self.LAO == None:
            self.get_LAO()
        else:
            if self.LAO != p:
                if self.players[p].total_troops > self.players[self.LAO].total_troops:
                    self.LAO = p
                elif self.players[p].total_troops == self.players[self.LAO].total_troops:
                    self.LAO = None
    
    def get_MTO(self,):
        MTO = None
        h_score = -100
        for p in self.players:
            if len(self.players[p].territories) > h_score:
                h_score = len(self.players[p].territories)
                MTO = p
            elif len(self.players[p].territories) == h_score:
                MTO = None
        self.MTO = MTO
    
    def update_MTO(self, p):
        if self.MTO == None:
            self.get_MTO()
        else:
            if self.MTO != p:
                if len(self.players[p].territories)  > len(self.players[self.MTO].territories):
                    self.MTO = p
                elif len(self.players[p].territories) == len(self.players[self.MTO].territories):
                    self.MTO = None

    def get_HIP(self, ):
        HIP = None
        h_score = -100
        for p in self.players:
            if self.players[p].alive:
                curri = self.get_player_infra_level(self.players[p])
                if curri > h_score:
                    h_score = curri
                    HIP = p
                elif curri == h_score:
                    HIP = None
        self.HIP = HIP

    def update_HIP(self, p):
        if self.HIP == None:
            self.get_HIP()
        else:
            if self.HIP != p:
                if self.players[self.HIP].alive and self.players[p].alive:
                    pi = self.get_player_infra_level(self.players[p])
                    hi = self.get_player_infra_level(self.players[self.HIP])
                    if pi  > hi:
                        self.HIP = p
                    elif pi == hi:
                        self.HIP = None
                else:
                    self.get_HIP()

    def get_TIP(self, ):
        TIP = None
        h_score = -100
        for p in self.players:
            curri = self.get_player_industrial_level(self.players[p])
            if curri > h_score:
                h_score = curri
                TIP = p
            elif curri == h_score:
                TIP = None
        self.TIP = TIP
    
    def update_TIP(self, p):
        if self.TIP == None:
            self.get_TIP()
        else:
            if self.TIP != p:
                pi = self.get_player_industrial_level(self.players[p])
                hi = self.get_player_industrial_level(self.players[self.TIP])
                if pi > hi:
                    self.TIP = p
                elif pi == hi:
                    self.TIP = None
    
    def get_SUP(self,):
        l = [self.LAO, self.MTO, self.HIP, self.TIP]
        for p in l:
            if l.count(p) >= 3:
                self.SUP = p
                return
        self.SUP = None

    def update_global_status(self, ):
        self.server.emit('update_global_status',
        {'LAO': self.players[self.LAO].name if self.LAO != None else "Yet to exist",
        'MTO': self.players[self.MTO].name if self.MTO != None else "Yet to exist",
        'TIP': self.players[self.TIP].name if self.TIP != None else "Yet to exist",
        'SUP': self.players[self.SUP].name if self.SUP != None else "Yet to exist",}, room=self.lobby)

    def convert_reserves(self, amt, player):
        extra = 0
        if amt == 2:
            extra = 3
        elif amt == 3:
            extra = 4
        elif amt == 4:
            extra = 7
        elif amt == 5:
            extra = 10
        elif amt == 6:
            extra = 13
        elif amt == 7:
            extra = 17
        elif amt == 8:
            extra = 21
        elif amt == 9:
            extra = 25
        elif amt == 10:
            extra = 30
        elif amt == 11:
            extra = 34
        elif amt == 12:
            extra = 39
        elif amt == 13:
            extra = 46
        elif amt == 14:
            extra = 53
        elif amt == 15:
            extra = 60
        self.players[player].reserves += extra
        self.players[player].stars -= amt

    def get_total_troops_of_player(self, player):
        player = self.players[player]
        total = 0
        for t in player.territories:
            total += self.map.territories[t].troops
        player.total_troops = total
        return total

    def send_player_list(self, ):
        data = {}
        for pid in self.pids:
            data[self.players[pid].name] = {
                'troops': self.get_total_troops_of_player(pid),
                'trtys': len(self.players[pid].territories),
                'color': self.players[pid].color
            }
        self.server.emit('get_players_stats', data, room=self.lobby)
    
    def update_player_stats(self, pid):
        data = {
            'name': self.players[pid].name,
            'troops': self.players[pid].total_troops,
            'trtys': len(self.players[pid].territories)
        }
        self.server.emit('update_players_stats', data, room=self.lobby)

    def shuffle_players(self, ):
        random.shuffle(self.pids)
        shuffled_dict = {key: self.players[key] for key in self.pids}
        self.players = shuffled_dict

    def signal_view_clear(self,):
        for player in self.players:
            self.server.emit('clear_view', room=player)

    def upgrade_infrastructure(self, amt, player):
        # CM
        self.players[player].infrastructure_upgrade += amt
        self.players[player].stars -= amt*4
        self.update_HIP(player)
        self.get_SUP()
        self.update_global_status()
        self.signal_MTrackers('popu')

    def get_deployable_amt(self, player):
        bonus = 0
        t_score = 0
        p = self.players[player]
        for trty in p.territories:
            t = self.map.territories[trty]
            if t.isCapital:
                bonus += 1
            if t.isCity:
                t_score += 1
            if t.isMegacity:
                bonus += 1
            if t.isTransportcenter:
                bonus += 2
            t_score += 1
        bonus += self.map.get_continental_bonus(p.territories)
        if t_score < 9:
            return bonus + 3
        return bonus + t_score//3

    def clear_deployables(self, player):
        p =  self.players[player]
        if p.deployable_amt > 0:
            # CM
            while (p.deployable_amt != 0):
                trty = random.choice(p.territories)
                t = self.map.territories[trty]
                t.troops += 1
                p.total_troops += 1
                p.deployable_amt -= 1
                self.server.emit('update_trty_display', {trty:{'troops': t.troops}}, room=self.lobby)
            self.update_LAO(player)
            self.get_SUP()
            self.update_global_status()
            self.update_player_stats(player)
            self.signal_MTrackers('popu')

    def get_player_industrial_level(self, player):
        lvl = 0
        c_amt = self.map.count_cities(player.territories)
        if c_amt == 3:
            lvl += 1
        elif c_amt > 3:
            lvl += 1 + (c_amt-3)//2
        for trty in player.territories:
            if self.map.territories[trty].isMegacity:
                lvl += 1
        return lvl

    def get_player_infra_level(self, player):
        lvl = 0
        for trty in player.territories:
            if self.map.territories[trty].isTransportcenter:
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
        trty_atk = self.map.territories[t1]
        trty_def = self.map.territories[t2]

        # Compute participating forces
        atk_amt = int(data['amount'])
        def_amt = trty_def.troops

        # Compute player battle stats
        atk_stats = atk_p.temp_stats
        def_stats = self.get_player_battle_stats(def_p)

        # Simulate battle and get result
        print(f"Attacker: {atk_p.name}\nAttacking amount: {atk_amt} Attacker stats: {atk_stats}\nDefender: {def_p.name}\nDefensing amount: {def_amt} Defender stats: {def_stats}")
        result = self.simulate_attack(atk_amt, def_amt, atk_stats, def_stats)

        # Remove troops from attacking territory
        trty_atk.troops -= atk_amt
        self.server.emit('update_trty_display', {t1:{'troops': trty_atk.troops}}, room=self.lobby)
        
        # Possible future concern: multiplier causing both sides going below 0
        # Battle results
        # attacker wins
        # CM
        if result[0] > 0:

            # Territory troop change
            trty_def.troops = result[0]
            self.server.emit('update_trty_display', {t2:{'troops': trty_def.troops}}, room=self.lobby)
            # Attacker gain territory
            atk_p.territories.append(t2)
            self.server.emit('update_player_territories', {'list': atk_p.territories}, room=a_pid)
            self.server.emit('update_trty_display', {t2:{'color': atk_p.color}}, room=self.lobby)
            # Defender lost territory
            def_p.territories.remove(t2)
            self.server.emit('update_player_territories', {'list': def_p.territories}, room=d_pid)

            # update turn victory
            atk_p.turn_victory = True

        # defender wins
        else:

            trty_def.troops = result[1]
            self.server.emit('update_trty_display', {t2:{'troops': trty_def.troops}}, room=self.lobby)
        
        atk_p.total_troops -= (atk_amt-result[0])
        def_p.total_troops -= (def_amt-result[1])

        # update player stats list
        self.update_player_stats(a_pid)
        self.update_player_stats(d_pid)

        self.update_LAO(a_pid)
        self.update_LAO(d_pid)

        self.update_MTO(a_pid)
        self.update_MTO(d_pid)

        if trty_def.isCity or trty_def.isMegacity:
            self.update_TIP(a_pid)
            self.update_TIP(d_pid)

        if trty_def.isTransportcenter:
            self.update_HIP(a_pid)
            self.update_HIP(d_pid)

        self.get_SUP()
        self.update_global_status()

        # mission
        self.signal_MTrackers('indus')
        self.signal_MTrackers('popu')
        self.signal_MTrackers('trty')

        self.et.determine_elimination(self, a_pid, d_pid)
        self.egt.determine_end_game(self)
        

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

