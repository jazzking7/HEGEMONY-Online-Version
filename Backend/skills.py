import math
import random

class Skill:
    
    def __init__(self, name, player, gs):

        self.name = name
        self.player = player
        self.gs = gs

        self.active = True

        self.intMod = False
        self.extMod = False
        self.reactMod = False

        self.hasUsageLimit = False
        self.hasCooldown = False
        self.singleTurnActive = False
        self.hasRoundEffect = False


    def update_current_status(self, ):
        pass

class Realm_of_Permafrost(Skill):

    def __init__(self, player, gs):
        super().__init__("Realm_of_Permafrost", player, gs)
        self.intMod = True
        self.extMod = True

    def internalStatsMod(self, battle_stats):

        battle_stats[0] = 6
        battle_stats[1] = 3


    def externalStatsMod(self, battle_stats):

        battle_stats[0] = 6
        battle_stats[1] = 3

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Realm of Permafrost",
            'description': "In any battle you engage in, the industrial and infrastructure levels of both you and your enemies are ignored.",
            'operational': self.active
        }, room=self.player)

class Iron_Wall(Skill):

    def __init__(self, player, gs):
        super().__init__("Iron_Wall", player, gs)
        self.reactMod = True

    def reactStatsMod(self, ownStats, enemyStats, attacking):
        if not attacking:

            ownStats[3] = 40
            ownStats[4] = 2

            disparity = (enemyStats[0] - ownStats[0]) + (enemyStats[1] - ownStats[1])

            if disparity > 3:
                ownStats[3] += 20
                ownStats[4] += 1
            elif disparity > 2:
                ownStats[3] += 10
            elif disparity > 1:
                ownStats[3] += 5
    
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Iron Wall",
            'description': "At least 40% nullification rate and x2 damage output in defense. The stronger the opponent, the higher the defense.",
            'operational': self.active
        }, room=self.player)

class Dictator(Skill):

    def __init__(self, player, gs):
        super().__init__("Dictator", player, gs)

    def get_additional_stars(self,):
        if self.active:
            self.gs.players[self.player].stars += 2

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': self.name,
            'description': "Gain a minimum of 2 stars per turn regardless of successful conquests.",
            'operational': self.active
        }, room=self.player)

class Mass_Mobilization(Skill):

    def __init__(self, player, gs):
        super().__init__("Mass_Mobilization", player, gs)
        self.hasUsageLimit = True
        self.hasCooldown = True
        self.hasRoundEffect = True

        self.limit = 0
        nump = len(gs.players)
        if nump <= 6:
            self.limit = 2
        elif nump <= 9:
            self.limit = 3
        elif nump <= 12:
            self.limit = 4
        else:
            self.limit = 5
        
        self.cooldown = 0

    def apply_round_effect(self,):
        if self.cooldown:
            self.cooldown -= 1

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Mass Mobilization",
            'description': "Mobilize enormous amount of reserves, exact number depends your power index. Lower the power index, higher the amount",
            'operational': self.active,
            'hasLimit': self.hasUsageLimit,
            'limits': self.limit,
            'cooldown': self.cooldown,
            'btn_msg': "Activate Mobilization"
        }, room=self.player)

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if self.limit == 0:
            self.gs.server.emit('display_new_notification', {'msg': "Limit reached!"}, room=self.player)
            return
        if self.cooldown:
            self.gs.server.emit('display_new_notification', {'msg': "Still in cooldown!"}, room=self.player)
            return
        
        # compute average PPI
        # compute global troop amount
        total_PPI = 0
        total_troops = 0
        for p in self.gs.players:
            total_PPI += self.gs.players[p].PPI
            total_troops += self.gs.players[p].total_troops
        
        avg_PPI = total_PPI/len(self.gs.players)
        
        # difference in power
        diff = self.gs.players[self.player].PPI - avg_PPI

        # increase reserves
        if diff < -10:
            self.gs.players[self.player].reserves += math.ceil(0.23*total_troops)
        elif diff < -5:
            self.gs.players[self.player].reserves += math.ceil(0.2*total_troops)
        elif diff < 0:
            self.gs.players[self.player].reserves += math.ceil(0.17*total_troops)
        elif diff < 5:
            self.gs.players[self.player].reserves += math.ceil(0.15*total_troops)
        elif diff < 10:
            self.gs.players[self.player].reserves += math.ceil(0.12*total_troops)
        else:
            self.gs.players[self.player].reserves += math.ceil(0.1*total_troops)

        # update private view
        self.gs.update_private_status(self.player)

        # update limits and cooldown
        self.limit -= 1
        self.cooldown = 3

