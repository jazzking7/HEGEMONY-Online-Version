import math
import random

class Mission:
    def __init__(self, name, player, gs):
        self.name = name
        self.player = player
        self.gs = gs
        self.type = None

    def check_conditions(self, ):
        raise NotImplementedError("Subclasses must implement check_conditions method")

    def signal_mission_success(self,):
        self.gs.GES.halt_events()
        return

    def set_up_tracker_view(self, ):
        raise NotImplementedError("Subclasses must implement set_up method")

    def end_game_checking(self, ):
        raise NotImplementedError("Subclasses must implement end_game_checking method")

    def update_tracker_view(self, updates):
        self.gs.server.emit('update_tracker', updates, room=self.player)

    def signal_mission_failure(self, ):
        if self.gs.players[self.player].alive:
            self.gs.players[self.player].alive = False
            self.gs.players[self.player].skill.active = False
            self.gs.perm_elims.append(self.player)
            self.gs.death_logs[self.player] = 'MF'
            self.gs.signal_MTrackers('death')
            self.gs.egt.determine_end_game(self.gs)

class Pacifist(Mission):

    def __init__(self, player, gs):
        super().__init__("Pacifist", player, gs)
        self.death_count = 0
        self.round = 0
        self.type = 'r_based'
        self.max_death_count = math.floor(len(gs.pids)/2)
        self.goal_round = 8

    def check_conditions(self,):
        if not self.gs.players[self.player].alive:
            return
        dc = len(self.gs.perm_elims)
        if dc > self.death_count:
            self.round = -1
            self.death_count = dc
            self.update_tracker_view({
                'misProgBar': [0, self.goal_round],
                'misProgDesp': f'{0}/{self.goal_round} consecutive rounds of peace maintained',
                'lossProg': [self.death_count, self.max_death_count],
                'lossDesp': f'{self.death_count}/{self.max_death_count} deaths until mission failure'
            })
        if self.death_count == self.max_death_count:
            self.update_tracker_view({
                'misProgBar': [0, self.goal_round],
                'misProgDesp': f'{0}/{self.goal_round} consecutive rounds of peace maintained',
                'lossProg': [self.death_count, self.max_death_count],
                'lossDesp': f'Eliminated due to mission failure'
            })
            self.signal_mission_failure()
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        self.round += 1
        self.update_tracker_view({
            'misProgBar': [self.round, self.goal_round],
            'misProgDesp': f'{self.round}/{self.goal_round} consecutive rounds of peace maintained',
            })
        if self.round == self.goal_round:
            # signal end
            self.signal_mission_success()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.goal_round],
            'misProgDesp': f'{self.round}/{self.goal_round} consecutive rounds of peace maintained',
            'lossProg': [self.death_count, self.max_death_count],
            'lossDesp': f'{self.death_count}/{self.max_death_count} deaths until mission failure'
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.goal_round and self.gs.players[self.player].alive

class Warmonger(Mission):
    def __init__(self, player, gs):
        super().__init__("Warmonger", player, gs)
        self.goal_count = len(self.gs.pids)//3
        self.goal_count = 2 if len(self.gs.pids) == 5 else self.goal_count
        self.peace = 0
        self.type = 'r_based'
        self.max_peace = 9
        self.death_count = 0

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return

        # count personal kill        
        dc = 0
        for d in self.gs.death_logs:
            if self.player == self.gs.death_logs[d]:
                dc += 1

        if dc > self.death_count:
            self.peace = -1
            self.death_count = dc
            # Signal update
            self.update_tracker_view({
                'misProgBar': [self.death_count, self.goal_count],
                'misProgDesp': f'{self.death_count}/{self.goal_count} deaths until mission success',
                'lossProg': [0, self.max_peace],
                'lossDesp': f'{0}/{self.max_peace} consecutives round of peace until mission failure'
            })
        if self.death_count == self.goal_count:
            # signal end
            self.signal_mission_success()

    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        self.peace += 1
        self.update_tracker_view({
            'lossProg': [self.peace, self.max_peace],
            'lossDesp': f'{self.peace}/{self.max_peace} consecutives round of peace until mission failure'
            })
        if self.peace == self.max_peace:
            self.update_tracker_view({
            'misProgBar': [0, self.goal_count],
            'misProgDesp': f'-/- deaths until mission success',
            'lossDesp': f'Eliminated due to mission failure'
            })
            self.signal_mission_failure()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.death_count, self.goal_count],
            'misProgDesp': f'{self.death_count}/{self.goal_count} deaths until mission success',
            'lossProg': [self.peace, self.max_peace],
            'lossDesp': f'{self.peace}/{self.max_peace} consecutives round of peace until mission failure'
        }, room=self.player)

    def end_game_checking(self, ):

        # count personal kill        
        dc = 0
        for d in self.gs.death_logs:
            if self.player == self.gs.death_logs[d]:
                dc += 1
        self.death_count = dc

        return self.death_count == self.goal_count and self.gs.players[self.player].alive

