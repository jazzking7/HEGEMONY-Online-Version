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

        self.connected = True # Keep track if the player is connected

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
        # Player Power Index
        self.PPI = 0

        self.con_amt = 0    # keep counts of how many territories the player has conquered during a turn

class Game_State_Manager:

    def __init__(self, mapName, player_list, setup_events, server, lobby):

        # Player dict => key: player_id (socket connection id)  value: player object
        self.players = {}
        # All communicatable ids | Used as the turn order for turn based events
        self.pids = []
        # Original players -> not created using skills
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
        # skill distributor
        self.SDIS = None

        # server
        self.server = server
        self.lobby = lobby

        # EVENT SCHEDULER
        self.GES = General_Event_Scheduler(self, setup_events)

        # Mission
        self.Mdist = None
        # Mission sets
        self.Mset = None
        # Mission Trackers that gets triggered at specific call points. See mission_distributor.py for definition
        self.MTrackers = {}

        # Elimination Tracker
        self.et = Elimination_tracker()
        # End game tracker
        self.egt = None

        # Global status
        self.LAO = None
        self.MTO = None
        self.HIP = None
        self.TIP = None
        self.SUP = None

        # Died player
        self.perm_elims = []
        # victim -> killer/mission failure
        self.death_logs = {}

    # connect player to a disconnected player object
    def takeover_disconnected_player(self, new_pid, old_pid, new_name):

        # update superpowers
        self.LAO = self.LAO if self.LAO != old_pid else new_pid
        self.MTO = self.MTO if self.MTO != old_pid else new_pid
        self.HIP = self.HIP if self.HIP != old_pid else new_pid
        self.TIP = self.TIP if self.TIP != old_pid else new_pid
        self.SUP = self.SUP if self.SUP != old_pid else new_pid

        # change pid in turn queue
        i_to_c = None
        for index, pid in enumerate(self.pids):
            if pid == old_pid:
                i_to_c = index
        
        self.pids[i_to_c] = new_pid

        # change pid in oriplayers
        for index, pid in enumerate(self.oriPlayers):
            if pid == old_pid:
                i_to_c = index
        
        self.oriPlayers[i_to_c] = new_pid

        # Update players
        p_object = self.players[old_pid]
        self.players[new_pid] = p_object
        self.players[new_pid].name = new_name
        if self.players[new_pid].skill:
            self.players[new_pid].skill.player = new_pid
        del self.players[old_pid]

        # Update death logs and perm_elims
        if old_pid in self.perm_elims:
            self.perm_elims.remove(old_pid)
            self.perm_elims.append(new_pid)
        if old_pid in self.death_logs:
            val = self.death_logs[old_pid]
            self.death_logs[new_pid] = val
            del self.death_logs[old_pid]

        # Update mission trackers !!! Condition check for missions need update
        for mission in self.Mset:
            # change player of old_pid to new_pid
            if mission.player == old_pid:
                mission.player = new_pid
            # update partner for loyalist
            if mission.name == 'Loyalist':
                if mission.target_player == old_pid:
                    mission.target_player = new_pid
                    mission.update_tracker_view({
                    'targets': {mission.gs.players[mission.target_player].name: 's'},
                    })
            if mission.name == 'Duelist':
                if mission.target_player == old_pid:
                    mission.target_player = new_pid
                    mission.update_tracker_view({
                    'targets': {mission.gs.players[mission.target_player].name: 'f'},
                    })
            # update target for bounty hunter
            if mission.name == 'Bounty_Hunter':
                if old_pid in mission.target_players:
                    mission.target_players.remove(old_pid)
                    mission.target_players.append(new_pid)
                    mission.check_conditions()
            # update target for decapitator:
            if mission.name == 'Decapitator':
                if old_pid in mission.target_players:
                    mission.target_players.remove(old_pid)
                    mission.target_players.append(new_pid)
                    mission.check_conditions()
        
        return True
    
    def update_all_views(self, pid):
        
        time.sleep(10)
        
        # Territory
        all_trty_updates = {}
        for tid, trty in enumerate(self.map.territories):

            all_trty_updates[tid] = {
                "troops": trty.troops,
                "isCapital": trty.isCapital
            }
            # city
            if trty.isCity:
                all_trty_updates[tid]['hasDev'] = 'city'

            # color
            for p in self.players:
                if tid in self.players[p].territories:
                    all_trty_updates[tid]['color'] = self.players[p].color

            # capital color
            if trty.isCapital:
                for p in self.players:
                    if self.players[p].capital == trty.name:
                        all_trty_updates[tid]['capital_color'] = self.players[p].color
        
        # Territory
        self.server.emit('update_trty_display', all_trty_updates, room=pid)

        # Global overview
        self.update_global_status()
        # Private overview
        self.update_private_status(pid)
        # Mission overview
        for mission in self.Mset:
            if mission.player == pid:
                mission.set_up_tracker_view()
                mission.check_conditions()
        # Playerlist
        self.send_player_list()
        

        self.players[pid].connected = True if not self.players[pid].connected else False

    def compute_SD(self, metric, avg, alive):
        total_div = 0
        for p in self.players:
            curr_p = self.players[p]
            if curr_p.alive:
                if metric == 'indus':
                    total_div += (self.get_player_industrial_level(curr_p) - avg)**2
                elif metric == 'infra':
                    total_div += (curr_p.infrastructure_upgrade + curr_p.infrastructure - avg)**2
                elif metric == 'trty':
                    total_div += (self.get_deployable_amt(p) - avg)**2
                elif metric == 'popu':
                    total_div += (curr_p.total_troops - avg)**2
        return (total_div/alive)**(1/2)

    def logistic_function(self, z):
        return 1 / (1 + math.exp(-z))

    def compute_PPI(self, ):
        total_trty = 0
        total_popu = 0
        total_inf = 0
        total_ind = 0

        p_alive = []
        for p in self.players:
            curr_p = self.players[p]
            if curr_p.alive:
                total_ind += self.get_player_industrial_level(curr_p)
                total_inf += curr_p.infrastructure_upgrade + curr_p.infrastructure
                total_popu += curr_p.total_troops
                total_trty += self.get_deployable_amt(p)
                p_alive.append(p)
            else:
                curr_p.PPI = 0

        num_alive = len(p_alive) if len(p_alive) > 0 else 1
        avg_ind = total_ind/num_alive
        avg_inf = total_inf/num_alive
        avg_popu = total_popu/num_alive
        avg_trty = total_trty/num_alive

        indsd = self.compute_SD('indus', avg_ind, num_alive)
        infsd = self.compute_SD('infra', avg_inf, num_alive)
        popusd = self.compute_SD('popu', avg_popu, num_alive)
        trtysd = self.compute_SD('trty', avg_trty, num_alive)

        indsd = 1 if indsd == 0 else indsd
        infsd = 1 if infsd == 0 else infsd
        popusd = 1 if popusd == 0 else popusd
        trtysd = 1 if trtysd == 0 else trtysd

        for p in p_alive:
            curr_p = self.players[p]
            z_score = 0.25*((self.get_deployable_amt(p)-avg_trty)/trtysd) + 0.25*((self.get_player_industrial_level(curr_p)-avg_ind)/indsd) + 0.25*((curr_p.infrastructure_upgrade + curr_p.infrastructure-avg_inf)/infsd) + 0.25*((curr_p.total_troops-avg_popu)/popusd)
            curr_p.PPI = round(self.logistic_function(z_score) * 100, 3)

    # Signal the specific mission tracker to check condition
    def signal_MTrackers(self, event_name):
        if event_name in self.MTrackers:
            self.MTrackers[event_name].event.set()
            return True
        return False

    def game_over(self, ):
        winners = self.Mdist.determine_winners(self)
        winners = [{self.players[w].name: winners[w]} for w in winners]
        self.signal_view_clear()
        time.sleep(1)
        self.server.emit('GAME_OVER', {
            'winners': winners,
        }, room=self.lobby)

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

    # Update the global status
    def update_global_status(self, ):
        self.server.emit('update_global_status',
        {'game_round': self.GES.round,
        'LAO': self.players[self.LAO].name if self.LAO != None else "Yet to exist",
        'MTO': self.players[self.MTO].name if self.MTO != None else "Yet to exist",
        'TIP': self.players[self.TIP].name if self.TIP != None else "Yet to exist",
        'SUP': self.players[self.SUP].name if self.SUP != None else "Yet to exist",}, room=self.lobby)
    
    # FOR SHOWING SPECIAL AUTHORITY OUTSIDE OF TURN FOR SPECIFIC PLAYER
    def update_private_status(self, pid):
        self.server.emit('private_overview', {'curr_SA': self.players[pid].stars, 'curr_RS': self.players[pid].reserves}, room=pid)

    def convert_reserves(self, amt, player):
        extra = 0
        if amt == 2:
            extra = 3
        elif amt == 3:
            extra = 5
        elif amt == 4:
            extra = 7
        elif amt == 5:
            extra = 10
        elif amt == 6:
            extra = 13
        elif amt == 7:
            extra = 16
        elif amt == 8:
            extra = 19
        elif amt == 9:
            extra = 23
        elif amt == 10:
            extra = 28
        elif amt == 11:
            extra = 33
        elif amt == 12:
            extra = 38
        elif amt == 13:
            extra = 44
        elif amt == 14:
            extra = 52
        elif amt == 15:
            extra = 60
        self.players[player].reserves += extra
        self.players[player].stars -= amt
        self.update_private_status(player)

    def get_total_troops_of_player(self, player):
        player = self.players[player]
        total = 0
        for t in player.territories:
            total += self.map.territories[t].troops
        player.total_troops = total
        return total

    def send_player_list(self, ):
        self.compute_PPI()
        data = {}
        for pid in self.pids:
            data[self.players[pid].name] = {
                'troops': self.get_total_troops_of_player(pid),
                'trtys': len(self.players[pid].territories),
                'color': self.players[pid].color,
                'PPI': self.players[pid].PPI
            }
        self.server.emit('get_players_stats', data, room=self.lobby)
    
    def update_player_stats(self, ):
        self.compute_PPI()
        for p in self.players:
            data = {
                'name': self.players[p].name,
                'troops': self.players[p].total_troops,
                'trtys': len(self.players[p].territories),
                'PPI': self.players[p].PPI
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
        self.update_private_status(player)
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
            updated_trty = []
            while (p.deployable_amt != 0):
                trty = random.choice(p.territories)
                t = self.map.territories[trty]
                t.troops += 1
                p.total_troops += 1
                p.deployable_amt -= 1
                if trty not in updated_trty:
                    updated_trty.append(trty)
            updated_tids = {tid: {'troops': self.map.territories[tid].troops} for tid in updated_trty}
            print(updated_tids)
            self.server.emit('update_trty_display', updated_tids, room=self.lobby)
            self.update_LAO(player)
            self.get_SUP()
            self.update_global_status()
            self.update_player_stats()
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

        # 0 -> indus  1 -> infra  2 -> frameshift (min)  3 -> null rate   4 -> dmg multiplier
        stats = []
        # get industrial level
        stats.append(self.get_player_industrial_level(player)+6)
        # get infrastructure level
        stats.append(self.get_player_infra_level(player)+3)
        # frameshift (min roll)
        if stats[0] < player.min_roll:
            stats.append(stats[0])
        else:
            stats.append(player.min_roll)
        # Default Null rate
        stats.append(0)
        # Dmg multipler
        stats.append(1)
        return stats
    
    def apply_skill_related_modification(self, atk_p, atk_stats, def_p, def_stats):

        # Attacker and Defender modify their own stats
        # Industrialist + Zealous_Expansion + Ares' Blessing + Realm of Permafrost
        # + Frameshifter
        if atk_p.skill:
            if atk_p.skill.active and atk_p.skill.intMod:
                atk_p.skill.internalStatsMod(atk_stats)
        
        if def_p.skill:
            if def_p.skill.active and def_p.skill.intMod:
                def_p.skill.internalStatsMod(def_stats)
        
        # Attack and Defender modify other's stats
        # Realm of Permafrost
        if atk_p.skill:
            if atk_p.skill.active and atk_p.skill.extMod:
                atk_p.skill.externalStatsMod(def_stats)
        
        if def_p.skill:
            if def_p.skill.active and def_p.skill.extMod:
                def_p.skill.externalStatsMod(atk_stats)

        # Attacker and Defender modify their stats according to other's stats
        # Iron Wall
        if atk_p.skill:
            if atk_p.skill.active and atk_p.skill.reactMod:
                atk_p.skill.reactStatsMod(atk_stats, def_stats, True)
        
        if def_p.skill:
            if def_p.skill.active and def_p.skill.reactMod:
                def_p.skill.reactStatsMod(def_stats, atk_stats, False)

    def handle_battle(self, data):
        # Load territories involved
        t1, t2 = data['choice']
        
        # Identify opponents: 
        # atk_p -> player object of attacker
        # def_p -> player object of defender
        # a_pid -> socket id of attacker
        # d_pid -> socket id of defender
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

        # Stats modifier
        self.apply_skill_related_modification(atk_p, atk_stats, def_p, def_stats)

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
            # Counter multiplier overkill
            if result[1] < 0:
                result[1] = 0
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
            atk_p.con_amt += 1

            # Necromancer
            if atk_p.skill:
                if atk_p.skill.active:
                    if atk_p.skill.name == "Necromancer" and atk_p.skill.activated:
                        atk_p.reserves += def_amt-result[1]
                        self.update_private_status(a_pid)

        # defender wins
        else:
            # Counter multiplier overkill
            if result[1] <= 0:
                result[1] = 1
            if result[0] < 0:
                result[0] = 0
            trty_def.troops = result[1]
            self.server.emit('update_trty_display', {t2:{'troops': trty_def.troops}}, room=self.lobby)

            # Necromancer
            if def_p.skill:
                if def_p.skill.active:
                    if def_p.skill.name == "Necromancer":
                        def_p.reserves += atk_amt-result[0]
                        self.update_private_status(d_pid)
        
            if atk_p.skill:
                if atk_p.skill.active:
                    if atk_p.skill.name == "Necromancer" and atk_p.skill.activated:
                        atk_p.reserves += def_amt-result[1]
                        self.update_private_status(a_pid)

        # Sound effect
        if def_p.total_troops != 0:
            big_battle = ((atk_amt/atk_p.total_troops > 0.15) and (def_amt/def_p.total_troops > 0.15)) or atk_amt/atk_p.total_troops > 0.25
            self.server.emit('battle_propagation', {'battlesize': big_battle}, room=self.lobby)

        # visual effect
        self.server.emit('battle_casualties', {
            f'{t1}': {'tid': t1, 'number': atk_amt-result[0]},
            f'{t2}': {'tid': t2, 'number': def_amt-result[1]},
        }, room=self.lobby)

        # update total troops of players
        atk_p.total_troops -= (atk_amt-result[0])
        def_p.total_troops -= (def_amt-result[1])

        # update player stats list
        self.update_player_stats()

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
        a_maxv, a_maxt, a_min, a_null, a_mul = atk_stats[0], atk_stats[1], atk_stats[2], atk_stats[3], atk_stats[4]
        d_maxv, d_maxt, d_min, d_null, d_mul = def_stats[0], def_stats[1] - 1, def_stats[2], def_stats[3], def_stats[4]

        # Adjust stats
        a_maxt = a_troops if a_troops < a_maxt else a_maxt
        d_maxt = d_troops if d_troops < d_maxt else d_maxt

        print(a_troops, d_troops)

        # Starts simulation
        while(a_troops > 0 and d_troops > 0):

            a_rolls = sorted([random.randint(a_min, a_maxv) for _ in range(a_maxt)], reverse=True)
            d_rolls = sorted([random.randint(d_min, d_maxv) for _ in range(d_maxt)], reverse=True)

            max_dmg = len(d_rolls) if len(d_rolls) < len(a_rolls) else len(a_rolls)

            for i in range(max_dmg):
                if a_rolls[i] > d_rolls[i]:
                    if random.randint(1, 100) > d_null:
                        d_troops -= 1*a_mul
                else:
                    a_troops -= 1*d_mul
            
            # Adjust dice number
            a_maxt = a_troops if a_troops < a_maxt else a_maxt
            d_maxt = d_troops if d_troops < d_maxt else d_maxt

            print(a_rolls, d_rolls)
            print(a_troops, d_troops)

        return [a_troops, d_troops]
