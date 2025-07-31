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

    def signal_mission_success(self, win_type="solo"):
        if win_type == "solo":
            self.gs.GES.halt_events()
        elif win_type == "gam":
            self.gs.gambler_win = True
        else:
            self.gs.round_based_win = True
        return

    def set_up_tracker_view(self, ):
        raise NotImplementedError("Subclasses must implement set_up method")

    def end_game_checking(self, ):
        raise NotImplementedError("Subclasses must implement end_game_checking method")
    
    def end_game_global_peace_checking(self, ):
        raise NotImplementedError("Subclasses must implement end_game_checking method")

    def update_tracker_view(self, updates):
        self.gs.server.emit('update_tracker', updates, room=self.player)

    def signal_mission_failure(self, ):
        if self.gs.players[self.player].alive:
            self.gs.players[self.player].alive = False
            if self.gs.players[self.player].skill:
                self.gs.players[self.player].skill.active = False
                if self.gs.players[self.player].skill.name == 'Collusion':
                    self.gs.players[self.player].skill.secret_control_list = []
                    self.gs.get_TIP()
                    self.gs.update_player_stats()
                    self.gs.get_SUP()
                    self.gs.update_global_status()
                    self.gs.signal_MTrackers('indus')
                if self.gs.players[self.player].skill.name == 'Loan Shark':
                    for debtor in self.gs.players[self.player].skill.loan_list:
                        self.gs.players[debtor].hijacked = False
                        if self.gs.players[debtor].skill:
                            self.gs.players[debtor].skill.active = True
                        self.gs.server.emit('debt_off', room=debtor)
            for player in self.gs.players:
                curr_p = self.gs.players[player]
                if curr_p.skill:
                    if curr_p.skill.name == 'Loan Shark':
                        if self.player in curr_p.skill.loan_list:
                            curr_p.skill.handle_payment(self.player, 'sepauth')
                            curr_p.skill.handle_payment(self.player, 'troops')
                            if self.player in curr_p.skill.loan_list:
                                del curr_p.skill.loan_list[self.player]
                            self.gs.server.emit('debt_off', room=self.player)
            self.gs.GES.flush_concurrent_event(self.player)
            self.gs.perm_elims.append(self.player)
            if self.name != "Guardian":
                self.gs.death_logs[self.player] = 'MF'
                self.gs.signal_MTrackers('death')
                self.gs.get_TIP()
                self.gs.get_HIP()
                self.gs.get_MTO()
                self.gs.get_LAO()
                self.gs.get_SUP()
                self.gs.egt.determine_end_game(self.gs)
            else:
                self.gs.get_TIP()
                self.gs.get_HIP()
                self.gs.get_MTO()
                self.gs.get_LAO()
                self.gs.get_SUP()


class Pacifist(Mission):

    def __init__(self, player, gs):
        super().__init__("Pacifist", player, gs)
        self.death_count = 0
        self.round = 0
        self.type = 'r_based'
        self.max_death_count = math.floor(len(gs.pids)/2)
        #self.goal_round = 8
        self.goal_round = 7

    def check_conditions(self,):
        if not self.gs.players[self.player].alive:
            return
        dc = len(self.gs.perm_elims)
        if dc > self.death_count:
            self.round = 0
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
            self.signal_mission_success("round")

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
    
    def end_game_global_peace_checking(self, ):
        return self.round == self.goal_round

class Warmonger(Mission):
    def __init__(self, player, gs):
        super().__init__("Warmonger", player, gs)
        self.goal_count = len(self.gs.pids)//3
        self.goal_count = 2 if len(self.gs.pids) == 5 else self.goal_count
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
            self.death_count = dc
            # Signal update
            self.update_tracker_view({
                'misProgBar': [self.death_count, self.goal_count],
                'misProgDesp': f'{self.death_count}/{self.goal_count} personal kills until mission success',
            })
        if self.death_count == self.goal_count:
            # signal end
            self.signal_mission_success()
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.death_count, self.goal_count],
            'misProgDesp': f'{self.death_count}/{self.goal_count} personal kills until mission success',
        }, room=self.player)

    def end_game_checking(self, ):

        # count personal kill        
        dc = 0
        for d in self.gs.death_logs:
            if self.player == self.gs.death_logs[d]:
                dc += 1
        self.death_count = dc

        return self.death_count == self.goal_count and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
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
        # you forgot to check this condition
        if self.target_player is not None:
            return
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
    
    def end_game_global_peace_checking(self, ):
        return self.exactly_two_players_left()
        
