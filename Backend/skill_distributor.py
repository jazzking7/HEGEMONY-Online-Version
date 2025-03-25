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
            "Elitocracy",
            "Necromancer",
            "Divine_Punishment",
            "Air_Superiority",
            "Collusion",
            "Laplace's Demon",
            "Arsenal of the Underworld",
            "Loan Shark",
            "Reaping of Anubis",
            "Pandora's Box",
            "Loopwalker",
            "Revanchism"
        ]

    def get_options(self, ):
        return random.sample(self.skill_options, k=10)
    
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
        elif skill_name == "Elitocracy":
            return Elitocracy(player, gs)
        elif skill_name == "Necromancer":
            return Necromancer(player, gs)
        elif skill_name == "Divine_Punishment":
            return Divine_Punishment(player, gs)
        elif skill_name == "Air_Superiority":
            return Air_Superiority(player, gs)
        elif skill_name == "Collusion":
            return Collusion(player, gs)
        elif skill_name == "Laplace's Demon":
            return Laplace_Demon(player, gs)
        elif skill_name == "Arsenal of the Underworld":
            return Arsenal_of_the_Underworld(player, gs)
        elif skill_name == "Loan Shark":
            return Loan_Shark(player, gs)
        elif skill_name == "Reaping of Anubis":
            return Reaping_of_Anubis(player, gs)
        elif skill_name == "Pandora's Box":
            return Pandora_Box(player, gs)
        elif skill_name == "Loopwalker":
            return Loopwalker(player, gs)
        elif skill_name == "Revanchism":
            return Revanchism(player, gs)