from missions import *
import random
import threading

# GAME CAN ONLY BE ENDED BY DEATH OR ROUND TRACKERS
# Abstract Mission Tracker | DAEMON MODE CHECKING
class Mission_Tracker(threading.Thread):
    
    def __init__(self, gs):
        super().__init__()
        self.observers = []
        self.gs = gs
        self.event = threading.Event()
        self.daemon = True

    def add_observer(self, player):
        self.observers.append(player)

    def remove_observer(self, player):
        self.observers.remove(player)

    def check_conditions(self,):
        raise NotImplementedError("Subclasses must implement check_conditions method")
    
    def run(self, ):
        while not self.gs.GES.interrupt:

            # CHECK IS ONLY DONE WHEN self.event.set()
            self.event.wait()
            
            self.check_conditions()

            self.event.clear()

# Only check condition at end of each round     Round
class Round_Based_Incrementor(Mission_Tracker):

    def __init__(self, gs):
        super().__init__(gs)
    
    def check_conditions(self,):
        print('Round mission tracker activated')
        for obs in self.observers:
            obs.check_round_condition()
            print(f'Checked {obs.name} of player {obs.gs.players[obs.player]}')
        if self.gs.round_based_win:
            self.gs.GES.halt_events()

# Check condition at specific point     Death | Trty | Indus | Popu
class Event_Based_Tracker(Mission_Tracker):

    def __init__(self, gs):
        super().__init__(gs)
    
    def check_conditions(self, ):
        print('Mission tracker activated')
        for obs in self.observers:
            obs.check_conditions()
            print(f'Checked {obs.name} of player {obs.gs.players[obs.player]}')

