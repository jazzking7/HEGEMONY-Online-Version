from skills import *

class Skill_Distributor:

    def __init__(self,):
        
        self.skill_options = [
            "Iron_Wall",
            "Realm_of_Permafrost",
            "Dictator",
            "Mass_Mobilization",
            "Industrial_Revolution",
            "Robinhood",
            "Ares' Blessing",
            "Zealous_Expansion",
            "Frameshifter",
            "Necromancer",
            "Divine_Punishment"
        ]

    def get_options(self, ):
        return random.sample(self.skill_options, k=9)
    
    def get_single_option(self, ):
        return random.choice(self.skill_options)
    
    def initiate_skill(self, skill_name, player, gs):
        if skill_name == 'Iron_Wall':
            return Iron_Wall(player, gs)
        elif skill_name == 'Realm_of_Permafrost':
            return Realm_of_Permafrost(player, gs)
        elif skill_name == 'Dictator':
            return Dictator(player, gs)
        elif skill_name == 'Mass_Mobilization':
            return Mass_Mobilization(player, gs)
        elif skill_name == 'Industrial_Revolution':
            return Industrial_Revolution(player, gs)
        elif skill_name == 'Robinhood':
            return Robinhood(player, gs)
        elif skill_name == "Ares' Blessing":
            return Ares_Blessing(player, gs)
        elif skill_name == "Zealous_Expansion":
            return Zealous_Expansion(player, gs)
        elif skill_name == "Frameshifter":
            return Frameshifter(player, gs)
        elif skill_name == "Necromancer":
            return Necromancer(player, gs)
        elif skill_name == "Divine_Punishment":
            return Divine_Punishment(player, gs)