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
        for obs in self.observers:
            obs.check_round_condition()

# Check condition at specific point     Death | Trty | Indus | Popu
class Event_Based_Tracker(Mission_Tracker):

    def __init__(self, gs):
        super().__init__(gs)
    
    def check_conditions(self, ):
        for obs in self.observers:
            obs.check_conditions()

class Mission_Distributor:

    def __init__(self,):
        self.nat_con = [
            ['Pac', 'War'],
            ['Uni', 'Pol'],
            ['Dom', 'Ind', 'Exp'],
            ['Dom', 'Ind', 'Pop'],
            ['Dom', 'Exp', 'Pop'],
        ]
        self.dup_con = ['Pop', 'Exp', 'Ind', 'Dom']
        self.self_wins = ['Loy', 'Gua', 'Bon', 'Dec', 'War']
        self.missions = [
            'Pac', 'War', 'Loy', 'Bon',
            'Uni', 'Pol', 'Fan', 'Ind',
            'Exp', 'Pop', 'Dom', 'Gua',
            'Dec'
        ]

        self.first_tier = ['Decapitator', 'Bounty_Hunter']
        self.second_tier = ['Guardian', 'Loyalist']


    def validate_mission_set(self, miss_set):
        c = 0
        for m in miss_set:
            if m in self.self_wins:
                c += 1
            if m in self.dup_con and miss_set.count(m) > 1:
                return True
        if 'Pac' in miss_set and c >= math.floor(len(miss_set)/2):
            return False
        if c > 0:
            return True
        for nc in self.nat_con:
            if all(m in nc for m in miss_set):
                return True
        return False

    def get_mission_set(self, num_p):
        miss_set = []
        done = False
        cl, cg = 0, 0
        print(math.floor(num_p/2))
        while not done:
            choice = random.choice(self.missions)
            if choice == 'Loy' and not cl and num_p > 3:
                miss_set.append(choice)
                cl += 1
            elif choice == 'Loy' and cl:
                continue
            elif choice == 'Gua' and not cg:
                miss_set.append(choice)
                cg += 1
            elif choice == 'Gua' and cg:
                continue
            else:
                miss_set.append(choice)
            if len(miss_set) == num_p:
                if self.validate_mission_set(miss_set):
                    return miss_set
                miss_set = []

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

    def set_up_mission_trackers(self, gs, miss_set):
        for m in miss_set:
            if m.name in ['Pacifist', 'Warmonger', 'Loyalist', 'Bounty_Hunter']:
                if 'death' not in gs.MTrackers:
                    gs.MTrackers['death'] = Event_Based_Tracker(gs)
                gs.MTrackers['death'].add_observer(m)
            if m.type == 'r_based':
                if 'round' not in gs.MTrackers:
                    gs.MTrackers['round'] = Round_Based_Incrementor(gs)
                gs.MTrackers['round'].add_observer(m)
            if m.name in ['Unifier', 'Polarizer', 'Fanatic', 'Industrialist', 'Expansionist', 'Guardian', 'Dominator', 'Decapitator']:
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
        if len(c) == 1:
            return {c[0]: "Lone Survivor"}
        f = {}
        s = {}
        t = {}
        l = None
        miss_set = gs.Mset
        for m in miss_set:
            if m.end_game_checking():
                if m.name in self.first_tier:
                    f[m.player] = m.name
                elif m.name in self.second_tier:
                    s[m.player] = m.name
                    if m.name == 'Loyalist':
                        l = m
                else:
                    t[m.player] = m.name

        if l is not None:
            if l.target_player in t:
                s[l.target_player] = t[l.target_player]
            elif l.target_player in f:
                f[l.player] = s[l.player]
    
        if len(f) > 0:
            return f
        elif len(s) > 0:
            return s
        else:
            return t
        