class Mission_Distributor:

    def __init__(self,):
        self.nat_con = [
            ['Uni', 'Pol']
        ]
        self.dup_con = ['Pop', 'Exp', 'Ind', 'Dom']
        self.self_wins = ['Loy', 'Bon', 'Dec', 'War', 'Pac', 'Str', 'Due', 'Pun', 'Sur']
        self.missions = [
            'Pac', 
            'War', 'Loy', 'Bon',
            'Uni', 'Pol', 'Fan', 
            'Ind',
            'Exp', 'Pop', 'Dom',
            'Gua',
            'Dec',
            'Str', 'Due', 'Pun',
            'Sur'
        ]

        self.S_tier = ['Decapitator', 'Pacifist', 'Starchaser', 'Duelist', 'Punisher']
        self.A_tier = ['Loyalist', 'Survivalist']
        self.B_tier = ['Warmonger', 'Bounty_Hunter']

    def validate_mission_set(self, miss_set):
        c = 0
        for m in miss_set:
            if m in self.self_wins:
                c += 1
            if m in self.dup_con and miss_set.count(m) > 1:
                return True
        if c > 0:
            return True
        for nc in self.nat_con:
            if all(m in nc for m in miss_set):
                return True
        return False

    # Generate mission set based on number of players
    def get_mission_set(self, num_p):
        miss_set = []
        done = False
        count = 0
        while not done:
            choice = random.choice(self.missions)
            if choice == 'Loy':
                if (count + 2) <= num_p and num_p > 4:
                    miss_set.append(choice)
                    miss_set.append(choice)
                    count += 2
            elif choice == 'Pol':
                if choice not in miss_set:
                    if miss_set.count('Pol') > 2:
                        continue
                    elif (count + 2) <= num_p and num_p > 4:
                        miss_set.append(choice)
                        miss_set.append(choice)
                        count += 2
                    else:
                        miss_set.append(choice)
                        count += 1
            elif choice == 'Due':
                if (count + 2) <= num_p:
                    miss_set.append(choice)
                    miss_set.append(choice)
                    count += 2
            elif choice == 'Pun':
                for m in miss_set:
                    if m in self.self_wins:
                        miss_set.append(choice)
                        count += 1
                        break
            else:
                miss_set.append(choice)
                count += 1
            if count == num_p:
                if self.validate_mission_set(miss_set):
                    return miss_set
                miss_set = []
                count = 0

    def initiate_mission(self, gs, player, name):
        if name == 'Pac':
            return Pacifist(player, gs)
        elif name == 'War':
            return Warmonger(player, gs)
        elif name == 'Loy':
            return Loyalist(player, gs)
        elif name == 'Bon':
            return Bounty_Hunter(player, gs)
        elif name == 'Uni':
            return Unifier(player, gs)
        elif name == 'Pol':
            return Polarizer(player, gs)
        elif name == 'Fan':
            return Fanatic(player, gs)
        elif name == 'Ind':
            return Industrialist(player, gs)
        elif name == 'Exp':
            return Expansionist(player, gs)
        elif name == 'Pop':
            return Populist(player, gs)
        elif name == 'Dom':
            return Dominator(player, gs)
        elif name == 'Gua':
            return Guardian(player, gs)
        elif name == 'Dec':
            return Decapitator(player, gs)
        elif name == 'Str':
            return Starchaser(player, gs)
        elif name == 'Due':
            return Duelist(player, gs)
        elif name == 'Pun':
            return Punisher(player, gs)

    def set_up_mission_trackers(self, gs, miss_set):
        for m in miss_set:
            if m.name in ['Pacifist', 'Warmonger', 'Loyalist', 'Bounty_Hunter', 'Duelist', 'Punisher', 'Survivalist']:
                if 'death' not in gs.MTrackers:
                    gs.MTrackers['death'] = Event_Based_Tracker(gs)
                gs.MTrackers['death'].add_observer(m)
            if m.type == 'r_based':
                if 'round' not in gs.MTrackers:
                    gs.MTrackers['round'] = Round_Based_Incrementor(gs)
                gs.MTrackers['round'].add_observer(m)
            if m.name in ['Unifier', 'Polarizer', 'Fanatic', 'Industrialist', 'Expansionist', 'Guardian', 'Dominator', 'Decapitator', 'Starchaser']:
                if 'trty' not in gs.MTrackers:
                    gs.MTrackers['trty'] = Event_Based_Tracker(gs)
                gs.MTrackers['trty'].add_observer(m)
            if m.name in ['Industrialist', 'Dominator']:
                if 'indus' not in gs.MTrackers:
                    gs.MTrackers['indus'] = Event_Based_Tracker(gs)
                gs.MTrackers['indus'].add_observer(m)
            if m.name in ['Populist', 'Dominator']:
                if 'popu' not in gs.MTrackers:
                    gs.MTrackers['popu'] = Event_Based_Tracker(gs)
                gs.MTrackers['popu'].add_observer(m)
        
        # start running the trackers
        for t in gs.MTrackers:
            gs.MTrackers[t].start()
    
    def determine_winners(self, gs):

        # Redefine this
        c = []
        for p in gs.players:
            if gs.players[p].alive:
                c.append(p)
        # Solo Winner
        if len(c) == 1:
            for mis in gs.Mset:
                if mis.player == c[0]:
                    return {c[0]: mis.name}
        Pac = {}
        S_tier = {}
        A_tier = {}
        B_tier = {}
        C_tier = {}
        miss_set = gs.Mset
        for m in miss_set:
            if m.end_game_checking():
                if m.name in self.S_tier:
                    if m.name == 'Pacifist':
                        Pac[m.player] = m.name
                    else:
                        S_tier[m.player] = m.name
                elif m.name in self.A_tier:
                    A_tier[m.player] = m.name
                elif m.name in self.B_tier:
                    B_tier[m.player] = m.name
                else:
                    C_tier[m.player] = m.name

        # Return {} -> key: pid   value: name of mission
        if len(Pac) > 0:
            return Pac
        if len(S_tier) > 0:
            return S_tier
        elif len(A_tier) > 0:
            return A_tier
        elif len(B_tier) > 0:
            return B_tier
        else:
            return C_tier
        
    def no_conflicts(self, mission_name_list, mission_list):
        print(mission_name_list)
        print(mission_list)
        self.self_wins = ['Loy', 'Bon', 'Dec', 'War', 'Pac', 'Str', 'Due', 'Pun']
        for name in mission_name_list:
            if name in ['Loyalist', 'Bounty_Hunter', 'Decapitator', 'Warmonger', 'Pacifist', 'Starchaser', 'Duelist', 'Punisher']:
                return False
            if name in ['Industrialist', 'Expansionist', 'Dominator', 'Populist'] and mission_name_list.count(name) > 1:
                return False
            if name == 'Fanatic' and mission_name_list.count(name) > 1:
                return False
        if 'Unifier' in mission_name_list and 'Polarizer' in mission_name_list:
            return False
        if mission_name_list.count('Unifier') > 2:
            count_cont = {}
            for mission in mission_list:
                if mission.name == 'Unifier':
                    if mission.target_continent not in count_cont:
                        count_cont[mission.target_continent] = 1
                    else:
                        count_cont[mission.target_continent] += 1
            for cont, count in count_cont.items():
                if count > 1:
                    return False
        if 'Unifier' in mission_name_list and 'Fanatic' in mission_name_list:
            U, F = [], None
            for mission in mission_list:
                if mission.name == 'Unifier':
                    U.append(mission)
                if mission.name == 'Fanatic':
                    F = mission
            for miss in U:
                if bool(set(miss.gs.map.conts[miss.target_continent]['trtys']) & set(F.targets)):
                    return False
        if 'Guardian' in mission_name_list and 'Fanatic' in mission_name_list:
            G, F = [], None
            for mission in mission_list:
                if mission.name == 'Guardian':
                    G.append(mission)
                if mission.name == 'Fanatic':
                    F = mission
            for miss in G:
                curr_id = 0
                for trty in miss.gs.map.territories:
                    if trty.name == miss.gs.players[miss.player].capital:
                        break
                    curr_id += 1
                
                if curr_id in F.targets:
                    return False
        if 'Guardian' in mission_name_list and 'Unifier' in mission_name_list:
            G, U = [], []
            for mission in mission_list:
                if mission.name == 'Guardian':
                    G.append(mission)
                if mission.name == 'Fanatic':
                    U.append(mission)
            for miss in G:
                curr_id = 0
                for trty in miss.gs.map.territories:
                    if trty.name == miss.gs.players[miss.player].capital:
                        break
                    curr_id += 1
                for uni in U:
                    if curr_id in uni.gs.map.conts[uni.target_continent]['trtys']:
                        return False
        return True
    
    def determine_gp_winners(self, gs):

        mission_name_list = [mission.name for mission in gs.Mset if (gs.players[mission.player].alive and gs.players[mission.player].connected)]
        mission_list = [mission for mission in gs.Mset if gs.players[mission.player].alive]
        if self.no_conflicts(mission_name_list, mission_list):
            winners = {}
            for miss in mission_list:
                winners[miss.player] = miss.name
            return winners

        # Redefine this
        c = []
        for p in gs.players:
            if gs.players[p].alive:
                c.append(p)
        # Solo Winner
        if len(c) == 1:
            for mis in gs.Mset:
                if mis.player == c[0]:
                    return {c[0]: mis.name}
        
        Pac = {}
        S_tier = {}
        A_tier = {}
        B_tier = {}
        C_tier = {}
        miss_set = gs.Mset
        for m in miss_set:
            if m.end_game_global_peace_checking():
                if m.name in self.S_tier:
                    if m.name == 'Pacifist':
                        Pac[m.player] = m.name
                    else:
                        S_tier[m.player] = m.name
                elif m.name in self.A_tier:
                    A_tier[m.player] = m.name
                elif m.name in self.B_tier:
                    B_tier[m.player] = m.name
                else:
                    C_tier[m.player] = m.name

        # Return {} -> key: pid   value: name of mission
        if len(Pac) > 0:
            return Pac
        if len(S_tier) > 0:
            return S_tier
        elif len(A_tier) > 0:
            return A_tier
        elif len(B_tier) > 0:
            return B_tier
        else:
            return C_tier