class Loyalist(Mission):
    def __init__(self, player, gs):
        super().__init__("Loyalist", player, gs)
        self.target_player = None

    def set_partner(self, ):
        for m in self.gs.Mset:
            if m.name == "Loyalist":
                if m.target_player == None:
                    if m.player != self.player:
                        self.target_player = m.player
                        m.target_player = self.player
                        return

    def exactly_two_players_left(self, ):
        s = []
        for p in self.gs.players:
            if self.gs.players[p].alive:
                s.append(p)
        return len(s) == 2 and self.player in s and self.target_player in s

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if not self.gs.players[self.target_player].alive:
            self.update_tracker_view({
            'targets': {self.gs.players[self.target_player].name: 'f'},
            'misProgDesp': 'Partner did not survive, mission failed'
            })
            self.signal_mission_failure()

            # Signal Partner about mission failure
            for miss in self.gs.Mset:
                if miss.name == "Loyalist":
                    if miss.player == self.target_player:
                        miss.update_tracker_view({
                        'targets': {miss.gs.players[miss.target_player].name: 'f'},
                        'misProgDesp': 'Partner did not survive, mission failed'
                        })
                        miss.signal_mission_failure()
        # verify how many players still alive
        if self.exactly_two_players_left():
            self.signal_mission_success()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': {self.gs.players[self.target_player].name: 's'},
            'misProgDesp': 'Partner still alive, fight to be the last survivors!'
        }, room=self.player)

    def end_game_checking(self, ):
        return self.exactly_two_players_left()
        
