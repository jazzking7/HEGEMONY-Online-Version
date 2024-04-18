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
        gs.GES.halt_events()
        gs.signal_view_clear()
        gs.server.emit('set_up_announcement', {'msg': f"GAME OVER\n{vp.name}'s victory!"})
        return

    def set_up_tracker_view(self, ):
        raise NotImplementedError("Subclasses must implement set_up method")

    def end_game_checking(self, ):
        raise NotImplementedError("Subclasses must implement set_up method")

    def update_tracker_view(self, updates):
        self.gs.server.emit('update_tracker', updates, room=self.player)

    def signal_mission_failure(self, ):
        self.gs.players[self.player].alive = False
        self.gs.miss_elims.append(self.player)
        self.gs.kill_logs[self.player] = 'MF'
        self.gs.signal_MTrackers('death')

class Pacifist(Mission):

    def __init__(self, player, gs):
        super().__init__("Pacifist", player, gs)
        self.death_count = 0
        self.round = 0
        self.type = 'r_based'
        self.max_death_count = math.floor(len(gs.pids)/2)
        self.goal_round = 10

    def check_conditions(self,):
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
        self.round += 1
        self.update_tracker_view({
            'misProgBar': [0, self.goal_round],
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

class Warmonger(Mission):
    def __init__(self, player, gs):
        super().__init__("Warmonger", player, gs)
        self.goal_count = len(self.gs.pids)//2+1
        self.peace = 0
        self.type = 'r_based'
        self.max_peace = 7
        self.death_count = 0

    def check_conditions(self, ):
        dc = len(self.gs.perm_elims)
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

class Loyalist(Mission):
    def __init__(self, player, gs):
        super().__init__("Loyalist", player, gs)
        self.target_player = None
        while self.target_player is None:
            self.target_player = random.choice(gs.pids)
            if self.target_player == player:
                self.target_player = None

    def check_conditions(self, ):
        if not self.gs.players[self.target_player].alive:
            self.update_tracker_view({
            'targets': {self.gs.players[self.target_player].name: 'f'},
            'misProgDesp': 'Target did not survive until game ends, mission failed'
            })
            self.signal_mission_failure()
        # verify how many players still alive
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': {self.gs.players[self.target_player].name: 's'},
            'misProgDesp': 'Target still alive, mission continue'
        }, room=self.player)
        
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
        # check if target players are dead
        c = 0
        for target in self.target_players:
            if target in self.gs.kill_logs:
                # someone else killed the target
                if self.gs.kill_logs[target] not in [self.player, 'MF']:
                    # signal death
                    self.update_tracker_view({'misProgDesp': 'bounty failed, someone else killed the player'})
                    self.signal_mission_failure()
                    return
                else:
                    self.update_tracker_view({'targets': {self.gs.players[target].name: 's'}})
                    c += 1
            else:
                self.update_tracker_view({'targets': {self.gs.players[target].name: 'f'}})
        if c == len(self.target_players):
            # signal end
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
        
class Unifier(Mission):
    def __init__(self, player, gs):
        super().__init__("Unifier", player, gs)
        self.target_continent = random.choice(list(gs.map.conts.keys()))
        self.target_round = 0
        l = len(gs.map.conts[self.target_continent]['trtys'])
        if l <= 5:
            self.target_round = 7
        elif l <= 10:
            self.target_round = 5
        else:
            self.target_round = 3
        self.round = 0
        self.type = 'r_based'
    
    def own_target_cont(self, ):
        return self.gs.map.own_continent(self.gs.players[self.player].territories, self.gs.map.conts[self.target_continent]['trtys'])

    def check_conditions(self, ):
        if not self.own_target_cont():
            self.round = -1
            self.update_tracker_view({
            'targets': {self.target_continent: 'f'},
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Successfully controlled {self.target_continent} for {0}/{self.target_round} consecutive rounds'
            })
        else:
            self.update_tracker_view({'targets': {self.target_continent: 'f'}})
    
    def check_round_condition(self, ):
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

class Polarizer(Mission):
    def __init__(self, player, gs):
        super().__init__("Polarizer", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 5

    def no_unification(self,):
        for cont in self.gs.map.conts:
            for p in self.gs.players:
                if self.gs.map.own_continent(self.gs.players[p].territories, self.gs.map.conts[cont]['trtys']):
                    return False
        return True

    def check_conditions(self, ):
        if not self.no_unification(self, ):
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'{0}/{self.target_round} consecutive rounds without continental unification'})
    
    def check_round_condition(self,):
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

class Fanatic(Mission):
    def __init__(self, player, gs):
        super().__init__("Fanatic", player, gs)
        self.type = 'r_based'
        self.round = 0
        m = len(gs.map.territories)
        self.targets = random.sample([i for i in range(m)], 7)
        self.target_round = 5
    
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
        # verify if player owns the targets
        if not self.own_all_targets():
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Controlled target territories for {0}/{self.target_round} consecutive rounds',})
    
    def check_round_condition(self, ):
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

class Industrialist(Mission):
    def __init__(self, player, gs):
        super().__init__("Industrialist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 5

    def check_conditions(self, ):
        if self.gs.TIP != self.player:
            self.round = -1
            self.update_tracker_view({
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Being the most industrailized player for {0}/{self.target_round} consecutive rounds',
            })
    
    def check_round_condition(self, ):
        if self.gs.TIP == self.player:
            self.round += 1
            self.update_tracker_view({
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Being the most industrailized player for {self.round}/{self.target_round} consecutive rounds',
            })
            if self.round == self.target_round:
                # signal end
                self.signal_mission_success()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Being the most industrailized player for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

class Expansionist(Mission):
    def __init__(self, player, gs):
        super().__init__("Expansionist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 5

    def check_conditions(self, ):
        if self.gs.MTO != self.player:
            self.round = -1
            self.update_tracker_view({
            'misProgBar': [0, self.target_round],
            'misProgDesp': f'Controlled the most territories for {0}/{self.target_round} consecutive rounds',
            })

    def check_round_condition(self, ):
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

class Populist(Mission):
    def __init__(self, player, gs):
        super().__init__("Populist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 5

    def check_conditions(self, ):
        # verify if player holds LAO title
        if self.gs.LAO != self.player:
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Holding the largest army for {0}/{self.target_round} consecutive rounds',})

    def check_round_condition(self, ):
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
        
class Dominator(Mission):
    def __init__(self, player, gs):
        super().__init__("Dominator", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 3

    def check_conditions(self, ):
        # verify if player holds SUP title
        if self.gs.SUP != self.player:
            self.round = -1
            self.update_tracker_view({'misProgBar': [0, self.target_round],
            'misProgDesp': f'Exercising supremacy for {0}/{self.target_round} consecutive rounds',})

    def check_round_condition(self, ):
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