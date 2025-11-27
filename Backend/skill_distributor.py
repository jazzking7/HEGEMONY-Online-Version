from skills import *

class Skill_Distributor:

    def __init__(self,):
        
        self.skill_options = [
            "Iron_Wall",
            "Dictator",
            "Mass Mobilization",
            "Industrial_Revolution",
            "Ares' Blessing",
            "Zealous_Expansion",
            "Elitocracy",
            "Divine_Punishment",
            "Robinhood",
            "Realm_of_Permafrost",
            "Necromancer",
            "Air_Superiority",
            "Collusion",
            "Laplace's Demon",
            "Arsenal of the Underworld",
            "Loan Shark",
            "Reaping of Anubis",
            "Pandora's Box",
            "Loopwalker",
            "Revanchism",
            "Archmage",
            "Pillar of Immortality",
            "Babylon"
        ]

        self.beginner = [ 
            "Iron_Wall", "Dictator", "Mass Mobilization", "Industrial_Revolution", 
            "Ares' Blessing", "Zealous_Expansion", "Elitocracy", "Divine_Punishment"
            ]
        self.intermediate = [ 
            "Iron_Wall", "Dictator", "Mass Mobilization", "Industrial_Revolution", 
            "Ares' Blessing", "Zealous_Expansion", "Elitocracy", "Divine_Punishment",
            "Robinhood", "Realm_of_Permafrost", "Necromancer", "Air_Superiority"
            ]
        self.pro = [ 
            "Iron_Wall", "Dictator", "Mass Mobilization", "Industrial_Revolution", 
            "Ares' Blessing", "Zealous_Expansion", "Elitocracy", "Divine_Punishment",
            "Robinhood", "Realm_of_Permafrost", "Necromancer", "Air_Superiority",
            "Collusion", "Laplace's Demon", "Arsenal of the Underworld", "Loan Shark"
            ]
        self.master = [ 
            "Iron_Wall", "Dictator", "Mass Mobilization", "Industrial_Revolution", 
            "Ares' Blessing", "Zealous_Expansion", "Elitocracy", "Divine_Punishment",
            "Robinhood", "Realm_of_Permafrost", "Necromancer", "Air_Superiority",
            "Collusion", "Laplace's Demon", "Arsenal of the Underworld", "Loan Shark", 
            "Reaping of Anubis", "Pandora's Box", "Loopwalker", "Revanchism"
            ]

    def get_Annihilator_options(self, ):
        return ['Elitocracy', 'Air_Superiority', 'Dictator', 'Divine_Punishment', 'Necromancer', 'Realm_of_Permafrost', 'Reaping of Anubis', 'Babylon']

    def get_options(self, complexity="pioneer"):
        skill_pool = self.skill_options
        N = 9
        if complexity == 'beginner':
            skill_pool = self.beginner
            N = 5
        elif complexity == 'intermediate':
            skill_pool = self.intermediate
            N = 6
        elif complexity == 'pro':
            skill_pool = self.pro
            N = 7
        elif complexity == 'master':
            skill_pool = self.master
            N = 8
        print(skill_pool)
        return random.sample(skill_pool, k=N)
    
    def get_single_option(self, ):
        return random.choice(self.skill_options)
    
    def get_skill_description(self, skill_name, gs):
        if skill_name == 'Iron_Wall':
            return "Defensive War Art that deals at least 2 times the damage to attackers and have a 30 percent chance to block each incoming damage. The stronger your opponent the stronger your defense."
        elif skill_name == 'Realm_of_Permafrost':
            return "Ignore all stats during battles. Able to launch Ice Age that lasts 2 rounds using 2★. Ice Age significantly reduces enemy reinforcement and make them unable to gain Special Authority."
        elif skill_name == 'Dictator':
            return "Every round, you are guaranteed to earn 2★."
        elif skill_name == 'Mass Mobilization':
            return "Able to summon a large amount of reserves. The weaker you are the more troops will you receive."
        elif skill_name == 'Industrial_Revolution':
            return "Able to build 2 free cities per continent. Get +1 Industrial Level during battles."
        elif skill_name == 'Robinhood':
            return "Able to steal reinforcement and Special Authority from the strongest players."
        elif skill_name == "Ares' Blessing":
            return "Berserker War Art that increase your Industrial and Infrastructure Level by 2 while raising your damage multiplier to 2 when activated. Last for 1 turn and there is a 3 round cooldown between usages."
        elif skill_name == "Zealous_Expansion":
            return "Able to upgrade Infrastructure Level by 1 using 2★ instead of 3★. +1 Infrastructure Level during battles. +5 reserves for every Infrastructure Level increased using this War Art."
        elif skill_name == "Elitocracy":
            return "Able to increase your Minimum Roll by 1 using 3★. Your damage multiplier increases as your Minimum Roll increases."
        elif skill_name == "Necromancer":
            return "When activated, all enemy troops that you killed become your reserves."
        elif skill_name == "Divine_Punishment":
            return "Able to bombard anywhere on the map. You receive usages equivalent to number of players at the start of the game. Every 2 rounds you receive 1 additional usage."
        elif skill_name == "Air_Superiority":
            return "Able to jump over territories to attack. The more continents your troops are spreaded out to, the more reserves and stars you will receive per round."
        elif skill_name == "Collusion":
            return "Able to gain secret ownership of enemy territories. You get at least 2 usages at the start of the game and 1 additional usage every round."
        elif skill_name == "Laplace's Demon":
            return "Know all players' War Art and secret stats, able to use stars to uncover other's Secret Agenda."
        elif skill_name == "Arsenal of the Underworld":
            return "Able to set minefields and build underground missile silo. The higher your battle stats are, the more minefields you can set and the stronger the missiles launched from your silo."
        elif skill_name == "Loan Shark":
            return "Disable a player's War Art, and they have to pay you Special Authority or troops to reactivate their War Art."
        elif skill_name == "Reaping of Anubis":
            return "At the start of every battle, you are guaranteed to destroyed a set amount of troops from enemy forces. The set amount starts from 0 and can be upgraded using Special Authority."
        elif skill_name == "Pandora's Box":
            return "For 2★ you can peek into Pandora's Box, you will get rewards or nothing at all."
        elif skill_name == "Loopwalker":
            return f"Time Traveling War Art, you are to run multiple simulations of a battle using time loops and pick the best outcome out of the simulations. You can set how many simulations are run per battle and you have {200*len(gs.players)} time loops available for the whole game."
        elif skill_name == "Revanchism":
            return "When you get attacked, you will accumulate Rage Points. Bonus stats are received when enough Rage Points are accumulated."
        elif skill_name == "Archmage":
            return "Cost of building Leyline Crosses decrease to 1★. Increased Crit Rate, Crit Damge and Blessings from Leyline Crosses."
        elif skill_name == "Pillar of Immortality":
            return "Able to install Pillars of Immortatlity. When a pillar is stationed on a territory, each troop stationed on that territory counts as 10 troops during battles."
        elif skill_name == "Babylon":
            return "Benefit from multiple randomly selected passives."
        
    def get_quote(self, skill_name, gs):
        if skill_name == 'Iron_Wall':
            return "Impenetrable as steel, unmoving as stone."
        elif skill_name == 'Realm_of_Permafrost':
            return "Nothing fades, nothing grows — all is held in the icy grip of eternity."
        elif skill_name == 'Dictator':
            return "The object of power is power."
        elif skill_name == 'Mass Mobilization':
            return "Quantity is a quality of its own."
        elif skill_name == 'Industrial_Revolution':
            return "Let human ingenuity power a new world order."
        elif skill_name == 'Robinhood':
            return "Strip the wealth of the greedy, fuel the hopes of the needy."
        elif skill_name == "Ares' Blessing":
            return "When war is waged under Ares' watchful eyes, even the smallest force can conquer nations."
        elif skill_name == "Zealous_Expansion":
            return "The road to success is always under construction."
        elif skill_name == "Elitocracy":
            return "Quality of men rules over quantity."
        elif skill_name == "Necromancer":
            return "One who controls the dead commands the living."
        elif skill_name == "Divine_Punishment":
            return "Justice from above, swift and unforgiving."
        elif skill_name == "Air_Superiority":
            return "The one who controls the skies controls the battlefield."
        elif skill_name == "Collusion":
            return "Corrupt the few, and they will corrupt the many."
        elif skill_name == "Laplace's Demon":
            return "The essence of war is not fighting; it is knowing."
        elif skill_name == "Arsenal of the Underworld":
            return "What is hidden is often more powerful than what is seen."
        elif skill_name == "Loan Shark":
            return "Strike at the shepherd, and the sheep will scatter."
        elif skill_name == "Reaping of Anubis":
            return "They fall before the first step is even taken."
        elif skill_name == "Pandora's Box":
            return "Sometimes, there's nothing inside. Sometimes, everything."
        elif skill_name == "Loopwalker":
            return "Every failure is fuel for the perfect loop."
        elif skill_name == "Revanchism":
            return "To be wronged is nothing unless you continue to remember it."
        elif skill_name == "Archmage":
            return "Where others beg the divine, the miracle maker becomes it."
        elif skill_name == "Pillar of Immortality":
            return "Where the gods once stood the pillars now remain."
        elif skill_name == "Babylon":
            return "All treasures return to their origin — and I am the origin."
    def initiate_skill(self, skill_name, player, gs):
        if skill_name == 'Iron_Wall':
            return Iron_Wall(player, gs)
        elif skill_name == 'Realm_of_Permafrost':
            return Realm_of_Permafrost(player, gs)
        elif skill_name == 'Dictator':
            return Dictator(player, gs)
        elif skill_name == 'Mass Mobilization':
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
        elif skill_name == "Archmage":
            return Archmage(player, gs)
        elif skill_name == "Pillar of Immortality":
            return Pillar_of_Immortality(player, gs)
        elif skill_name == 'Babylon':
            return Babylon(player, gs)