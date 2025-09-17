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

class Game_State_Manager:

    def __init__(self, mapName, player_list, setup_events, time_settings, server, lobby):

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
# Jasper is a pig! Pig! Pig!
        # color options
        self.color_options = []
        # skill distributor
        self.SDIS = None

        # server
        self.server = server
        self.lobby = lobby

        # EVENT SCHEDULER
        self.GES = General_Event_Scheduler(self, setup_events, time_settings)

        # Mission
        self.Mdist = None
        # Mission sets
        self.Mset = None
        # Mission Trackers that gets triggered at specific call points. See mission_distributor.py for definition
        self.MTrackers = {}
        # Special mission condition checker
        self.SMset = []

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
        self.death_time = {}

        # Ice age
        self.set_ice_age = False
        self.in_ice_age = 0

        # Round based win
        self.round_based_win = False
        # Gambler win
        self.gambler_win = False
        # Annihilator
        self.Annihilator = None

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

        i_to_c = None
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
        
        # skill update
        for skill_holder in self.players:
            curr_p = self.players[skill_holder]
            if curr_p.skill:
                if curr_p.skill.name == 'Loan Shark':
                    if old_pid in curr_p.skill.loan_list:
                        debt = curr_p.skill.loan_list[old_pid]
                        del curr_p.skill.loan_list[old_pid]
                        curr_p.skill.loan_list[new_pid] = debt
                    if old_pid in curr_p.skill.ransom_history:
                        round = curr_p.skill.ransom_history[old_pid]
                        del curr_p.skill.ransom_history[old_pid]
                        curr_p.skill.ransom_history[new_pid] = round
                if curr_p.skill.name == 'Robinhood':
                    if old_pid in curr_p.skill.targets:
                        curr_p.skill.targets.remove(old_pid)
                        curr_p.skill.targets.append(new_pid)
                

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
                    'renewed_targets': {mission.gs.players[mission.target_player].name: 's'},
                    })
                    mission.check_conditions()
            if mission.name == 'Protectionist':
                if mission.target_player == old_pid:
                    mission.target_player = new_pid
                if mission.protection == old_pid:
                    mission.protection = new_pid
            if mission.name == 'Assassin':
                if mission.target_player == old_pid:
                    mission.target_player = new_pid
                if mission.nemesis == old_pid:
                    mission.nemesis = new_pid
                    mission.update_tracker_view({
                        'renewed_targets': {mission.gs.players[mission.target_player].name: 'f'},
                    })
                    mission.update_tracker_view({'misProgDesp':  f'Your need to eliminate {mission.gs.players[mission.target_player].name}. Their bodyguard is {mission.gs.players[mission.nemesis].name}.'})
                    mission.check_conditions()
            if mission.name == 'Duelist':
                if mission.target_player == old_pid:
                    mission.target_player = new_pid
                    mission.update_tracker_view({
                    'renewed_targets': {mission.gs.players[mission.target_player].name: 'f'},
                    })
                    mission.check_conditions()
            # update target for bounty hunter
            if mission.name == 'Bounty_Hunter':
                if old_pid in mission.target_players:
                    mission.target_players.remove(old_pid)
                    mission.target_players.append(new_pid)
                    targets = {}
                    for t in mission.target_players:
                        targets[mission.gs.players[t].name] = 'f'
                    mission.update_tracker_view({
                    'renewed_targets': targets,
                    })  
                    mission.check_conditions()
            # update target for decapitator:
            if mission.name == 'Decapitator':
                if old_pid in mission.target_players:
                    mission.target_players.remove(old_pid)
                    mission.target_players.append(new_pid)
                    targets = {}
                    for t in mission.target_players:
                        targets[mission.gs.players[t].name] = 'f'
                    mission.update_tracker_view({
                    'renewed_targets': targets,
                    })  
                    mission.check_conditions()
        self.server.emit('display_new_notification', {'msg': f'Player {self.players[new_pid].name} connected back to server!'}, room=self.lobby)
        self.players[new_pid].connected = True if not self.players[new_pid].connected else False
        return True
    
    def update_all_views(self, pid):        
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

    def compute_SD(self, metric, avg, alive):
        total_div = 0
        for p in self.players:
            curr_p = self.players[p]
            if curr_p.alive:
                if metric == 'indus':
                    total_div += (self.get_dejure_industrial_level(curr_p) - avg)**2
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
                total_ind += self.get_dejure_industrial_level(curr_p)
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
            z_score = 0.15*((self.get_deployable_amt(p)-avg_trty)/trtysd) + 0.35*((self.get_dejure_industrial_level(curr_p)-avg_ind)/indsd) + 0.15*((curr_p.infrastructure_upgrade + curr_p.infrastructure-avg_inf)/infsd) + 0.35*((curr_p.total_troops-avg_popu)/popusd)
            curr_p.PPI = round(self.logistic_function(z_score) * 100, 3)

    # Signal the specific mission tracker to check condition
    def signal_MTrackers(self, event_name):
        if event_name in self.MTrackers:
            self.MTrackers[event_name].event.set()
            return True
        return False

    def _emit_game_over(self, winners):
        if winners:
            winners = [{self.players[w].name: winners[w]} for w in winners]
        else:
            winners = []
        player_overview = [
            [self.players[pid].name, self.players[pid].skill.name] + [mission.name for mission in self.Mset if mission.player == pid][:1]
            for pid in self.oriPlayers
        ]
        self.signal_view_clear()
        time.sleep(1)
        self.server.emit('GAME_OVER', {
            'winners': winners,
            'player_overview': player_overview,
        }, room=self.lobby)

    def game_over(self):
        winners = self.Mdist.determine_winners(self)
        self._emit_game_over(winners)

    def global_peace_game_over(self):
        winners = self.Mdist.determine_gp_winners(self)
        self._emit_game_over(winners)

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
            curri = self.get_dejure_industrial_level(self.players[p])
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
                pi = self.get_dejure_industrial_level(self.players[p])
                hi = self.get_dejure_industrial_level(self.players[self.TIP])
                if pi > hi:
                    self.TIP = p
                elif pi == hi:
                    self.TIP = None
    
    def get_SUP(self,):
        highest_ppi = max(player.PPI for player in self.players.values())
        highest_pids = [pid for pid, player in self.players.items() if player.PPI == highest_ppi]

        if len(highest_pids) > 1:
            self.SUP = None
        else:
            self.SUP = highest_pids[0]

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
        dmg_mul = 1
        hiddenInd = ""
        if self.players[pid].skill:
            if self.players[pid].skill.name == 'Elitocracy':
                if self.players[pid].skill.Annihilator_as_user:
                    dmg_mul = self.players[pid].min_roll
                else:
                    dmg_mul += self.players[pid].min_roll//2
            if self.players[pid].skill.name == 'Collusion':
                hiddenInd = f" ({self.get_player_industrial_level(self.players[pid]) + 6})"
        self.server.emit('private_overview', {'curr_SA': self.players[pid].stars,
                                               'curr_RS': self.players[pid].reserves,
                                               'curr_indus': str(self.get_dejure_industrial_level(self.players[pid])+6) + hiddenInd,
                                               'curr_infra': self.get_player_infra_level(self.players[pid])+3,
                                               'curr_nul_rate': 0,
                                               'curr_dmg_mul': dmg_mul,
                                               'curr_min_roll': self.players[pid].min_roll}, room=pid)
    
    def starPrice(self, base, player):
        price = base - (self.players[player].infrastructure_upgrade//2)
        return price if price > 1 else 1

    def convert_reserves(self, amt, player):
        if self.in_ice_age:
            if self.players[player].skill:
                if self.players[player].skill.name != 'Realm_of_Permafrost':
                    return
                elif not self.players[player].skill.active:
                    return
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
        if not self.players[player].hijacked:
            self.players[player].reserves += extra
            self.players[player].stars -= amt
            self.update_private_status(player)
        else:
            self.server.emit('display_new_notification', {'msg': 'Cannot use your special authority!'}, room=player)

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
                'PPI': self.players[pid].PPI,
                'player_id': pid,
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

    def reverse_players(self):
        self.pids.reverse()
        reversed_dict = {key: self.players[key] for key in self.pids}
        self.players = reversed_dict

    def signal_view_clear(self,):
        for player in self.players:
            self.server.emit('clear_view', room=player)

    def upgrade_infrastructure(self, amt, player):
        # CM
        if self.in_ice_age:
            if self.players[player].skill:
                if self.players[player].skill.name != 'Realm_of_Permafrost':
                    return
                elif not self.players[player].skill.active:
                    return
        if not self.players[player].hijacked:
            self.players[player].stars -= amt*self.starPrice(3,player)
            self.players[player].infrastructure_upgrade += amt
            self.update_private_status(player)
            self.update_HIP(player)
            self.get_SUP()
            self.update_global_status()
            self.signal_MTrackers('popu')
        else:
            self.server.emit('display_new_notification', {'msg': 'Cannot use your special authority!'}, room=player)

    # Collusion
    def in_secret_control(self, trty_number, player_id):
        for pid in self.players:
            if self.players[pid].skill:
                if self.players[pid].skill.name == "Collusion" and self.players[pid].skill.active:
                    if trty_number in self.players[pid].skill.secret_control_list and player_id != pid:
                        return True
        return False

    def get_deployable_amt(self, player):
        bonus = 0
        t_score = 0
        p = self.players[player]
        divider = 3
        for trty in p.territories:

            # Collusion takeaway
            if self.in_secret_control(trty, player):
                continue

            t = self.map.territories[trty]
            if t.isCapital:
                bonus += 1
            if t.isCity:
                t_score += 1
            if t.isMegacity:
                bonus += 5
            if t.isTransportcenter:
                divider = 2
            if t.isHall:
                bonus += 2
            t_score += 1

        # Collusion bonus
        if p.skill:
            if p.skill.name == "Collusion" and p.skill.active:
                for trty in p.skill.secret_control_list:
                    if trty in p.territories:
                        continue
                    t = self.map.territories[trty]
                    if t.isCapital:
                        bonus += 1
                    if t.isCity:
                        t_score += 1
                    if t.isMegacity:
                        bonus += 5
                    # if t.isTransportcenter:
                    #     bonus += 2
                    t_score += 1
        bonus += self.map.get_continental_bonus(p.territories)

        # Permafrost skip ice age debuff
        if p.skill:
            if p.skill.name == "Realm_of_Permafrost" and p.skill.active:
                if t_score < 9:
                    return bonus + 3
                return bonus + t_score//divider
        if self.in_ice_age:
            if t_score < 15:
                return math.ceil(bonus*0.6) + 2
            return math.ceil(bonus*0.6) + t_score//(divider+2)
        if t_score < 9:
            return bonus + 3
        return bonus + t_score//divider

    def clear_deployables(self, player):
        p =  self.players[player]
        if p.deployable_amt > 0:
            # CM
            updated_trty = []
            while (p.deployable_amt > 0):
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
            self.update_player_stats()
            self.get_SUP()
            self.update_global_status()
            self.signal_MTrackers('popu')

    def leyline_probability(self, num_leylines, hasBuff):
        if num_leylines < 1:
            return 0  # no leylines means no probability

        prob = 17
        increment = 5

        if hasBuff:
            prob = 18
            increment = 6

        for i in range(2, num_leylines + 1):
            prob += increment
            increment += 1
        
        if hasBuff:
            if prob > 80:
                prob = 80
        else:
            if prob > 60:
                prob = 60
        return prob

    def leyline_damage(self, num_leylines, hasBuff):
        if num_leylines < 1:
            return 1
        if not hasBuff:
            base_multiplier = 3
            bonus = num_leylines // 3
        else:
            base_multiplier = 4
            bonus = num_leylines // 3
        return base_multiplier + bonus

    def count_connected_forts(self, player, trty, counted=None):
        if counted is None:
            counted = []

        # Only proceed if this territory belongs to the player, is a fort, and not yet counted
        if trty not in player.territories or trty in counted:
            return 0

        if not self.map.territories[trty].isFort:
            return 0

        counted.append(trty)
        count = 1  # This territory is a fort

        # Now, only explore neighbors that are forts
        for t in self.map.territories[trty].neighbors:
            count += self.count_connected_forts(player, t, counted)

        return count

    def shifted_high_roll(self, a_min, a_maxv, shift_ratio=0.25):

        values = list(range(a_min, a_maxv + 1))
        n = len(values)
        base_prob = 1 / n
        avg = (a_min + a_maxv) / 2


        probs = [base_prob for _ in values]


        low_idxs = [i for i, v in enumerate(values) if v < avg]
        high_idxs = [i for i, v in enumerate(values) if v >= avg]

        if not low_idxs or len(high_idxs) < 2:
            return random.choices(values, weights=probs, k=1)[0]


        take_amount = shift_ratio * base_prob
        for i in low_idxs:
            probs[i] -= take_amount

        total_taken = take_amount * len(low_idxs)
        portions = [2] + [1] * (len(low_idxs) - 2)
        portion_total = sum(portions)

        if portion_total == 0:
            return random.choices(values, weights=probs, k=1)[0]

        portion_unit = total_taken / portion_total


        for i, amount in zip(high_idxs[:-1], portions):
            probs[i] += amount * portion_unit


        total_prob = sum(probs)
        probs = [p / total_prob for p in probs]

        return probs
    
    def get_dejure_industrial_level(self, player):
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

    def get_player_industrial_level(self, player):
        lvl = 0
        c_amt = self.map.count_cities(player.territories)

        pid = None
        for p in self.players:
            if self.players[p] == player:
                pid = p
                break

        # Collusion takeaway
        for trty in player.territories:
            if self.in_secret_control(trty, pid):
                if self.map.territories[trty].isCity:
                    c_amt -= 1

        # Collusion bonus
        if player.skill:
            if player.skill.name == "Collusion" and player.skill.active:
                for trty in player.skill.secret_control_list:
                    if trty not in player.territories:
                        if self.map.territories[trty].isCity:
                            c_amt += 1
                        if self.map.territories[trty].isMegacity:
                            lvl += 1

        if c_amt == 3:
            lvl += 1
        elif c_amt > 3:
            lvl += 1 + (c_amt-3)//2
        for trty in player.territories:
            if self.in_secret_control(trty, pid):
                continue
            if self.map.territories[trty].isMegacity:
                lvl += 1
        return lvl

    def get_player_infra_level(self, player):
        lvl = 0
        pid = None
        for p in self.players:
            if self.players[p] == player:
                pid = p
                break
        for trty in player.territories:
            # Collusion takeaway
            if self.in_secret_control(trty, pid):
                continue
            if self.map.territories[trty].isTransportcenter:
                lvl += 1
        # Collusion bonus
        if player.skill:
            if player.skill.name == "Collusion" and player.skill.active:
                for trty in player.skill.secret_control_list:
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
        # Industrialist + Ares' Blessing + Realm of Permafrost
        # + Elitocracy
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

        if atk_p.skill:
            if "Realm_of_Permafrost" == atk_p.skill.name and atk_p.skill.active:
                atk_stats[3] = 0
                atk_stats[4] = 1
                def_stats[3] = 0
                def_stats[4] = 1

        if def_p.skill:
            if "Realm_of_Permafrost" == def_p.skill.name and def_p.skill.active:
                atk_stats[3] = 0
                atk_stats[4] = 1
                def_stats[3] = 0
                def_stats[4] = 1

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

        def_p.aliveBefore = def_p.alive

        # Identify territories
        trty_atk = self.map.territories[t1]
        trty_def = self.map.territories[t2]

        # Compute participating forces
        atk_amt = int(data['amount'])
        def_amt = trty_def.troops

        # Compute player battle stats
        atk_stats = atk_p.temp_stats[:]
        def_stats = self.get_player_battle_stats(def_p)

        # Fortification
        if trty_def.isFort:
            fortCounts = self.count_connected_forts(def_p, t2)
            if fortCounts:
                def_stats[3] += 20 + (fortCounts * 5)
                def_stats[2] += 1 + (fortCounts//4)
                if def_stats[3] > 60:
                    def_stats[3] = 60

        alcb = False
        dlcb = False
        if atk_p.skill:
            if atk_p.skill.active and atk_p.skill.name == "Archmage":
                alcb = True
        if def_p.skill:
            if def_p.skill.active and def_p.skill.name == "Archmage":
                dlcb = True

        # Leyline
        acrit = self.leyline_probability(atk_p.numLeylines, alcb)
        dcrit = self.leyline_probability(def_p.numLeylines, dlcb)
        acdmg = self.leyline_damage(atk_p.numLeylines, alcb)
        dcdmg = self.leyline_damage(def_p.numLeylines, dlcb)

        # elitocracy territory based stat increase
        if atk_p.skill:
            if atk_p.skill.name == "Elitocracy" and atk_p.skill.active:
                if trty_atk.isCity or trty_atk.isCapital:
                    atk_stats[2] += atk_p.skill.important_bonus
            if atk_p.skill.name == "Mass_Mobilization" and atk_p.skill.active:
                atk_stats[4] += atk_amt//20
            if atk_p.skill.name == "Babylon" and atk_p.skill.active:
                if 3 in atk_p.skill.passives:
                    atk_stats[2] += 1
                    atk_stats[4] += 1


        if def_p.skill:
            if def_p.skill.name == "Elitocracy" and def_p.skill.active:
                if trty_def.isCity or trty_def.isCapital:
                    def_stats[2] += def_p.skill.important_bonus
            
            if def_p.skill.name == "Babylon" and def_p.skill.active:
                if 3 in def_p.skill.passives:
                    atk_stats[2] += 1
                    atk_stats[4] += 1

            if def_p.skill.name == "Air_Superiority" and def_p.skill.active:
                for cont in self.map.conts:
                    currcont = self.map.conts[cont]['trtys']
                    if t2 in currcont:
                        airBonus = True
                        for trty in currcont:
                            if trty in def_p.territories and trty != t2:
                                airBonus = False
                                break
                        if airBonus:
                            def_stats[3] += 25
                            if def_stats[3] > 85:
                                def_stats[3] = 85
                            def_stats[4] += 1
                            if def_p.skill.Annihilator_as_user:
                                def_stats[2] += 1
                                def_stats[3] += 5
                                if def_stats[3] > 90:
                                    def_stats[3] = 90

        # Stats modifier
        self.apply_skill_related_modification(atk_p, atk_stats, def_p, def_stats)

        # Reaping of Anubis
        atk_anu, def_anu = 0, 0
        if atk_p.skill:
            if atk_p.skill.name == "Reaping of Anubis" and atk_p.skill.active:
                def_anu = atk_p.skill.guaranteed_dmg

        if def_p.skill:
            if def_p.skill.name == "Reaping of Anubis" and def_p.skill.active and def_amt > 0:
                atk_anu = def_p.skill.guaranteed_dmg

        if atk_p.skill:
            if atk_p.skill.name == "Realm_of_Permafrost" and atk_p.skill.active:
                atk_anu = 0

        if def_p.skill:
            if def_p.skill.name == "Realm_of_Permafrost" and def_p.skill.active:
                def_anu = 0

        # landmine explosion
        ld = 0
        if def_p.skill:
            if def_p.skill.name == 'Arsenal of the Underworld':
                ld = def_p.skill.get_landmine_damage(t2, atk_amt)

        atkh = False
        defh = False
        # Central Managed Troop Training
        for h1 in atk_p.territories:
            if self.map.territories[h1].isHall:
                atkh = True
                break
        for h2 in def_p.territories:
            if self.map.territories[h2].isHall:
                defh = True
                break

        atroopmul, dtroopmul = 1, 1
        AIA, DIA = 0, 0

        # Simulate battle and get result
        print(f"Attacker: {atk_p.name}\nAttacking amount: {atk_amt} Attacker stats: {atk_stats}\nDefender: {def_p.name}\nDefending amount: {def_amt} Defender stats: {def_stats}")
        multitime = False
        if atk_p.skill:
            if atk_p.skill.name == "Loopwalker" and atk_p.skill.active:
                multitime = True
            if atk_p.skill.name == "Babylon":
                if atk_p.skill.active and 2 in atk_p.skill.passives:
                    multitime = True
            if atk_p.skill.name == "Realm_of_Permafrost" and atk_p.skill.active:
                atkh = False
                defh = False
                acrit = 0
                dcrit = 0
                acdmg = 1
                dcdmg = 1
            if atk_p.skill.name == "Pillar of Immortality" and atk_p.skill.active:
                if t1 in atk_p.skill.pillars:
                    atroopmul = 10
                AIA = len(atk_p.skill.pillars)*3

        if def_p.skill:
            if def_p.skill.name == "Loopwalker" and def_p.skill.active:
                multitime = True
            if def_p.skill.name == "Babylon":
                if def_p.skill.active and 2 in def_p.skill.passives:
                    multitime = True
            if def_p.skill.name == "Realm_of_Permafrost" and def_p.skill.active:
                atkh = False
                defh = False
                acrit = 0
                dcrit = 0
                acdmg = 1
                dcdmg = 1
            if def_p.skill.name == "Pillar of Immortality" and def_p.skill.active:
                if t2 in def_p.skill.pillars:
                    dtroopmul = 10
                DIA = len(def_p.skill.pillars)*3

        if multitime: # time looper
            result = self.simulate_multi_attack(atk_amt-ld-atk_anu, def_amt-def_anu, atk_stats, def_stats, atk_p, def_p, atkh, defh, acrit, dcrit, acdmg, dcdmg, atroopmul, dtroopmul, AIA, DIA)
        else: # normal
            result = self.simulate_attack(atk_amt-ld-atk_anu, def_amt-def_anu, atk_stats, def_stats, atkh, defh, acrit, dcrit, acdmg, dcdmg, atroopmul, dtroopmul, AIA, DIA)
        print(result)
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
                    if atk_p.skill.name == "Necromancer":
                        atk_p.skill.curr_turn_gain += def_amt-result[1]
            
            # Revanchism
            if def_p.skill:
                if def_p.skill.name == "Revanchism" and def_p.skill.active:
                    def_p.skill.accumulate_rage(def_amt-result[1], trty_def)
                if def_p.skill.name == "Pillar of Immortality":
                    if t2 in def_p.skill.pillars:
                        def_p.skill.pillars.remove(t2)
                if def_p.skill.name == "Babylon" and def_p.skill.active:
                    if 11 in def_p.skill.passives:
                        def_p.skill.accumulate_rage(trty_def)

            # Mission Checker
            if self.SMset:
                for m in self.SMset:
                    if m.name == "Gambler" and m.player == a_pid:
                        if atk_amt < def_amt:
                            m.check_conditions(def_amt)
                    if m.name == 'Guardian' and m.player == d_pid and trty_def.isCapital and def_p.alive and def_p.capital == trty_def.name:
                        m.signal_mission_failure()

            if trty_def.isFort:
                trty_def.isFort = False
                self.server.emit('update_trty_display', {t2: {'hasEffect': 'gone'}}, room=self.lobby)
            
            if trty_def.isLeyline:
                trty_def.isLeyline = False
                self.server.emit('update_trty_display', {t2: {'hasEffect': 'leylineGone'}}, room=self.lobby)
                def_p.numLeylines -= 1

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
                    if atk_p.skill.name == "Necromancer":
                        atk_p.skill.curr_turn_gain += def_amt-result[1]

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

        # Ares' Blessing checking for rage meter
        if def_p.skill:
            if def_p.skill.name == "Ares' Blessing" and def_p.skill.active:
                def_p.skill.checking_rage_meter()

        # update player stats list
        self.update_player_stats()

        self.update_LAO(a_pid)
        self.update_LAO(d_pid)

        self.update_MTO(a_pid)
        self.update_MTO(d_pid)

        if trty_def.isCity or trty_def.isMegacity:
            self.update_TIP(a_pid)
            self.update_TIP(d_pid)
            self.update_private_status(a_pid)
            self.update_private_status(d_pid)

        if trty_def.isTransportcenter:
            self.update_HIP(a_pid)
            self.update_HIP(d_pid)

        self.get_SUP()
        self.update_global_status()

        # mission
        self.signal_MTrackers('trty') # Where Guardian signal mission failure
        self.signal_MTrackers('indus')
        self.signal_MTrackers('popu')

        self.et.determine_elimination(self, a_pid, d_pid)
        self.egt.determine_end_game(self)

        if self.gambler_win:
            self.GES.halt_events()

        if self.GES.terminated:
            self.GES.stage_completed = True
        
    def simulate_attack(self, atk_amt, def_amt, atk_stats, def_stats, atkh, defh, acrit, dcrit, acdmg, dcdmg, atroopmul, dtroopmul, AIA, DIA):
        
        # Troop amount
        a_troops = atk_amt
        d_troops = def_amt

        # Troop multiplier
        a_troops *= atroopmul
        d_troops *= dtroopmul

        # Max stats
        a_maxv, a_maxt, a_min, a_null, a_mul = atk_stats[0], atk_stats[1], atk_stats[2], atk_stats[3], atk_stats[4]
        d_maxv, d_maxt, d_min, d_null, d_mul = def_stats[0], def_stats[1] - 1, def_stats[2], def_stats[3], def_stats[4]

        # Adjust stats
        a_maxt = a_troops if a_troops < a_maxt else a_maxt
        d_maxt = d_troops if d_troops < d_maxt else d_maxt

        if a_min > a_maxv:
            a_min = a_maxv
        
        if d_min > d_maxv:
            d_min = d_maxv

        aprobs = None
        dprobs = None
        if atkh:
            aprobs = self.shifted_high_roll(a_min, a_maxv)
        if defh:
            dprobs = self.shifted_high_roll(d_min, d_maxv)

        if not atkh:
            print(f"Attacker is running on standard distribution")
        else:
            print(f"Attacker is running on: {aprobs}")

        if not defh:
            print(f"Defender is running on standard distribution")
        else:
            print(f"Defender is running on: {dprobs}")

        print(a_troops, d_troops)

        # Starts simulation
        while(a_troops > 0 and d_troops > 0):

            if atkh:
                a_rolls = sorted(random.choices(population=list(range(a_min, a_maxv + 1)), weights=aprobs, k=a_maxt),reverse=True)
            else:
                a_rolls = sorted([random.randint(a_min, a_maxv) for _ in range(a_maxt)], reverse=True)

            if defh:
                d_rolls = sorted(random.choices(population=list(range(d_min, d_maxv + 1)), weights=dprobs, k=d_maxt),reverse=True)
            else:
                d_rolls = sorted([random.randint(d_min, d_maxv) for _ in range(d_maxt)], reverse=True)

            max_dmg = len(d_rolls) if len(d_rolls) < len(a_rolls) else len(a_rolls)
            
            a_receive = 0
            d_receive = 0

            for i in range(max_dmg):
                if a_rolls[i] > d_rolls[i]:
                    if random.randint(1, 100) > d_null:                        
                        d_receive += 1
                else:
                    a_receive += 1
            
            if AIA:
                for i in range(AIA):
                    if random.randint(1,100) > 99:
                        d_troops -= 1
            if DIA:
                for i in range(DIA):
                    if random.randint(1,100) > 99:
                        a_troops -= 1

            if a_receive:
                dcurr = random.randint(1, 100)
                dc = 1
                if dcrit >= dcurr:
                    print("Defender dealt crit damage")
                    dc = dcdmg
                a_troops -= a_receive*d_mul*dc
            if d_receive:
                acurr = random.randint(1, 100)
                ac = 1
                if acrit >= acurr:
                    print("Attacker dealt crit damage")
                    ac = acdmg
                d_troops -= d_receive*a_mul*ac
            
            # Adjust dice number
            a_maxt = a_troops if a_troops < a_maxt else a_maxt
            d_maxt = d_troops if d_troops < d_maxt else d_maxt

            print(a_rolls, d_rolls)
            print(a_troops, d_troops)
        a_troops = math.ceil(a_troops/atroopmul)
        d_troops = math.ceil(d_troops/dtroopmul)
        return [a_troops, d_troops]

    def simulate_multi_attack(self, atk_amt, def_amt, atk_stats, def_stats, atk_p, def_p, atkh, defh, acrit, dcrit, acdmg, dcdmg, atroopmul, dtroopmul, AIA, DIA):

        # Time loop setting
        atk_loop, def_loop, run_loop = 1, 1, 1
        if atk_p.skill:
            if atk_p.skill.name == "Loopwalker" and atk_p.skill.active:
                # confirm multi time
                if atk_p.skill.loop_per_battle > 1:
                    atk_loop = atk_p.skill.loop_per_battle
                # prevent overflow
                if atk_loop > atk_p.skill.aval_loops:
                    atk_loop = atk_p.skill.aval_loops
                # prevent negative
                if atk_loop <= 0:
                    atk_loop = 1
                # update aval_loops
                if atk_p.skill.aval_loops > 0:
                    atk_p.skill.aval_loops -= (atk_loop-1)
            if atk_p.skill.name == "Babylon":
                if atk_p.skill.active and 2 in atk_p.skill.passives:
                    atk_loop = 2

        if def_p.skill:
            if def_p.skill.name == "Loopwalker" and def_p.skill.active:
                # confirm multi time
                if def_p.skill.loop_per_battle > 1:
                    def_loop = def_p.skill.loop_per_battle
                # prevent overflow
                if def_loop > def_p.skill.aval_loops:
                    def_loop = def_p.skill.aval_loops
                # prevent negative
                if def_loop <= 0:
                    def_loop = 1
                # update aval_loops
                if def_p.skill.aval_loops > 0:
                    def_p.skill.aval_loops -= (def_loop-1)
            if def_p.skill.name == "Babylon":
                if def_p.skill.active and 2 in def_p.skill.passives:
                    def_loop = 2

        atkfav = False
        deffav = False
        if def_loop == atk_loop:
            run_loop = 1
        elif def_loop > atk_loop:
            run_loop += def_loop - atk_loop
            deffav = True
        elif atk_loop > def_loop:
            run_loop += atk_loop - def_loop
            atkfav = True

        # Troop amount
        a_troops = atk_amt
        d_troops = def_amt

        # Max stats
        a_maxv, a_maxt, a_min, a_null, a_mul = atk_stats[0], atk_stats[1], atk_stats[2], atk_stats[3], atk_stats[4]
        d_maxv, d_maxt, d_min, d_null, d_mul = def_stats[0], def_stats[1] - 1, def_stats[2], def_stats[3], def_stats[4]

        # Adjust stats
        a_maxt = a_troops if a_troops < a_maxt else a_maxt
        d_maxt = d_troops if d_troops < d_maxt else d_maxt

        if a_min > a_maxv:
            a_min = a_maxv
        
        if d_min > d_maxv:
            d_min = d_maxv

        aprobs = None
        dprobs = None
        if atkh:
            aprobs = self.shifted_high_roll(a_min, a_maxv)
        if defh:
            dprobs = self.shifted_high_roll(d_min, d_maxv)

        if not atkh:
            print(f"Attacker is running on standard distribution")
        else:
            print(f"Attacker is running on: {aprobs}")

        if not defh:
            print(f"Defender is running on standard distribution")
        else:
            print(f"Defender is running on: {dprobs}")

        a_troops *= atroopmul
        d_troops *= dtroopmul

        print(a_troops, d_troops)
        print(f"Running {run_loop} loops.")
        outcomes = []
        # Starts simulation
        while(run_loop):

            while(a_troops > 0 and d_troops > 0):

                if atkh:
                    a_rolls = sorted(random.choices(population=list(range(a_min, a_maxv + 1)), weights=aprobs, k=a_maxt),reverse=True)
                else:
                    a_rolls = sorted([random.randint(a_min, a_maxv) for _ in range(a_maxt)], reverse=True)

                if defh:
                    d_rolls = sorted(random.choices(population=list(range(d_min, d_maxv + 1)), weights=dprobs, k=d_maxt),reverse=True)
                else:
                    d_rolls = sorted([random.randint(d_min, d_maxv) for _ in range(d_maxt)], reverse=True)

                max_dmg = len(d_rolls) if len(d_rolls) < len(a_rolls) else len(a_rolls)

                a_receive = 0
                d_receive = 0

                for i in range(max_dmg):
                    if a_rolls[i] > d_rolls[i]:
                        if random.randint(1, 100) > d_null:                        
                            d_receive += 1
                    else:
                        a_receive += 1

                if AIA:
                    for i in range(AIA):
                        if random.randint(1,100) > 99:
                            d_troops -= 1
                if DIA:
                    for i in range(DIA):
                        if random.randint(1,100) > 99:
                            a_troops -= 1
                        
                if a_receive:
                    dcurr = random.randint(1, 100)
                    dc = 1
                    if dcrit >= dcurr:
                        print("Defender dealt crit damage")
                        dc = dcdmg
                    a_troops -= a_receive*d_mul*dc
                if d_receive:
                    acurr = random.randint(1, 100)
                    ac = 1
                    if acrit >= acurr:
                        print("Attacker dealt crit damage")
                        ac = acdmg
                    d_troops -= d_receive*a_mul*ac
                
                # Adjust dice number
                a_maxt = a_troops if a_troops < a_maxt else a_maxt
                d_maxt = d_troops if d_troops < d_maxt else d_maxt
            
            a_troops = math.ceil(a_troops/atroopmul)
            d_troops = math.ceil(d_troops/dtroopmul)

            # adjust result number
            if a_troops <= 0 and d_troops <= 0:
                a_troops = 0
                d_troops = 1  # Defender wins in tie
            else:
                a_troops = max(0, a_troops)
                d_troops = max(0, d_troops)
            
            outcomes.append([a_troops, d_troops])
            a_troops = atk_amt * atroopmul
            d_troops = def_amt * dtroopmul
            
            # Max stats
            a_maxv, a_maxt, a_min, a_null, a_mul = atk_stats[0], atk_stats[1], atk_stats[2], atk_stats[3], atk_stats[4]
            d_maxv, d_maxt, d_min, d_null, d_mul = def_stats[0], def_stats[1] - 1, def_stats[2], def_stats[3], def_stats[4]

            # Adjust stats
            a_maxt = a_troops if a_troops < a_maxt else a_maxt
            d_maxt = d_troops if d_troops < d_maxt else d_maxt

            if a_min > a_maxv:
                a_min = a_maxv
            
            if d_min > d_maxv:
                d_min = d_maxv

            run_loop -= 1
        print(outcomes)
        # End of battle simulations
        if deffav:
            return def_p.skill.get_best_outcome(outcomes, True)
        if atkfav:
            return atk_p.skill.get_best_outcome(outcomes, False)
        return outcomes[0]