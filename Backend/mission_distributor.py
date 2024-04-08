from missions import *
import random

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
        self.self_wins = ['Loy', 'Gua', 'Bon']
        self.missions = [
            'Pac', 'War', 'Loy', 'Bon',
            'Uni', 'Pol', 'Fan', 'Ind',
            'Exp', 'Pop', 'Dom', 'Gua'
        ]

    def validate_mission_set(self, miss_set):
        for m in miss_set:
            if m in self.self_wins:
                return True
            if m in self.dup_con and miss_set.count(m) > 1:
                return True
        for nc in self.nat_con:
            if all(m in nc for m in miss_set):
                return True
        return False

    def get_mission_set(self, num_p):
        miss_set = []
        done = False
        cl, cg = 0, 0
        while not done:
            choice = random.choice(self.missions)
            if choice == 'Loy' and not cl:
                miss_set.append(choice)
                cl += 1
            elif choice == 'Gua' and not cg:
                miss_set.append(choice)
                cg += 1
            else:
                miss_set.append(choice)
            if len(miss_set) == num_p:
                if self.validate_mission_set(miss_set):
                    return miss_set
                miss_set = []
    
    