class Bounty_Hunter(Mission):
    def __init__(self, player, gs):
        super().__init__("Bounty_Hunter", player, gs)
        self.target_players = None
        numt = 0
        nump = len(gs.pids)
        if nump < 5:
            numt = 1
        elif nump < 8:
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
    
    def end_game_global_peace_checking(self, ):
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
        if not self.gs.players[self.player].alive:
            return
        if not self.own_target_cont():
            self.round = 0
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
            self.signal_mission_success("round")

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': {self.target_continent: 'f'},
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Successfully controlled {self.target_continent} for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)
    
    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.own_target_cont() and self.gs.players[self.player].alive

class Polarizer(Mission):
    def __init__(self, player, gs):
        super().__init__("Polarizer", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 3

    def no_unification(self,):
        for cont in self.gs.map.conts:
            for p in self.gs.players:
                if self.gs.map.own_continent(self.gs.players[p].territories, self.gs.map.conts[cont]['trtys']) and p != self.player:
                    return False
        return True

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if not self.no_unification():
            self.round = 0
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
            self.signal_mission_success("round")
        
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'{self.round}/{self.target_round} consecutive rounds without continental unification',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive

    def end_game_global_peace_checking(self, ):
        return self.no_unification() and self.gs.players[self.player].alive

class Fanatic(Mission):
    def __init__(self, player, gs):
        super().__init__("Fanatic", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 5
        self.targets = []

    def set_targets(self, ):
        m = len(self.gs.map.territories)
        if len(self.targets) == 0:
            self.targets = random.sample([i for i in range(m)], 4)
        else:
            while len(self.targets) < 4:
                target = random.randint(0, m-1)
                if target not in self.targets:
                    self.targets.append(target)
        for miss in self.gs.Mset:
            if miss.name == "Fanatic":
                if len(miss.targets) < 4:
                    for t in self.targets:
                        if t not in miss.targets:
                            miss.targets.append(t)
                            break
                else:
                    for t in self.targets:
                        if t not in miss.targets:
                            miss.targets[random.randint(0, 3)] = t
                            break
                    for t in miss.targets:
                        if t not in self.targets:
                            self.targets[random.randint(0, 3)] = t
                            break
    
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
            self.round = 0
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
                self.signal_mission_success("round")
                
    def set_up_tracker_view(self, ):
        targets = {}
        print(self.targets)
        self.gs.server.emit('mod_targets_to_capture', {'targets': self.targets}, room=self.player)
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
    
    def end_game_global_peace_checking(self, ):
        return self.own_all_targets() and self.gs.players[self.player].alive

class Industrialist(Mission):
    def __init__(self, player, gs):
        super().__init__("Industrialist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 4

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.TIP != self.player:
            self.round = 0
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
                self.signal_mission_success("round")

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Being the most industrialized player for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.gs.TIP == self.player and self.gs.players[self.player].alive

class Expansionist(Mission):
    def __init__(self, player, gs):
        super().__init__("Expansionist", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 4

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.gs.MTO != self.player:
            self.round = 0
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
                self.signal_mission_success("round")
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Controlled the most territories for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.gs.MTO == self.player and self.gs.players[self.player].alive

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
            self.round = 0
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
                self.signal_mission_success("round")
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Holding the largest army for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.gs.LAO == self.player and self.gs.players[self.player].alive
        
class Dominator(Mission):
    def __init__(self, player, gs):
        super().__init__("Dominator", player, gs)
        self.type = 'r_based'
        self.round = 0
        self.target_round = 3

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # verify if player holds SUP title
        if self.gs.SUP != self.player:
            self.round = 0
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
                self.signal_mission_success("round")
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.target_round],
            'misProgDesp': f'Exercising supremacy for {self.round}/{self.target_round} consecutive rounds',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.target_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.gs.SUP == self.player and self.gs.players[self.player].alive

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
    
    def end_game_global_peace_checking(self, ):
        return self.gs.players[self.player].alive
    
class Decapitator(Mission):
    def __init__(self, player, gs):
        super().__init__("Decapitator", player, gs)
        self.target_players = None
        numt = 0
        nump = len(gs.pids)
        numt = nump//2
        numt = numt if numt > 2 else 2
        if len(gs.pids) > 3 and numt == 2:
            numt += 1
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
    
    def end_game_global_peace_checking(self, ):
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
        if m > 85:
            self.target_chases += 3
        elif m > 65:
            self.target_chases += 2
        elif m > 40:
            self.target_chases += 1

        self.round = 0
        self.death_round = 8

    def set_up_tracker_view(self, ):
        self.gs.server.emit('mod_targets_to_capture', {'targets': [self.curr_target]}, room=self.player)
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
                    self.gs.server.emit('mod_targets_to_capture', {'targets': [self.curr_target]}, room=self.player)
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
    
    def end_game_global_peace_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        return self.chase_completed == self.target_chases or len(self.gs.players[self.player].territories) == len(self.gs.map.territories)

class Duelist(Mission):
    def __init__(self, player, gs):
        super().__init__("Duelist", player, gs)
        self.target_player = None

    def set_nemesis(self,):
        if self.target_player is not None:
            return
        for miss in self.gs.Mset:
            if miss.name == "Duelist":
                if miss.player != self.player and miss.target_player is None:
                    miss.target_player = self.player
                    self.target_player = miss.player
                    return

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        # check if target player is dead
        if self.target_player in self.gs.perm_elims:
            if self.gs.death_logs[self.target_player] != self.player:
                self.update_tracker_view({'misProgDesp': 'Failed to kill your nemesis'})
                self.signal_mission_failure()
            else:
                self.update_tracker_view({'targets': {self.gs.players[self.target_player].name: 's'}})
                self.update_tracker_view({'misProgDesp': 'Nemesis eliminated'})
                self.signal_mission_success()

    def set_up_tracker_view(self, ):
        targets = {}
        targets[self.gs.players[self.target_player].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgDesp': 'Kill your nemesis!'
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.target_player in self.gs.perm_elims:
            if self.gs.death_logs[self.target_player] != self.player:
                return False
            else:
                return True
        return False
    
    def end_game_global_peace_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.target_player in self.gs.perm_elims:
            if self.gs.death_logs[self.target_player] != self.player:
                return False
            else:
                return True
        return False

class Punisher(Mission):
    def __init__(self, player, gs):
        super().__init__("Punisher", player, gs)
        self.targets = ['Punisher', 'Duelist', 'Starchaser', 'Decapitator', 'Bounty_Hunter', 'Warmonger', 'Pacifist', 'Loyalist', "Survivalist", "Protectionist", "Assassin", "Annihilator"]

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return

        c = 0
        for miss in self.gs.Mset:
            if miss.name in self.targets:
                if miss.player in self.gs.perm_elims:
                    if self.gs.death_logs[miss.player] == self.player:
                        self.update_tracker_view({'misProgDesp': 'Justice served!'})
                        self.signal_mission_success()
                        return
                else:
                    c += 1

        if c == 0:
            self.update_tracker_view({'misProgDesp': 'No more justice to be served!'})
            self.signal_mission_failure()

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgDesp': 'Bring judgement to the sinners! Kill at least 1 non-C class agenda holder.'
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        for miss in self.gs.Mset:
            if miss.name in self.targets:
                if miss.player in self.gs.perm_elims:
                    if self.gs.death_logs[miss.player] == self.player:
                        return True
        return False
    
    def end_game_global_peace_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        for miss in self.gs.Mset:
            if miss.name in self.targets:
                if miss.player in self.gs.perm_elims:
                    if self.gs.death_logs[miss.player] == self.player:
                        return True
        return False

class Survivalist(Mission):
    def __init__(self, player, gs):
        super().__init__("Survivalist", player, gs)
        self.round = 0
        self.type = 'r_based'
        self.goal_round = 8

    def check_conditions(self,):
        if not self.gs.players[self.player].alive:
            self.signal_mission_failure()
            self.update_tracker_view({
                'misProgBar': [self.round, self.goal_round],
                'misProgDesp': f'You are eliminated. Agenda failed.',
            })
            return
    
    def check_round_condition(self, ):
        if not self.gs.players[self.player].alive:
            return
        self.round += 1
        self.update_tracker_view({
            'misProgBar': [self.round, self.goal_round],
            'misProgDesp': f'Stay alive until the very end! Survived {self.round}/{self.goal_round} rounds.',
            })
        if self.round == self.goal_round:
            # signal end
            self.signal_mission_success("round")

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.round, self.goal_round],
            'misProgDesp': f'Stay alive until the very end! Survived {self.round}/{self.goal_round} rounds.',
        }, room=self.player)

    def end_game_checking(self, ):
        return self.round == self.goal_round and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.gs.players[self.player].alive
    
class Assassin(Mission):
    def __init__(self, player, gs):
        super().__init__("Assassin", player, gs)
        self.target_player = None
        self.nemesis = None

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.target_player in self.gs.death_logs:
            if self.player == self.gs.death_logs[self.target_player]:
                self.update_tracker_view({'targets': {self.gs.players[self.target_player].name: 's'}})
                self.update_tracker_view({'misProgDesp': 'Target Eliminated!'})
                self.signal_mission_success()
            else:
                self.update_tracker_view({'targets': {self.gs.players[self.target_player].name: 'f'}})
                self.signal_mission_failure()
        else:
            self.update_tracker_view({'targets': {self.gs.players[self.target_player].name: 'f'}})

    def set_up_tracker_view(self, ):
        targets = {}
        targets[self.gs.players[self.target_player].name] = 'f'
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'targets': targets,
            'misProgDesp': f'Your need to eliminate {self.gs.players[self.target_player].name}. Their bodyguard is {self.gs.players[self.nemesis].name}.'
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.target_player in self.gs.death_logs:
            return self.player == self.gs.death_logs[self.target_player]
        else:
            return False
    
    def end_game_global_peace_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.target_player in self.gs.death_logs:
            return self.player == self.gs.death_logs[self.target_player]
        else:
            return False
        
    def set_targets(self):
        if self.target_player is not None or self.nemesis is not None:
            return  # Already assigned

        for m in self.gs.Mset:
            if m.name == 'Protectionist' and m.target_player is None and m.protection is None:
                candidates = [
                    p for p in self.gs.players
                    if p != self.player and p != m.player and self.gs.players[p].alive
                ]
                if not candidates:
                    return

                random_target = random.choice(candidates)

                # Assign values
                self.target_player = random_target
                self.nemesis = m.player

                m.protection = random_target
                m.target_player = self.player
                return
    
class Protectionist(Mission):
    def __init__(self, player, gs):
        super().__init__("Protectionist", player, gs)
        self.target_player = None
        self.protection = None

    def check_conditions(self, ):
        if not self.gs.players[self.player].alive:
            return
        if self.protection in self.gs.perm_elims:
            self.update_tracker_view({'misProgDesp': 'Failed to protect your target!'})
            self.signal_mission_failure()
        if self.target_player in self.gs.death_logs:
            if self.player == self.gs.death_logs[self.target_player]:
                self.update_tracker_view({'misProgDesp': 'Killer Eliminated!'})
                self.signal_mission_success()
            else:
                self.update_tracker_view({'misProgDesp': 'Failed to kill the assassin!'})
                self.signal_mission_failure()

    def set_up_tracker_view(self, ):
        target_mission = None
        for m in self.gs.Mset:
            if m.player == self.protection:
                target_mission = m.name
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgDesp': f"Your need to prevent your target from getting eliminated until you personally killed the assassin. Your target's agenda is {target_mission}."
        }, room=self.player)

    def end_game_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.protection in self.gs.perm_elims:
            return False
        if self.target_player in self.gs.death_logs:
            if self.player == self.gs.death_logs[self.target_player]:
                return True
            else:
                return False
        return False
    
    def end_game_global_peace_checking(self, ):
        if not self.gs.players[self.player].alive:
            return False
        if self.protection in self.gs.perm_elims:
            return False
        if self.target_player in self.gs.death_logs:
            if self.player == self.gs.death_logs[self.target_player]:
                return True
            else:
                return False
        return False
    
    def set_targets(self):
        if self.target_player is not None or self.protection is not None:
            return  # Already assigned

        for m in self.gs.Mset:
            if m.name == 'Assassin' and m.target_player is None and m.nemesis is None:
                # Find a random player who is not the assassin or Protectionist mission holders
                candidates = [
                    p for p in self.gs.players
                    if p != self.player and p != m.player and self.gs.players[p].alive
                ]
                if not candidates:
                    return  # No valid players to assign

                random_target = random.choice(candidates)

                # Assign values
                m.target_player = random_target
                m.nemesis = self.player

                self.protection = random_target
                self.target_player = m.player
                return
            