class Bounty_Hunter(Mission):
    def __init__(self, player, gs):
        super().__init__("Bounty_Hunter", player, gs)
        self.target_players = None
        numt = 0
        nump = len(gs.pids)
        if nump < 5:
            numt = 1
        elif nump < 9:
            numt = 2
        elif nump < 16:
            numt = 3
        while self.target_players is None:
            self.target_players = random.sample(gs.pids, numt)
            if player in self.target_players:
                self.target_players = None

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # check if target players are dead
        c = 0
        for target in self.target_players:
            if target in self.gs.perm_elims:
                self.update_tracker_view({'targets': {self.gs.players[target].name: 's'}})
                c += 1
            else:
                self.update_tracker_view({'targets': {self.gs.players[target].name: 'f'}})
        if c == len(self.target_players):
            # signal end
            self.update_tracker_view({'misProgDesp': 'bounty fulfilled'})
            self.signal_mission_success()

    def set_up_tracker_view(self, ):
        targets = {}
        for t in self.target_players:
            targets[self.gs.players[t].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgDesp': 'bounty not yet fulfilled'
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        for target in self.target_players:
            if target in self.gs.perm_elims:
                    continue
            else:
                return False
        return True

class Unifier(Mission):
    def __init__(self, player, gs):
        super().__init__("Unifier", player, gs)
        self.target_continent = random.choice(list(gs.map.conts.keys()))
        self.target_round = 0
        l = len(gs.map.conts[self.target_continent]['trtys'])
        if l <= 5:
            self.target_round = 5
        elif l <= 10:
            self.target_round = 3
        else:
            self.target_round = 2
        self.round = 0
        self.type = 'r_based'
    
    def own_target_cont(self, ):
        return self.gs.map.own_continent(self.gs.players[self.player].territories, self.gs.map.conts[self.target_continent]['trtys'])

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if not self.own_target_cont():
            self.round = -1
            self.update_tracker_view({
            'targets': {self.target_continent: 'f'},
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Successfully controlled {self.target_continent} for {0}/{self.target_round} consecutive rounds'
            })
        else:
            self.update_tracker_view({'targets': {self.target_continent: 's'}})
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.own_target_cont():
            self.round += 1
            self.update_tracker_view({
                'targets': {self.target_continent: 's'},
                'misProgBar': [self.round, self.target_round],
                'misProgDesp': f'Successfully controlled {self.target_continent} for {self.round}/{self.target_round} consecutive rounds'
                })
        if self.round == self.target_round:
            # signal end
            self.signal_mission_success()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': {self.target_continent: 'f'},
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Successfully controlled {self.target_continent} for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)
    
    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Polarizer(Mission):
    def __init__(self, player, gs):
        super().__init__("Polarizer", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 2

    def no_unification(self,):
        for cont in self.gs.map.conts:
            for p in self.gs.players:
                if self.gs.map.own_continent(self.gs.players[p].territories, self.gs.map.conts[cont]['trtys']):
                    return False
        return True

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if not self.no_unification():
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'{0}/{self.target_round} consecutive rounds without continental unification'})
    
    def check_round_condition(self,):
        if not self.gs.players[self.player].alive:
            return
        if self.no_unification():
            self.round += 1
            self.update_tracker_view({'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'{self.round}/{self.target_round} consecutive rounds without continental unification'})
        if self.round == self.target_round:
            # signal end
            self.signal_mission_success()
        
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'{self.round}/{self.target_round} consecutive rounds without continental unification',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Fanatic(Mission):
    def __init__(self, player, gs):
        super().__init__("Fanatic", player, gs)
        self.type = 'r_based'
        self.round = 0
        m = len(gs.map.territories)
        self.targets = random.sample([i for i in range(m)], 5)
        self.target_round = 4
    
    def own_all_targets(self, ):
        p_list = self.gs.players[self.player].territories
        targets = {}
        for t in self.targets:
            if t in p_list:
                targets[self.gs.map.territories[t].name] = 's'
            else:
                targets[self.gs.map.territories[t].name] = 'f'
        self.update_tracker_view({'targets': targets})
        return self.gs.map.own_continent(p_list, self.targets)

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # verify if player owns the targets
        if not self.own_all_targets():
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Controlled target territories for {0}/{self.target_round} consecutive rounds',})
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.own_all_targets():
            self.round += 1
            self.update_tracker_view({'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Controlled target territories for {self.round}/{self.target_round} consecutive rounds',})
            if self.round == self.target_round:
                # signal end 
                self.signal_mission_success()
                
    def set_up_tracker_view(self, ):
        targets = {}
        for t in self.targets:
            targets[self.gs.map.territories[t].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Controlled target territories for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Industrialist(Mission):
    def __init__(self, player, gs):
        super().__init__("Industrialist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 3

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.TIP != self.player:
            self.round = -1
            self.update_tracker_view({
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Being the most industrialized player for {0}/{self.target_round} consecutive rounds',
            })
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.TIP == self.player:
            self.round += 1
            self.update_tracker_view({
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Being the most industrialized player for {self.round}/{self.target_round} consecutive rounds',
            })
            if self.round == self.target_round:
                # signal end
                self.signal_mission_success()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Being the most industrialized player for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Expansionist(Mission):
    def __init__(self, player, gs):
        super().__init__("Expansionist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 3

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.MTO != self.player:
            self.round = -1
            self.update_tracker_view({
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Controlled the most territories for {0}/{self.target_round} consecutive rounds',
            })

    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.MTO == self.player:
            self.round += 1
            self.update_tracker_view({
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Controlled the most territories for {self.round}/{self.target_round} consecutive rounds',
            })
            if self.round == self.target_round:
                # signal end
                self.signal_mission_success()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Controlled the most territories for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Populist(Mission):
    def __init__(self, player, gs):
        super().__init__("Populist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 4

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # verify if player holds LAO title
        if self.gs.LAO != self.player:
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Holding the largest army for {0}/{self.target_round} consecutive rounds',})

    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.LAO == self.player:
            self.round += 1
            self.update_tracker_view({'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Holding the largest army for {self.round}/{self.target_round} consecutive rounds',})
            if self.round == self.target_round:
                # signal end 
                self.signal_mission_success()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Holding the largest army for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
        
class Dominator(Mission):
    def __init__(self, player, gs):
        super().__init__("Dominator", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 2

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # verify if player holds SUP title
        if self.gs.SUP != self.player:
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Exercising supremacy for {0}/{self.target_round} consecutive rounds',})

    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.SUP == self.player:
            self.round += 1
            self.update_tracker_view({'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Exercising supremacy for {self.round}/{self.target_round} consecutive rounds',})
            if self.round == self.target_round:
                # signal end 
                self.signal_mission_success()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Exercising supremacy for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

class Guardian(Mission):
    def __init__(self, player, gs):
        super().__init__("Guardian", player, gs)

    def own_capital(self,):
        p = self.gs.players[self.player]
        for t in p.territories:
            if self.gs.map.territories[t].name == p.capital:
                return True
        return False

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if not self.own_capital():
            # signal death
            self.update_tracker_view({'target': {self.gs.players[self.player].capital: 'f'},
            'misProgDesp': f'Capital captured by foreign forces, mission failed',})
            self.signal_mission_failure()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'target': {self.gs.players[self.player].capital: 's'},
            'misProgDesp': f'Capital remains unconquered, mission still in progress',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.gs.players[self.player].alive
    
class Decapitator(Mission):
    def __init__(self, player, gs):
        super().__init__("Decapitator", player, gs)
        self.target_players = None
        numt = 0
        nump = len(gs.pids)
        numt = nump//2
        while self.target_players is None:
            self.target_players = random.sample(gs.pids, numt)
            if player in self.target_players:
                self.target_players = None

    # get the capital id based on the player's capital name
    def get_capital_id(self, c_name):
        for tid in range(self.gs.map.num_nations):
            if self.gs.map.territories[tid].name == c_name:
                return tid

    def check_conditions(self, ):
        c = 0
        for target in self.target_players:
            # check if capital tid is in player's control
            capital_id = self.get_capital_id(self.gs.players[target].capital)
            if capital_id in self.gs.players[self.player].territories:
                self.update_tracker_view({'targets': {self.gs.players[target].name: 's'}})
                c += 1
            else:
                self.update_tracker_view({'targets': {self.gs.players[target].name: 'f'}})
        if c == len(self.target_players):
            # signal end
            self.update_tracker_view({'misProgDesp': 'All capital captured'})
            self.signal_mission_success()

    def set_up_tracker_view(self, ):
        targets = {}
        for t in self.target_players:
            targets[self.gs.players[t].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgDesp': 'Yet to capture all their capitals.'
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        for target in self.target_players:
            # check if capital tid is in player's control
            capital_id = self.get_capital_id(self.gs.players[target].capital)
            if capital_id not in self.gs.players[self.player].territories:
                return False
        return True
    
class Starchaser(Mission):
    def __init__(self, player, gs):
        super().__init__("Starchaser", player, gs)
        
        self.type = 'r_based'
        self.curr_target = None

        m = len(gs.map.territories)
        valid = False
        while not valid:
            t = random.randint(0, m-1)
            if t not in self.gs.players[self.player].territories:
                self.curr_target = t
                break
        
        self.chase_completed = 0
        self.target_chases = 7

        self.round = 0
        self.death_round = 5

    def set_up_tracker_view(self, ):
        targets = {}
        targets[self.gs.map.territories[self.curr_target].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgBar': [self.chase_completed, self.target_chases],
            'misProgDesp': f'{self.chase_completed}/{self.target_chases} chases completed',
            'lossDesp': f'{self.death_round} rounds left to complete current chase',
            'lossProg': [0, self.death_round]
        }, room=self.player)

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # verify if player owns the target
        if self.curr_target in self.gs.players[self.player].territories:
            self.round = -1
            self.chase_completed += 1
            self.update_tracker_view({'targets': {self.gs.map.territories[self.curr_target].name: 's'}})
            self.update_tracker_view({'misProgBar': [self.chase_completed, self.target_chases],
            'misProgDesp': f'{self.chase_completed}/{self.target_chases} chases completed',})
            self.update_tracker_view({'lossProg': [0, self.death_round],
                'lossDesp': f'{self.death_round} rounds left to complete current chase',})
            
            if len(self.gs.players[self.player].territories) == len(self.gs.map.territories):
                self.signal_mission_success()
                return

            if self.chase_completed == self.target_chases:
                self.signal_mission_success()
                return
            
            # Set new target
            valid = False
            while not valid:
                t = random.randint(0, len(self.gs.map.territories)-1)
                if t not in self.gs.players[self.player].territories:
                    self.curr_target = t
                    targets = {}
                    targets[self.gs.map.territories[t].name] = 'f'
                    self.update_tracker_view({'targets': targets, 'new_target': True})
                    valid = True
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.curr_target not in self.gs.players[self.player].territories:
            self.round += 1
            self.update_tracker_view({'lossProg': [self.round, self.death_round],
                'lossDesp': f'{self.death_round-self.round} rounds left to complete current chase',})
        if self.round == self.death_round:
            self.signal_mission_failure()
    
    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        return self.chase_completed == self.target_chases or len(self.gs.players[self.player].territories) == len(self.gs.map.territories)