class Industrial_Revolution(Skill):

    def __init__(self, player, gs):
        super().__init__("Industrial_Revolution", player, gs)
        self.intMod = True
        
        self.finish_building = True
        self.freeCityTracker = {}

        for cont in self.gs.map.conts:
            self.freeCityTracker[cont] = 0

    def internalStatsMod(self, battle_stats):
        battle_stats[0] += 1

    def update_current_status(self):

        ft = []
        for cont in self.freeCityTracker:
            if self.freeCityTracker[cont]:
                ft.append(cont)

        self.gs.server.emit("update_skill_status", {
            'name': "Industrial Revolution",
            'description': "Can build 1 city for free per continent, +1 industrial power in battles",
            'operational': self.active,
            'forbidden_targets': ft,
            'ft_msg': "Free city already built in:",
            'hasLimit': True,
            'limits': len(self.freeCityTracker) - len(ft),
            'btn_msg': "Activate rapid industrialization"
        }, room=self.player) 

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": "War art disabled!"}, room=self.player)
            return
        self.gs.GES.handle_async_event({'name': 'BFC'}, self.player)

    def validate_and_apply_changes(self, data):
        
        choices = data['choice']

        # too many cities
        if len(choices) > len(self.freeCityTracker):
            self.gs.server.emit("display_new_notification", {"msg": f"Selected more than allowed amount of cities!"}, room=self.player)
            return

        tmp_count = {}

        # already built on continent
        for choice in choices:
            if self.gs.map.territories[choice].isCity:
                self.gs.server.emit("display_new_notification", {"msg": f"Selected a territory that already has a city!"}, room=self.player)
                return
            for cont in self.gs.map.conts:
                if choice in self.gs.map.conts[cont]['trtys']:
                    if cont not in tmp_count:
                        tmp_count[cont] = 1
                    else:
                        self.gs.server.emit("display_new_notification", {"msg": f"Multiple selections on {cont}!"}, room=self.player)
                        return
                    if self.freeCityTracker[cont]:
                        self.gs.server.emit("display_new_notification", {"msg": f"Already built free city on {cont}!"}, room=self.player)
                        return

        # apply changes
        for choice in choices:
            self.gs.map.territories[choice].isCity = True
            self.gs.server.emit('update_trty_display', {choice: {'hasDev': 'city'}}, room=self.gs.lobby)
            for cont in self.gs.map.conts:
                # Update free city tracker
                if choice in self.gs.map.conts[cont]['trtys']:
                    self.freeCityTracker[cont] += 1
        
        self.gs.update_TIP(self.player)
        self.gs.get_SUP()
        self.gs.update_global_status()
        self.gs.signal_MTrackers('indus')
        
        # terminate building
        self.finish_building = True

class Robinhood(Skill):

    def __init__(self, player, gs):
        super().__init__("Robinhood", player, gs)
        self.hasRoundEffect = True
        self.targets = []
        self.top_nump = 0
        l = len(gs.players)
        if l < 5:
            self.top_nump = 1
        elif l < 10:
            self.top_nump = 2
        elif l < 16:
            self.top_nump = 3

    def apply_round_effect(self,):
        self.targets = []
        if self.active:
            # Sort players by their PPI values in descending order and get the top 2 players
            top2Players = sorted(self.gs.players.items(), key=lambda item: item[1].PPI, reverse=True)[:self.top_nump]  # items -> item[0] = key   item[1] = value
            # Extract the player sids from the top 2 players
            self.targets = [player[0] for player in top2Players]
    
    def leech_off_reinforcements(self, amt):
        if self.active:
            
            l_amt = amt//3
            self.gs.players[self.player].reserves += l_amt
            self.gs.update_private_status(self.player)

            amt -= l_amt
            return amt
        
    def leech_off_stars(self, amt):
        if self.active:
            
            l_amt = 0
            if amt > 1:
                l_amt = 1

            self.gs.players[self.player].stars += l_amt
            self.gs.update_private_status(self.player)

            amt -= l_amt
            return amt
        
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Robinhood",
            'description': "Take away resources from the top 2 strongest players to give to yourself",
            'operational': self.active
        }, room=self.player)