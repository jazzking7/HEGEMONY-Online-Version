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
    
    def get_skill_description(self, skill_name, gs):
        if skill_name == 'Iron_Wall':
            return "Defensive War Art that deals at least 2 times the damage to attackers and have a 30 percent chance to block each incoming damage. The stronger your opponent the stronger your defense."
        elif skill_name == 'Realm_of_Permafrost':
            return "Ignore all stats during battles. Able to launch Ice Age that lasts 2 rounds using 2★. Ice Age significantly reduces enemy reinforcement and make them unable to gain Special Authority."
        elif skill_name == 'Dictator':
            return "Every round, you are guaranteed to earn 2★."
        elif skill_name == 'Mass_Mobilization':
            return "Able to summon a large amount of reserves. The weaker you are the more troops will you receive."
        elif skill_name == 'Industrial_Revolution':
            return "Able to build 2 free cities per continent. Get +1 Industrial Level during battles."
        elif skill_name == 'Robinhood':
            return "Able to steal reinforcement and Special Authority from the strongest players."
        elif skill_name == "Ares' Blessing":
            return "Berserker War Art that increase your Industrial and Infrastructure Level by 2 while raising your damage multiplier to 2 when activated. Last for 1 turn and there is a 3 round cooldown between usages."
        elif skill_name == "Zealous_Expansion":
            return "Able to upgrade Infrastructure Level by 1 using 2★ instead of 4★. +1 Infrastructure Level during battles. +2 reserves for every Infrastructure Level increased."
        elif skill_name == "Elitocracy":
            return "Able to increase your Minimum Roll by 1 using 3★. Your damage multiplier increases as your Minimum Roll increases."
        elif skill_name == "Necromancer":
            return "When activated, all enemy troops that you skilled become your reserves. There is a 1 round cooldown between usages."
        elif skill_name == "Divine_Punishment":
            return "Able to bombard anywhere on the map. You receive (number of players + 1) usages at the start of the game. Every 3 rounds you receive 1 additional usage."
        elif skill_name == "Air_Superiority":
            return "Able to jump over territories to attack. The more continents your troops are spreaded out to, the more reserves you will receive per round."
        elif skill_name == "Collusion":
            return "Able to gain secret ownership of enemy territories for 3★. You get 2 free usages at the start of the game."
        elif skill_name == "Laplace's Demon":
            return "Know all players' War Art. Have a list of Secret Agendas that includes every Agenda in game and 2 extra Agendas that are not in game."
        elif skill_name == "Arsenal of the Underworld":
            return "Able to set minefields and build underground missile silo. The higher your battle stats are, the more minefields you can set and the stronger the missiles launched from your silo."
        elif skill_name == "Loan Shark":
            return "Disable a player's War Art, and they have to pay you Special Authority or troops to reactivate their War Art."
        elif skill_name == "Reaping of Anubis":
            return "In battles, you are guaranteed to remove a set amount of troops from enemy forces. The set amount starts from 0 and can be upgraded using Special Authority."
        elif skill_name == "Pandora's Box":
            return "For 2★ you can peek into Pandora's Box, you will get rewards or absolutely nothing."
        elif skill_name == "Loopwalker":
            return f"Time Traveling War Art, you are to run multiple simulations of a battle using time loops and pick the best outcome out of the simulations. You can set how many simulations are run per battle and you have {200*len(gs.players)} time loops available for the whole game."
        elif skill_name == "Revanchism":
            return "When you get attacked, you will accumulate Rage Points. Bonus stats are received when enough Rage Points is accumulated."
    
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