class Gambler(Mission):
    def __init__(self, player, gs):
        super().__init__("Gambler", player, gs)
        self.target_troops = len(self.gs.map.territories) - 20
        self.curr_troops = 0
    
    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgBar': [self.curr_troops, self.target_troops],
            'misProgDesp': f'Killed {self.curr_troops}/{self.target_troops} troops during successful conquests while sending less troops than the opponents.',
        }, room=self.player)
    
    def check_conditions(self, value=0):
        if not self.gs.players[self.player].alive:
            return
        self.curr_troops += value
        if self.curr_troops >= self.target_troops:
            self.curr_troops = self.target_troops
        self.update_tracker_view({
            'misProgBar': [self.curr_troops, self.target_troops],
            'misProgDesp': f'Successfully killed {self.curr_troops}/{self.target_troops} troops during offense while sending less troops than opponents.',
        })
        if self.curr_troops >= self.target_troops:
            self.signal_mission_success("gam")

    def end_game_checking(self, ):
        return self.curr_troops >= self.target_troops and self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        return self.curr_troops >= self.target_troops and self.gs.players[self.player].alive
    
class Opportunist(Mission):
    def __init__(self, player, gs):
        super().__init__("Opportunist", player, gs)
        
    def check_conditions(self):
        if not self.gs.players[self.player].alive:
            self.signal_mission_failure()
            self.update_tracker_view({
                'misProgDesp': 'You are eliminated. Agenda failed.'
            })
            return
        
    def set_up_tracker_view(self):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgDesp': 'Stay alive until another player wins!'
        }, room=self.player)

    def end_game_checking(self):
        return self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self):
        return self.gs.players[self.player].alive
    
class Annihilator(Mission):
    def __init__(self, player, gs):
        super().__init__("Annihilator", player, gs)
        gs.Annihilator = player

    def check_conditions(self,):
        if not self.gs.players[self.player].alive:
            self.signal_mission_failure()
            self.update_tracker_view({
                'misProgDesp': f'There are players that are still alive, annilation failed.',
            })
            return

    def set_up_tracker_view(self, ):
        self.gs.server.emit('initiate_tracker', {
            'title': self.name,
            'misProgDesp': f'DESTROY ALL OTHER PLAYERS AND BE THE LAST ONE STANDING!',
        }, room=self.player)

    def end_game_checking(self, ):
        for p, player in self.gs.players.items():
            if p != self.player and player.alive:
                return False
        return self.gs.players[self.player].alive
    
    def end_game_global_peace_checking(self, ):
        for p, player in self.gs.players.items():
            if p != self.player and player.alive:
                return False
        return self.gs.players[self.player].alive