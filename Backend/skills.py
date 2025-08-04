import math
import random

# Skill usage button shows when hasLimit, limits, cooldown

class Skill:
    
    def __init__(self, name, player, gs):

        self.name = name
        self.player = player
        self.gs = gs

        self.active = True

        self.intMod = False
        self.extMod = False
        self.reactMod = False

        self.turn_stats_mod = False
        self.hasUsageLimit = False
        self.hasCooldown = False
        self.singleTurnActive = False
        self.hasRoundEffect = False

        self.give_troop_bonus = False
        self.hasTurnEffect = False
        self.out_of_turn_activation = False

    def update_current_status(self, ):
        pass

    def get_skill_status(self, ):
        pass

class Realm_of_Permafrost(Skill):

    def __init__(self, player, gs):
        super().__init__("Realm_of_Permafrost", player, gs)
        self.intMod = True
        self.extMod = True
        self.hasRoundEffect = True
        self.iceAgeCd = 0
        self.Annihilator_as_user = player == gs.Annihilator

    def internalStatsMod(self, battle_stats):

        battle_stats[0] = 6
        battle_stats[1] = 3
        battle_stats[2] = 1
        battle_stats[3] = 0
        battle_stats[4] = 1

    def externalStatsMod(self, battle_stats):

        battle_stats[0] = 6
        battle_stats[1] = 3
        battle_stats[2] = 1
        battle_stats[3] = 0
        battle_stats[4] = 1

        if self.Annihilator_as_user and self.gs.in_ice_age:
            battle_stats[0] = 5
            battle_stats[1] = 3
            battle_stats[2] = 1
            battle_stats[3] = 0
            battle_stats[4] = 1

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": "War art disabled!"}, room=self.player)
            return
        if self.gs.pids[self.gs.GES.current_player] != self.player:
            self.gs.server.emit("display_new_notification", {"msg": "Cannot activate outside your turn!"}, room=self.player)
            return
        if self.gs.players[self.player].stars < 2:
            self.gs.server.emit("display_new_notification", {"msg": "Not enough stars to activate ice age!"}, room=self.player)
            return
        if self.iceAgeCd:
            self.gs.server.emit("display_new_notification", {"msg": "Ice age activation in cooldown!"}, room=self.player)
            return

        self.gs.set_ice_age = True
        self.iceAgeCd = 4 if not self.Annihilator_as_user else 3
        self.gs.players[self.player].stars -= 2
        self.gs.server.emit("display_new_notification", {"msg": "Ice Age Activated!"}, room=self.player)
        self.gs.update_private_status(self.player)
    
    def apply_round_effect(self):
        if self.iceAgeCd:
            self.iceAgeCd -= 1

    def update_current_status(self):

        limit = self.gs.players[self.player].stars//2 if self.gs.players[self.player].stars >= 2 else 0

        self.gs.server.emit("update_skill_status", {
            'name': "Realm of Permafrost",
            'description': "In any battle you engage in, all stats of both you and your enemies are set to default. For 2★, you can activate Ice Age that lasts 2 rounds",
            'hasLimit': True,
            'cooldown': self.iceAgeCd,
            'limits': limit,
            'operational': self.active,
            'btn_msg': "Begin Ice Age"
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        return info

class Iron_Wall(Skill):

    def __init__(self, player, gs):
        super().__init__("Iron_Wall", player, gs)
        self.reactMod = True
        self.ironwall = False
        self.limit = len(self.gs.players) // 2
        self.cooldown = 0
        self.hasRoundEffect = True

    def reactStatsMod(self, ownStats, enemyStats, attacking):
        if not attacking and self.active:

            ownStats[3] += 30
            ownStats[4] = 2

            disparity = (enemyStats[0] - ownStats[0]) + (enemyStats[1] - ownStats[1])

            if disparity > 4:
                ownStats[3] += 30
                ownStats[4] += 1
            elif disparity == 4:
                ownStats[3] += 20
                ownStats[4] += 1
            elif disparity == 3:
                ownStats[3] += 15
                ownStats[4] += 1    
            elif disparity == 2:
                ownStats[3] += 10
            elif disparity == 1:
                ownStats[3] += 5

            if self.ironwall:
                if ownStats[3] <= 60:
                    ownStats[3] = 95
                    ownStats[4] = 3
                else:
                    ownStats[3] = 99
                    ownStats[4] = 3
    
    def turn_off_iron_wall(self):
        self.ironwall = False
    
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Iron Wall",
            'description': "At least 30% nullification rate and x2 damage output in defense. The stronger the opponent, the higher the defense. When activated Iron Wall, Nullification Rate reaches 90% with Damage Multiplier reaching 3.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.limit,
            'btn_msg': "ACTIVATE IRON DOME",
            'cooldown': self.cooldown,
            'activated': self.ironwall,
            'inUseMsg': "IRON DOME IN ACTION"
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        info += 'Iron wall activating!' if self.ironwall else ''
        return info

    def apply_round_effect(self):
        if self.cooldown:
            self.cooldown -= 1
    
    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if self.cooldown:
            self.gs.server.emit('display_new_notification', {'msg': "In cooldown!"}, room=self.player)
            return
        if not self.limit:
            self.gs.server.emit('display_new_notification', {'msg': "No more usages!"}, room=self.player)
            return
        
        self.limit -= 1
        self.cooldown += 2
        self.ironwall = True
        
class Dictator(Skill):

    def __init__(self, player, gs):
        super().__init__("Dictator", player, gs)
        self.Annihilator_as_user = player == gs.Annihilator
        self.hasTurnEffect = True
        self.limit = len(self.gs.players) // 3

    def apply_turn_effect(self,):
        if self.active:
            self.gs.players[self.player].stars += 2
            if self.Annihilator_as_user:
                self.gs.players[self.player].stars += 1

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': self.name,
            'description': "Gain a minimum of 2★ per turn regardless of successful conquests. When ",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.limit,
            'btn_msg': "I Alone Am Worthy",
        }, room=self.player)
    
    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if not self.limit:
            self.gs.server.emit('display_new_notification', {'msg': "No more usages!"}, room=self.player)
            return
        
        self.limit -= 1
        
        added_stars = 0
        max_add = 6

        donors = sorted(
            [p for p in self.gs.players if p != self.player],
            key=lambda pid: self.gs.players[pid].stars,
            reverse=True
        )

        while added_stars < max_add and any(self.gs.players[p].stars > 0 for p in donors):
            for pid in donors:
                other_player = self.gs.players[pid]
                if other_player.stars > 0 and added_stars < max_add:
                    other_player.stars -= 1
                    self.gs.players[self.player].stars += 1
                    added_stars += 1
                    self.gs.update_private_status(self.player)
                    self.gs.update_private_status(pid)
                

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        return info

class Mass_Mobilization(Skill):

    def __init__(self, player, gs):
        super().__init__("Mass_Mobilization", player, gs)
        self.hasUsageLimit = True
        self.hasCooldown = True
        self.hasRoundEffect = True

        self.maxcooldown = 3
        self.will_cost = 8
        self.will = 0

        self.residual = 0

        self.limit = 0
        nump = len(gs.players)
        if nump < 6:
            self.limit = 2
        elif nump <= 9:
            self.limit = 3
        elif nump <= 12:
            self.limit = 4
        else:
            self.limit = 5

        self.cooldown = 0

    def apply_round_effect(self,):
        if self.active:
            if self.cooldown:
                self.cooldown -= 1
            self.will += 1
            if self.will == self.will_cost:
                self.limit += 1
                self.will = 0
            if self.residual:
                self.gs.players[self.player].reserves += self.residual
                self.residual = 0
                self.gs.update_private_status(self.player)

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

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f'Number of rounds of cooldown: {self.cooldown} | ' if self.cooldown else 'Ready to activate | '
        info += f'Number of usages left: {self.limit}'
        return info

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

        # round
        round_multiplier = 1
        if self.gs.GES.round == 0:
            round_multiplier = 0.6
        
        # increase reserves
        if diff < -10:
            self.gs.players[self.player].reserves += math.ceil(0.17*total_troops*round_multiplier)
            self.residual = math.ceil(0.25*total_troops*(1-round_multiplier))
        elif diff < -5:
            self.gs.players[self.player].reserves += math.ceil(0.14*total_troops*round_multiplier)
            self.residual = math.ceil(0.22*total_troops*(1-round_multiplier))
        elif diff < 0:
            self.gs.players[self.player].reserves += math.ceil(0.12*total_troops*round_multiplier)
            self.residual = math.ceil(0.18*total_troops*(1-round_multiplier))
        elif diff < 5:
            self.gs.players[self.player].reserves += math.ceil(0.12*total_troops*round_multiplier)
            self.residual = math.ceil(0.15*total_troops*(1-round_multiplier))
        elif diff < 10:
            self.gs.players[self.player].reserves += math.ceil(0.12*total_troops*round_multiplier)
            self.residual = math.ceil(0.12*total_troops*(1-round_multiplier))
        else:
            self.gs.players[self.player].reserves += math.ceil(0.1*total_troops*round_multiplier)
            self.residual = math.ceil(0.1*total_troops*(1-round_multiplier))

        # update private view
        self.gs.update_private_status(self.player)

        # update limits and cooldown
        self.limit -= 1
        self.cooldown = self.maxcooldown

class Industrial_Revolution(Skill):

    def __init__(self, player, gs):
        super().__init__("Industrial_Revolution", player, gs)
        self.intMod = True
        
        self.finish_building = True
        self.freeCityTracker = {}
        self.freeCityBuilt = []
        self.hasTurnEffect = True

        for cont in self.gs.map.conts:
            self.freeCityTracker[cont] = 0

    def internalStatsMod(self, battle_stats):
        if self.active:
            battle_stats[0] += 1
    
    def apply_turn_effect(self,):
        self.turn_stats_mod = False

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f'{2 * len(self.freeCityTracker) - sum(self.freeCityTracker.values())} free cities ready to be built\n'
        return info

    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Industrial Revolution",
            'description': "Can build up to 2 cities for free per continent, +1 Industrial Level in battles",
            'operational': self.active,
            'forbidden_targets': self.freeCityBuilt,
            'ft_msg': "Free cities built in:",
            'hasLimit': True,
            'limits': 2 * len(self.freeCityTracker) - sum(self.freeCityTracker.values()),
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
        total_allowed_cities = 2 * len(self.freeCityTracker) - sum(self.freeCityTracker.values())
        if len(choices) > total_allowed_cities:
            self.gs.server.emit("display_new_notification", {"msg": f"Selected more than allowed amount of cities!"}, room=self.player)
            return

        tmp_count = {}

        # already built on continent
        for choice in choices:
            if self.gs.map.territories[choice].isCity:
                self.gs.server.emit("display_new_notification", {"msg": f"Selected a territory that already has a city!"}, room=self.player)
                return
            if self.gs.map.territories[choice].isDeadZone:
                self.gs.server.emit("display_new_notification", {"msg": f"Cannot build on radioactive zone!"}, room=self.player)
                return
            for cont in self.gs.map.conts:
                if choice in self.gs.map.conts[cont]['trtys']:
                    if cont not in tmp_count:
                        tmp_count[cont] = 1
                    else:
                        tmp_count[cont] += 1
                    
                    if tmp_count[cont] > 2:
                        self.gs.server.emit("display_new_notification", {"msg": f"Cannot build more than 2 free cities on {cont}!"}, room=self.player)
                        return
                    if self.freeCityTracker[cont] + tmp_count[cont] > 2:
                        self.gs.server.emit("display_new_notification", {"msg": f"Cannot build more than 2 free cities on {cont}!"}, room=self.player)
                        return

        # apply changes
        for choice in choices:
            self.gs.map.territories[choice].isCity = True
            self.gs.server.emit('update_trty_display', {choice: {'hasDev': 'city'}}, room=self.gs.lobby)
            self.freeCityBuilt.append(self.gs.map.territories[choice].name)
            for cont in self.gs.map.conts:
                # Update free city tracker
                if choice in self.gs.map.conts[cont]['trtys']:
                    self.freeCityTracker[cont] += 1
        
        self.gs.server.emit('cityBuildingSFX', room=self.gs.lobby)
        self.gs.update_TIP(self.player)
        self.gs.update_private_status(self.player)
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
        if l < 6:
            self.top_nump = 1
        elif l < 10:
            self.top_nump = 2  
        elif l < 16:
            self.top_nump = 3

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        names = ''
        for p in self.targets:
            names += self.gs.players[p].name + " "
        if not names:
            names = 'nobody'
        info += 'Currently targeting ' + names
        return info

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
        else:
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
        return amt
        
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Robinhood",
            'description': f"Take away resources from the top {self.top_nump} strongest players to give to yourself",
            'operational': self.active
        }, room=self.player)

class Ares_Blessing(Skill):

    def __init__(self, player, gs):
        super().__init__("Ares' Blessing", player, gs)
        self.hasUsageLimit = True
        self.hasCooldown = True
        self.hasRoundEffect = True
        self.hasTurnEffect = True

        nump = len(gs.players)
        self.limit = math.ceil(nump/2) if math.ceil(nump/2) >= 2 else 2

        self.intMod = True
        self.cooldown = 0

        self.changed_stats = True
        self.activated = False

        self.current_max = 0
        self.rage_not_activated = True

    # checking only when being attacked
    def checking_rage_meter(self,):
        curr_total = self.gs.players[self.player].total_troops
        if curr_total > self.current_max:
            self.current_max = curr_total
            self.rage_not_activated = True
        if curr_total < (self.current_max*0.6) and self.rage_not_activated:
            self.cooldown = 0
            self.limit += 1
            self.rage_not_activated = False
    
    def internalStatsMod(self, battle_stats):

        if self.activated:
            battle_stats[0] += 2
            battle_stats[1] += 2
            battle_stats[4] += 1

    def apply_turn_effect(self, ):
        self.activated = False
        self.changed_stats = True

    def apply_round_effect(self,):
        if self.cooldown:
            self.cooldown -= 1

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Ares' Blessing",
            'description': "Truth is only found within the range of the cannons! +2 industrial power +2 infrastructure power x2 damage when activated.",
            'operational': self.active,
            'hasLimit': self.hasUsageLimit,
            'limits': self.limit,
            'cooldown': self.cooldown,
            'activated': self.activated,
            'btn_msg': "START RAMPAGE",
            'inUseMsg': "RAMPAGE ONGOING"
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f'{self.limit} usages left | '
        info += f'Number of rounds of cooldown left: {self.cooldown}' if self.cooldown else 'Ready to activate'
        return info

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
        
        self.activated = True
        self.changed_stats = False

        # update limits and cooldown
        self.limit -= 1
        self.cooldown = 3

class Zealous_Expansion(Skill):

    def __init__(self, player, gs):
        super().__init__("Zealous_Expansion", player, gs)
        self.give_troop_bonus = True
        self.intMod = True

    def internalStatsMod(self, battle_stats):
        if self.active:
            addi = (battle_stats[0] - 2) - 3
            battle_stats[1] += addi

    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Zealous Expansion",
            'description': "Cost of increasing infrastructure level decrease from 3★ to 2★. Each additional infrastructure level gives 5 bonus troop as reserve at your turn.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.gs.players[self.player].stars//2,
            'btn_msg': "Level up infrastructure by 1"
        }, room=self.player) 

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        return info

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": "War art disabled!"}, room=self.player)
            return
        
        self.gs.players[self.player].stars -= 2
        self.gs.players[self.player].infrastructure_upgrade += 1
        self.gs.update_private_status(self.player)
        self.gs.update_HIP(self.player)
        self.gs.get_SUP()
        self.gs.update_global_status()

class Elitocracy(Skill):
    def __init__(self, player, gs):
        super().__init__("Elitocracy", player, gs)
        self.intMod = True
        self.hasRoundEffect = True
        self.Annihilator_as_user = player == gs.Annihilator
        self.cost_per_autoupgrade = 2 if self.Annihilator_as_user else 3
    
    def apply_round_effect(self):
        curr = self.gs.GES.round
        if curr > 0 and curr % self.cost_per_autoupgrade == 0:
            self.gs.players[self.player].min_roll += 1
            self.gs.update_private_status(self.player)

    def internalStatsMod(self, battle_stats):
        if self.active:
            battle_stats[4] = battle_stats[2]//2 + 1

    def update_current_status(self):

        limit = self.gs.players[self.player].stars//3 if self.gs.players[self.player].min_roll < (self.gs.get_player_industrial_level(self.gs.players[self.player])+6) else 0

        self.gs.server.emit("update_skill_status", {
            'name': "Elitocracy",
            'description': "Able to raise the minimum dice roll. Cost 3★ to raise the minimum dice roll by 1. For every 2 level increased, your damage multiplier increase by 1",
            'operational': self.active,
            'hasLimit': True,
            'limits': limit,
            'btn_msg': "Increase minimum dice roll"
        }, room=self.player) 

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if self.gs.players[self.player].stars < 3:
            self.gs.server.emit('display_new_notification', {'msg': "Not enough stars to upgrade!"}, room=self.player)
            return
        self.gs.players[self.player].stars -= 3
        self.gs.players[self.player].min_roll += 1
        self.gs.update_private_status(self.player)

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        return info

class Necromancer(Skill):
    def __init__(self, player, gs):
        super().__init__("Necromancer", player, gs)
        self.curr_turn_gain = 0
        self.hasTurnEffect = True
        self.star_per_troops = 6 if player == gs.Annihilator else 9
    
    def apply_turn_effect(self,):
        self.gs.players[self.player].reserves += self.curr_turn_gain
        self.gs.players[self.player].stars += self.curr_turn_gain//self.star_per_troops
        self.gs.update_private_status(self.player)
        self.curr_turn_gain = 0

    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Necromancer",
            'description': "When opponents attack you and fail, their losses become your reserves. Losses from the enemies during your conquests become your reserves, you will receive them at the end of your turn. For every 7 troops you've received, you receive 1 star.",
            'operational': self.active,
        }, room=self.player) 
    
    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        return info
    
    def apply_round_effect(self,):
        if self.cooldown:
            self.cooldown -= 1

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if self.cooldown:
            self.gs.server.emit('display_new_notification', {'msg': "Still in cooldown!"}, room=self.player)
            return
        
        self.activated = True
        self.cooldown = 2

class Divine_Punishment(Skill):
        
    def __init__(self, player, gs):
        super().__init__("Divine_Punishment", player, gs)
        self.hasUsageLimit = True
        self.energy_cost = 1 if player == gs.Annihilator else 2
        self.limit = len(gs.players) + 1 if player == gs.Annihilator else len(gs.players)
        self.finished_bombardment = True

        # if self.limit > len(gs.map.territories)//len(gs.players):
        #     self.limit = len(gs.map.territories)//len(gs.players) - 2
        #     self.energy_cost = 2

        self.hasRoundEffect = True
        self.energy = 0

    def apply_round_effect(self,):
        if self.active:
            self.energy += 1
            if self.energy == self.energy_cost:
                self.limit += 1
                self.energy = 0
                if self.limit > 20:
                    self.limit = 20

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Divine Punishment",
            'description': "Operating an orbital strike station, you can launch bombardment and turn any enemy territory on the map into dead zone.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.limit,
            'btn_msg': "LAUNCH ATTACK",
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f'{self.limit} usages left\n'
        return info
    
    def activate_effect(self):
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": "War art disabled!"}, room=self.player)
            return
        self.gs.GES.handle_async_event({'name': 'D_P'}, self.player)

    def validate_and_apply_changes(self, data):
        
        choices = data['choice']

        # Interruption
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": f"Striking operation obstructed by enemy forces!"}, room=self.player)
            return

        # too many targets
        if len(choices) > self.limit:
            self.gs.server.emit("display_new_notification", {"msg": f"Number of targets exceeding your usage limit!"}, room=self.player)
            return

        # not striking yourself
        for target in choices:
            if target in self.gs.players[self.player].territories:
                    self.gs.server.emit("display_new_notification", {"msg": f"Cannot strike your own territories!"}, room=self.player)
                    return

        # apply changes
        for choice in choices:

            chosen_trty = self.gs.map.territories[choice]

            for nt in chosen_trty.neighbors:
                if nt not in self.gs.players[self.player].territories:
                    self.gs.map.territories[nt].isDeadZone = 2
                    self.gs.map.territories[nt].isFort = False
                    shockwave = min(5, self.gs.map.territories[nt].troops)
                    self.gs.map.territories[nt].troops -= shockwave
                    for player in self.gs.players:
                        if nt in self.gs.players[player].territories:
                            self.gs.players[player].total_troops -= shockwave

                            self.gs.update_LAO(player)
                            self.gs.update_TIP(player)
                            self.gs.update_private_status(player)

                            # Ares' Blessing Rage meter checking
                            if self.gs.players[player].skill:
                                if self.gs.players[player].skill.name == "Ares' Blessing" and self.gs.players[player].skill.active:
                                    self.gs.players[player].skill.checking_rage_meter()

                            # visual effect
                            self.gs.server.emit('battle_casualties', {
                                f'{nt}': {'tid': nt, 'number': shockwave},
                            }, room=self.gs.lobby)
                            break
                    self.gs.server.emit('update_trty_display', {nt: {'troops': self.gs.map.territories[nt].troops, 'hasEffect': 'nuke'}}, room=self.gs.lobby)

            wasMega = chosen_trty.isMegacity
            if chosen_trty.isMegacity:
                chosen_trty.isMegacity = False
            else:
                chosen_trty.isCity = False

            chosen_trty.isTransportcenter = False
            
            chosen_trty.isDeadZone = 2

            # Remove Fortification
            chosen_trty.isFort = False

            chosen_trty.isBureau = False

            casualties = math.ceil(0.75*chosen_trty.troops)
            chosen_trty.troops -= casualties

            # update total troop
            for player in self.gs.players:
                if choice in self.gs.players[player].territories:
                    self.gs.players[player].total_troops -= casualties

                    self.gs.update_LAO(player)
                    self.gs.update_TIP(player)
                    self.gs.update_HIP(player)
                    self.gs.update_private_status(player)

                    # Ares' Blessing Rage meter checking
                    if self.gs.players[player].skill:
                        if self.gs.players[player].skill.name == "Ares' Blessing" and self.gs.players[player].skill.active:
                            self.gs.players[player].skill.checking_rage_meter()

                    # visual effect
                    self.gs.server.emit('battle_casualties', {
                        f'{choice}': {'tid': choice, 'number': casualties},
                    }, room=self.gs.lobby)
                    break
            
            if wasMega:
                self.gs.server.emit('update_trty_display', {choice: {'hasDev': 'city', 'troops': chosen_trty.troops, 'hasEffect': 'nuke'}}, room=self.gs.lobby)
            else:
                self.gs.server.emit('update_trty_display', {choice: {'hasDev': '', 'troops': chosen_trty.troops, 'hasEffect': 'nuke'}}, room=self.gs.lobby)
        
        self.gs.update_player_stats()

        self.gs.get_SUP()
        self.gs.update_global_status()

        self.gs.signal_MTrackers('indus')
        self.gs.signal_MTrackers('popu')

        # soundFX
        self.gs.server.emit('nuclear_explosion', room=self.gs.lobby)

        # terminate strike
        self.finished_bombardment = True
        self.limit -= len(choices)

class Air_Superiority(Skill):

    def __init__(self, player, gs):
        super().__init__("Air_Superiority", player, gs)

        self.hasUsageLimit = True

        self.limit = 5

        self.hasTurnEffect = True
        self.energy = 0
        self.Annihilator_as_user = player == gs.Annihilator

    def apply_turn_effect(self,):
        self.limit = 5

    def calculate_bonuses(self, x):
        # Constants for the polynomial function
        a = 0.1
        b = 0.6
        c = 0.5

        # Calculate the bonus using the quadratic function and round up
        bonus = math.ceil(a * x ** 2 + b * x + c)
        if self.Annihilator_as_user:
            bonus = math.ceil(1.3*bonus)
        return bonus

    def long_arm_jurisdiction(self,):
        if self.active:
            distincts = []
            for t in self.gs.players[self.player].territories:
                for cont in self.gs.map.conts:
                    if t in self.gs.map.conts[cont]['trtys']:
                        if cont not in distincts:
                            distincts.append(cont)

            bonus = len(distincts)
            self.gs.players[self.player].reserves += self.calculate_bonuses(bonus)
            if self.Annihilator_as_user:
                self.gs.players[self.player].stars += bonus//3
            else:
                self.gs.players[self.player].stars += bonus//4
            self.gs.update_private_status(self.player)
    
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Air Superiority",
            'description': "Able to jump over territory to attack, 5 jumps per round, cannot skipping over more than 3 territories per jump. Long-Arm Jurisdiction give you extra reserves and special authorities based on how many distinct continents your troops are stationed on.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.limit,
            'btn_msg': "LAUNCH PARATROOPER ATTACK",
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational\n' if self.active else 'Inactive\n'
        return info

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": "War art disabled!"}, room=self.player)
            return
        if self.gs.pids[self.gs.GES.current_player] != self.player or self.gs.GES.current_event.name != 'conquer':
            self.gs.server.emit("display_new_notification", {"msg": "Not the right timing to attack!"}, room=self.player)
            return
        self.gs.GES.handle_async_event({'name': 'A_S'}, self.player)

    def validate_and_apply_changes(self, data):
        
        t1, t2 = data['choice']

        # Interruption
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": f"Striking operation obstructed by enemy forces!"}, room=self.player)
            return

        if not self.limit:
            self.gs.server.emit("display_new_notification", {"msg": f"No more paratrooper attacks for this round!"}, room=self.player)
            return
        
        if t2 not in self.gs.map.get_reachable_airspace(t1, 3):
            self.gs.server.emit("display_new_notification", {"msg": f"Invalid attack option!"}, room=self.player)
            return
        
        # if this is a air strike or not
        if t2 not in self.gs.map.territories[t1].neighbors:
            self.limit -= 1

        self.gs.handle_battle(data)

class Collusion(Skill):
    def __init__(self, player, gs):
        super().__init__("Collusion", player, gs)
        self.finished_choosing = True
        self.secret_control_list = []
        self.free_usages = 2
        if len(self.gs.players) > 4:
            self.free_usages += 1
        if len(self.gs.players) > 6:
            self.free_usages += 1
        self.hasRoundEffect = True

    def apply_round_effect(self):
        self.free_usages += 1

    def update_current_status(self):

        controlled_trtys = [self.gs.map.territories[tid].name for tid in self.secret_control_list]
        self.gs.server.emit("update_skill_status", {
            'name': "Collusion",
            'description': f"Corrupt authority of an enemy territory and secretly control the territory. Currently have {self.free_usages} usages.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.free_usages,
            'forbidden_targets': controlled_trtys,
            'ft_msg': "Secretly controlling:",
            'btn_msg': "Corrupt a territory"
        }, room=self.player) 

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += 'Secretly controlling '
        for tid in self.secret_control_list:
            info += ' ' + self.gs.map.territories[tid].name
        return info

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        if not self.free_usages:
            self.gs.server.emit('display_new_notification', {'msg': "Not enough usages to corrupt any territory!"}, room=self.player)
            return
        self.gs.GES.handle_async_event({'name': 'C_T'}, self.player)

    def validate_and_apply_changes(self, data):
        
        choice = data['choice']

        # Interruption
        if not self.active:
            self.gs.server.emit("display_new_notification", {"msg": f"Skill usage obstructed by enemy forces!"}, room=self.player)
            return

        if not self.free_usages:
            self.gs.server.emit("display_new_notification", {"msg": f"No usages available!"}, room=self.player)
            return
        
        for p in self.gs.players:
            if self.gs.players[p].skill:
                if self.gs.players[p].skill.name == "Collusion":
                    if choice in self.gs.players[p].skill.secret_control_list:
                        self.gs.server.emit("display_new_notification", {"msg": f"Invalid collusion target!"}, room=self.player)
                        self.gs.players[self.player].skill.finished_choosing = True
                        return
        
        if choice in self.gs.players[self.player].territories:
            self.gs.server.emit("display_new_notification", {"msg": f"Invalid collusion target!"}, room=self.player)
            self.gs.players[self.player].skill.finished_choosing = True
            return
        
        if self.gs.map.territories[choice].isMegacity or self.gs.map.territories[choice].isTransportcenter:
            self.gs.server.emit("display_new_notification", {"msg": f"Invalid collusion target!"}, room=self.player)
            self.gs.players[self.player].skill.finished_choosing = True
            return

        self.finished_choosing = True
        self.secret_control_list.append(choice)
        self.free_usages -= 1
        self.gs.server.emit('display_new_notification', {'msg': f'Gained secret control over {self.gs.map.territories[choice].name}'}, room=self.player)
        self.gs.update_private_status(self.player)
        self.gs.update_TIP(self.player)
        self.gs.signal_MTrackers('indus')
        self.gs.get_SUP()
        self.gs.update_global_status()

class Laplace_Demon(Skill):
    def __init__(self, player, gs):
        super().__init__("Laplace's Demon", player, gs)
        self.gs.server.emit('laplace_mode', room=self.player)
        self.known = []
        self.finished_choosing = False
        names = []
        for miss in self.gs.Mset:
            if miss.name not in names:
                names.append(miss.name)
        if len(names) < 16:
            count = 0
            MList = ['Loyalist', 'Bounty_Hunter', 'Decapitator', 'Warmonger', 'Pacifist', 'Starchaser', 'Duelist', 'Punisher',
                     'Industrialist', 'Expansionist', 'Dominator', 'Populist', 'Fanatic', 'Unifier', 'Polarizer', 'Guardian',
                     'Gambler', 'Assassin', 'Survivalist', 'Protectionist']
            while len(names) < 16 and count != 2:
                random_miss = random.choice(MList)
                if random_miss not in names:
                    names.append(random_miss)
                    count += 1
        random.shuffle(names)
        self.names = names

    def update_current_status(self):
        # modify this
        limit = self.gs.players[self.player].stars//4 if self.gs.players[self.player].stars >= 4 else 0
        information = "You own the top information gathering group, click on player to know their hidden stats. Missions that are most likely in game: "
        for name in self.names:
            information += name + ' '
        information += "\n"
        for p in self.known:
            for pl in self.gs.players:
                if self.gs.players[pl].name == p:
                    for miss in self.gs.Mset:
                        if miss.player == pl:
                            information += f"{p} has {miss.name} as their secret agenda.\n"
                            break
                    break
        html_info = information.replace('\n', '<br>')
        self.gs.server.emit("update_skill_status", {
            'name': "Laplace's Demon",
            'description': html_info,
            'operational': self.active,
            'limits': limit,
            'hasLimit': True,
            'btn_msg': "Gather Advanced Intel"
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += "Know as much as you do :)"
        return info
    
    def get_potential_targets(self):
        plist = []
        for p in self.gs.players:
            if p != self.player:
                currp = self.gs.players[p]
                if currp.name not in self.known:
                    plist.append(currp.name)
        return plist
    
    def get_intel(self, target):
        self.finished_choosing = True
        self.known.append(target)
        self.gs.players[self.player].stars -= 4
        self.gs.update_private_status(self.player)
    
    def activate_effect(self):
        if self.active and self.gs.players[self.player].stars >= 4:
            if len(self.known) < (len(self.gs.players)-1):
                self.gs.GES.handle_async_event({'name':"G_I"}, self.player)
            else:
                self.gs.server.emit("display_new_notification", {'msg': "No more intel can be gathered"}, room=self.player)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "War art is currently sealed!"}, room=self.player)

class Arsenal_of_the_Underworld(Skill):
    
    def __init__(self, player, gs):
        super().__init__("Arsenal of the Underworld", player, gs)
        # tid : number of mines
        self.minefields = {}
        self.max_minefields = 3
        # tid
        self.underground_silo = None
        self.silo_usage = 0
        self.silo_used = 0
        self.range = 0
        self.damage = 0
        self.hasRoundEffect = True
        self.finished_setting = True
        self.finished_launching = True
        self.out_of_turn_activation = True
        self.shockwaveDamage = 1
        self.missile_waitlist = []

    # at the start of each round, compute the number of usages and range
    def apply_round_effect(self):
        dev_lvls = self.gs.get_player_industrial_level(self.gs.players[self.player]) + self.gs.get_player_infra_level(self.gs.players[self.player])
        self.silo_usage = 2 + dev_lvls
        self.silo_used = 0
        self.damage = 3 + dev_lvls
        self.range = 5 + dev_lvls//2
        self.max_minefields = 3 + dev_lvls
        self.shockwaveDamage = 1 + dev_lvls//2
    
    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Arsenal of the Underworld",
            'description': "Controls underground arsenal that can deal heavy damage to enemy forces.",
            'operational': self.active,
            'hasLimit': True,
            'limits': 'Depends on action',
            'btn_msg': "Manage Arsenal"
        }, room=self.player)

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        if self.minefields:
            info += 'Minefields located in '
        for tid in self.minefields:
            info += ' ' + self.gs.map.territories[tid].name
        if self.underground_silo:
            info += ' | Underground Silo located in ' + self.gs.map.territories[self.underground_silo].name
        return info
    
    def activate_effect(self):
        if self.active:
            data = {}
            if self.minefields:
                data['minefields'] = []
                for tid in self.minefields:
                    data['minefields'].append([self.gs.map.territories[tid].name, self.minefields[tid]])
            if len(self.minefields) < self.max_minefields:
                data['set_minefields'] = True
            if self.underground_silo:
                data['silo_usable'] = True
                data['underground_silo_location'] = self.gs.map.territories[self.underground_silo].name
                data['silo_usage'] = self.silo_usage - self.silo_used
                data['occupied'] = self.underground_silo not in self.gs.players[self.player].territories
            else:
                data['silo_build'] = True
            data['minefield_limit'] = self.max_minefields
            self.gs.server.emit("arsenal_controls", data, room=self.player)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "Arsenal management has been blocked!"}, room=self.player)

    def handle_minefield_placements(self, choices):
        ### Safeguard In GES and app.py ###
        for choice in choices:
            self.minefields[int(choice)] = 5
        self.finished_setting = True

    def get_landmine_damage(self, t2, atk_amt):
        if t2 in self.minefields:
            if atk_amt > 20:
                damage = math.ceil(self.minefields[t2]*5*atk_amt/100)
                del self.minefields[t2]
                return damage
            else:
                if atk_amt <= self.minefields[t2]:
                    self.minefields[t2] -= atk_amt
                    if not self.minefields[t2]:
                        del self.minefields[t2]
                    return atk_amt
                else:
                    damage = self.minefields[t2]
                    del self.minefields[t2]
                    return damage
        return 0
                
    def handle_silo_placement(self, choice):
        self.underground_silo = int(choice)
        self.finished_setting = True
        # self.gs.players[self.player].stars -= 3
        # self.gs.update_private_status(self.player)
        # set up usage, range and damage
        self.apply_round_effect()

    def apply_missile_damages(self, choices):
        for choice in choices:
            choice = int(choice)
            casualties = self.damage
            curr_territory = self.gs.map.territories[choice]
            if casualties <= curr_territory.troops:
                curr_territory.troops -= casualties
            else:
                casualties = curr_territory.troops
                curr_territory.troops = 0

            for player in self.gs.players:
                if choice in self.gs.players[player].territories:
                    self.gs.players[player].total_troops -= casualties

                    self.gs.update_LAO(player)

                    # Ares' Blessing Rage meter checking
                    if self.gs.players[player].skill:
                        if self.gs.players[player].skill.name == "Ares' Blessing" and self.gs.players[player].skill.active:
                            self.gs.players[player].skill.checking_rage_meter()

                    # visual effect
                    self.gs.server.emit('battle_casualties', {
                        f'{choice}': {'tid': choice, 'number': casualties},
                    }, room=self.gs.lobby)
                    break
            self.gs.server.emit('update_trty_display', {choice: {'troops': curr_territory.troops}}, room=self.gs.lobby)
            # neighboring territory shockwave damage
            for nt in curr_territory.neighbors:
                if nt in self.gs.players[self.player].territories:
                    continue
                curr_neighbor = self.gs.map.territories[nt]
                shockwave = self.shockwaveDamage
                if shockwave <= curr_neighbor.troops:
                    curr_neighbor.troops -= shockwave
                else:
                    shockwave = curr_neighbor.troops
                    curr_neighbor.troops = 0

                for player in self.gs.players:
                    if nt in self.gs.players[player].territories:
                        self.gs.players[player].total_troops -= shockwave

                        self.gs.update_LAO(player)

                        # Ares' Blessing Rage meter checking
                        if self.gs.players[player].skill:
                            if self.gs.players[player].skill.name == "Ares' Blessing" and self.gs.players[player].skill.active:
                                self.gs.players[player].skill.checking_rage_meter()

                        # visual effect
                        self.gs.server.emit('battle_casualties', {
                            f'{nt}': {'tid': nt, 'number': shockwave},
                        }, room=self.gs.lobby)
                        break
                self.gs.server.emit('update_trty_display', {nt: {'troops': curr_neighbor.troops}}, room=self.gs.lobby)
        self.gs.update_player_stats()
        self.gs.get_SUP()
        self.gs.update_global_status()
        self.gs.signal_MTrackers('popu')
        self.gs.server.emit('play_missile_sound', room=self.gs.lobby)

    def execute_interturn(self):
        self.apply_missile_damages(self.missile_waitlist)
        self.missile_waitlist = []

    def handle_US_strike(self, choices):
        self.finished_launching = True
        if len(choices) > (self.silo_usage - self.silo_used):
            self.gs.server.emit("display_new_notification", {'msg': "Not enough usages left!"}, room=self.player)
            return
        if self.player == self.gs.pids[self.gs.GES.current_player]:
            self.apply_missile_damages(choices)
        else:
            self.missile_waitlist += choices
            self.gs.GES.interturn_events.append(self)
        self.silo_used += len(choices)

class Loan_Shark(Skill):
    def __init__(self, player, gs):
        super().__init__("Loan Shark", player, gs)
        self.max_loan = 1
        if len(self.gs.players) > 5:
            self.max_loan += 1
        elif len(self.gs.players) > 7:
            self.max_loan += 1
        # pid : [due amount, start round]
        self.loan_list = {}
        # pid : last payment round
        self.ransom_history = {}
        self.hasRoundEffect = True
        self.finished_choosing = True

    def apply_round_effect(self):
        not_safe = []
        for player in self.ransom_history:
            if self.gs.GES.round - self.ransom_history[player] == 3:
                if player not in not_safe:
                    not_safe.append(player)
        for p in not_safe:
            del self.ransom_history[p]
        
        # adding interest to unpaid ransom
        for debtor in list(self.loan_list.keys()):
            curr_diff = self.gs.GES.round - self.loan_list[debtor][1]
            if curr_diff > 1:
                self.loan_list[debtor][0] += 5
            # deadline is reached
            if curr_diff == 5:
                self.handle_payment(debtor, "sepauth")
                self.handle_payment(debtor, "troops")

    def get_potential_targets(self):
        potential_targets = [player for player in self.gs.players if self.gs.players[player].alive and self.gs.players[player].connected and not self.gs.players[player].hijacked and player != self.player and player not in self.ransom_history]
        invalid_targets = []
        for player in potential_targets:
            curr_p = self.gs.players[player]
            if curr_p.alive:
                if curr_p.skill:
                    if curr_p.skill.name == "Loan Shark":
                        for t in potential_targets:
                            if t in curr_p.skill.loan_list:
                                if t not in invalid_targets:
                                    invalid_targets.append(t)
        potential_targets = [self.gs.players[player].name for player in potential_targets if player not in invalid_targets]
        return potential_targets

    def activate_effect(self):
        if self.active:
            if len(self.loan_list) < self.max_loan:
                self.gs.GES.handle_async_event({'name':"M_R"}, self.player)
            else:
                self.gs.server.emit("display_new_notification", {'msg': "Ransom list is full!"}, room=self.player)
        else:
            self.gs.server.emit("display_new_notification", {'msg': "War art is currently sealed!"}, room=self.player)

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        if self.loan_list:
            for debtor in self.loan_list:
                info += self.gs.players[debtor].name + " is currently in debt. "
        else:
            info += "No ransomware victim yet."
        return info
    
    def set_ransom(self, target):
        self.finished_choosing = True
        pid = ""
        for player in self.gs.players:
            if self.gs.players[player].name == target:
                pid = player
                break
        self.loan_list[pid] = [10, self.gs.GES.round]
        if self.gs.GES.round == 0:
            self.loan_list[pid] = [5, self.gs.GES.round]

        curr = self.gs.players[pid]
        curr.hijacked = True
        if curr.skill:
            curr.skill.active = False
        self.gs.server.emit('show_debt_button', room=pid)

    def handle_payment(self, player, method):
        if player not in self.loan_list:
            return
        debt_amt = self.loan_list[player][0]
        debtor = self.gs.players[player]
        loaner = self.gs.players[self.player]
        if method == 'sepauth':
            r_amt = math.ceil(debt_amt/5)
            if r_amt <= debtor.stars:
                debtor.stars -= r_amt
                loaner.stars += r_amt
                del self.loan_list[player]
                self.ransom_history[player] = self.gs.GES.round
                debtor.hijacked = False
                if debtor.skill:
                    debtor.skill.active = True
                self.gs.server.emit('debt_off', room=player)
            else:
                self.loan_list[player][0] -= debtor.stars*5
                loaner.stars += debtor.stars
                debtor.stars = 0
            if debtor.stars < 0:
                debtor.stars = 0
            if loaner.stars < 0:
                loaner.stars = 0
            self.gs.update_private_status(self.player)
            self.gs.update_private_status(player)
        #payment with troops
        else:
            if debt_amt <= debtor.reserves:
                debtor.reserves -= debt_amt
                loaner.reserves += debt_amt
                del self.loan_list[player]
                self.ransom_history[player] = self.gs.GES.round
                debtor.hijacked = False
                if debtor.skill:
                    debtor.skill.active = True
                self.gs.update_private_status(self.player)
                self.gs.update_private_status(player)
                self.gs.server.emit('debt_off', room=player)
                return
            else:
                debt_amt -= debtor.reserves
                self.loan_list[player][0] -= debtor.reserves
                loaner.reserves += debtor.reserves
                debtor.reserves = 0
                self.gs.update_private_status(self.player)
                self.gs.update_private_status(player)

            if debt_amt <= debtor.total_troops:
                while debt_amt > 0:
                    curr_tid = random.choice(debtor.territories)
                    if self.gs.map.territories[curr_tid].troops:
                        loaner.reserves += 1
                        self.gs.map.territories[curr_tid].troops -= 1
                        debtor.total_troops -= 1
                        debt_amt -= 1
                        self.gs.update_LAO(player)
                        if debtor.skill:
                            if debtor.skill.name == "Ares' Blessing":
                                debtor.skill.checking_rage_meter()
                        self.gs.server.emit('battle_casualties', {
                        f'{curr_tid}': {'tid': curr_tid, 'number': 1},
                        }, room=self.gs.lobby)
                        self.gs.server.emit('update_trty_display', {curr_tid: {'troops': self.gs.map.territories[curr_tid].troops}}, room=self.gs.lobby)
                del self.loan_list[player]
                self.ransom_history[player] = self.gs.GES.round
                debtor.hijacked = False
                if debtor.skill:
                    debtor.skill.active = True
                self.gs.server.emit('debt_off', room=player)
                self.gs.update_private_status(self.player)
                self.gs.update_player_stats()
                self.gs.get_SUP()
                self.gs.update_global_status()
                self.gs.signal_MTrackers('popu')
            else:
                debt_off = debtor.total_troops
                while debtor.total_troops > 0:
                    curr_tid = random.choice(debtor.territories)
                    if self.gs.map.territories[curr_tid].troops:
                        loaner.reserves += 1
                        self.gs.map.territories[curr_tid].troops -= 1
                        debtor.total_troops -= 1
                        self.gs.update_LAO(player)
                        if debtor.skill:
                            if debtor.skill.name == "Ares' Blessing" and debtor.skill.active:
                                debtor.skill.checking_rage_meter()
                        self.gs.server.emit('battle_casualties', {
                        f'{curr_tid}': {'tid': curr_tid, 'number': 1},
                        }, room=self.gs.lobby)
                        self.gs.server.emit('update_trty_display', {curr_tid: {'troops': self.gs.map.territories[curr_tid].troops}}, room=self.gs.lobby)
                self.loan_list[player][0] -= debt_off
                self.gs.update_private_status(self.player)
                self.gs.update_player_stats()
                self.gs.get_SUP()
                self.gs.update_global_status()
                self.gs.signal_MTrackers('popu')

    def update_current_status(self):
        # modify this
        information = "Players on your ransom list each needs to pay you 2★ to regain control of their war art and special authority. Current list"
        if self.loan_list:
            information += ": "
            for debtor in self.loan_list:
                information += self.gs.players[debtor].name + ' '
        else:
            information += "is empty."
        self.gs.server.emit("update_skill_status", {
            'name': "Loan Shark",
            'description': information,
            'operational': self.active,
            'hasLimit': True,
            'limits': self.max_loan - len(self.loan_list),
            'btn_msg': "Make Ransom"
        }, room=self.player)

class Reaping_of_Anubis(Skill):
    def __init__(self, player, gs):
        super().__init__("Reaping of Anubis", player, gs)
        self.guaranteed_dmg = 0
        self.cost = 3 if player != gs.Annihilator else 2
        self.increment = 3 if player != gs.Annihilator else 2

    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += 'Destroying ' + str(self.guaranteed_dmg) + " from enemy troops at the start of every battle."
        return info
    
    def update_current_status(self):
        limit = 1 if self.gs.players[self.player].stars >= self.cost else 0
        self.gs.server.emit("update_skill_status", {
            'name': "Reaping of Anubis",
            'description': f"Fate marks {self.guaranteed_dmg} foes for death before each battle begins. Sacrifice {self.cost}★ to deepen the Toll.",
            'operational': self.active,
            'hasLimit': True,
            'limits': limit,
            'btn_msg': "Empower the Reaping"
        }, room=self.player)

    def activate_effect(self):
        if self.active:
            if self.gs.players[self.player].stars >= self.cost:
                self.guaranteed_dmg += 1
                self.gs.players[self.player].stars -= self.cost
                if self.gs.players[self.player].stars < 0:
                    self.gs.players[self.player].stars = 0
                self.gs.update_private_status(self.player)
                self.cost += self.increment

class Pandora_Box(Skill):
    def __init__(self, player, gs):
        super().__init__("Pandora's Box", player, gs)
        self.intMod = True
        self.indus = 0
        self.nulrate = 0
        self.multi = 0
        self.hasRoundEffect = True
        self.curr_pull = 100
        self.receivedBlessings = []
        self.guarantee = 0
        self.gs.players[self.player].stars += 2
        self.gs.update_private_status(self.player)

    def apply_round_effect(self):
        self.curr_pull = 100

    def internalStatsMod(self, battle_stats):
        if self.active:
            battle_stats[0] += self.indus
            battle_stats[3] += self.nulrate
            battle_stats[4] += self.multi
            if battle_stats[3] >= 100:
                battle_stats[3] = 99
    
    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += "Anything can be unleashed from it."
        return info
    
    def update_current_status(self):
        limit = self.gs.players[self.player].stars//2 if self.gs.players[self.player].stars >= 2 else 0
        self.gs.server.emit("update_skill_status", {
            'name': "Pandora's Box",
            'description': f"Pandora's Box is in your hands, peek through it using 2★ and you may unleash blessings... or curses. {self.curr_pull} peeks can be made in the current round.",
            'operational': self.active,
            'hasLimit': True,
            'limits': limit,
            'forbidden_targets': self.receivedBlessings,
            'ft_msg': "Received Blessings:",
            'btn_msg': "Lift the Lid"
        }, room=self.player)

    def activate_effect(self):
        if self.active:
            if self.curr_pull:
                if self.gs.players[self.player].stars >= 2:
                    self.gs.players[self.player].stars -= 2
                    if self.gs.players[self.player].stars < 0:
                        self.gs.players[self.player].stars = 0
                    self.gs.update_private_status(self.player)
                    self.get_outcome()
                    self.curr_pull -= 1
                    return
            else:
                self.gs.server.emit("display_new_notification", {'msg': "No more available pulls for this round!"}, room=self.player)
                return
        else:
            self.gs.server.emit("display_new_notification", {'msg': "War Art is disabled!"}, room=self.player)
    
    def get_outcome(self):
        # more star, more reserves, stats increase, intel
        num = random.randint(1, 100)
        if num < 56 and self.guarantee >= 4:
            num = random.randint(56, 100)
            self.guarantee = 0
        if num < 10: # 10%
            self.gs.server.emit("display_special_notification", {"msg": "Received nothing.....", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
        elif num < 30: # 20%
            self.gs.players[self.player].stars += 1
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "Received 1★...", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
        elif num < 55: # 25%
            self.gs.players[self.player].stars += 3
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "Received 3★!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
        elif num < 58: # 3%
            self.gs.players[self.player].stars += 7
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "RECEIVED 7★!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
        elif num < 61: # 3%
            self.gs.players[self.player].reserves += 30
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "RECEIVED 30 RESERVES!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
        elif num < 64: # 3%
            self.multi += 1
            self.gs.server.emit("display_special_notification", {"msg": "DAMAGE MULTIPLIER INCREASED BY 1!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+1 Damage Multiplier')
        elif num < 70: # 6%
            self.gs.players[self.player].min_roll += 1
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "Minimum Roll increased by 1!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+1 Minimum Roll')
        elif num < 73: # 3%
            self.gs.players[self.player].min_roll += 2
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "MINIMUM ROLL INCREASED BY 2!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+2 Minimum Roll')
        elif num < 79: # 6%
            self.gs.players[self.player].infrastructure_upgrade += 1
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "Infrastructure Level increased by 1!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+1 Infrastructure Level')
        elif num < 82: # 3%
            self.gs.players[self.player].infrastructure_upgrade += 2
            self.gs.update_private_status(self.player)
            self.gs.server.emit("display_special_notification", {"msg": "INFRASTRUCTURE LEVEL INCREASED BY 2!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+2 Infrastructure Level')
        elif num < 88: # 6%
            self.nulrate += 5
            self.gs.server.emit("display_special_notification", {"msg": "Nullification Rate increased by 5%!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+5% Nullification Rate')
        elif num < 91: # 3%
            self.nulrate += 10
            self.gs.server.emit("display_special_notification", {"msg": "NULLIFICATION RATE INCREASED BY 10%!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+10% Nullification Rate')
        elif num < 97: # 6%
            self.indus += 1
            self.gs.server.emit("display_special_notification", {"msg": "Industrial Level increased by 1!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+1 Industrial Level')
        else: # 3%
            self.indus += 2
            self.gs.server.emit("display_special_notification", {"msg": "INDUSTRIAL LEVEL INCREASED BY 2!", "t_color": "#FFD524", "b_color": "#55185D"}, room=self.player)
            self.receivedBlessings.append('+2 Industrial Level')
        if num < 30:
            self.guarantee += 1
        else:
            self.guarantee = 0

class Loopwalker(Skill):
    def __init__(self, player, gs):
        super().__init__("Loopwalker", player, gs)
        self.aval_loops = (len(self.gs.players)-1)*200
        self.loop_per_battle = 1
        self.out_of_turn_activation = True
    
    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f"Currently run {self.loop_per_battle} time loops per battle."
        return info
    
    def update_current_status(self):
        limit = self.aval_loops if self.aval_loops > 0 else 0
        self.gs.server.emit("update_skill_status", {
            'name': "Loopwalker",
            'description': f"Run all battles through multiple timelines and keep the best result. {limit} time loops available. Maximum 100 loops can be set per battle",
            'operational': self.active,
            'intset': self.loop_per_battle,
            'btn_msg': "Tune Parallel Runs"
        }, room=self.player)

    def activate_effect(self, number=None):
        if self.active:
            if number:
                if self.aval_loops > 0 and number <= self.aval_loops:
                    self.loop_per_battle = number
                else:
                    self.loop_per_battle = 1

    def get_best_outcome(self, outcomes, defending):
        if defending:
            # Defender optimization
            wins = [o for o in outcomes if o[0] == 0]  # attacker has 0 troops
            if wins:
                # Pick the defender win with the most remaining defender troops
                optimal = max(wins, key=lambda x: x[1])
            else:
                # No defender wins; pick loss that caused most damage to attacker
                losses = [o for o in outcomes if o[1] == 0]
                optimal = min(losses, key=lambda x: x[0]) if losses else None
        else:
            # Attacker optimization
            wins = [o for o in outcomes if o[1] == 0]  # defender has 0 troops
            if wins:
                # Pick the attacker win with the most remaining attacker troops
                optimal = max(wins, key=lambda x: x[0])
            else:
                # No attacker wins; pick loss that caused most damage to defender
                losses = [o for o in outcomes if o[0] == 0]
                optimal = min(losses, key=lambda x: x[1]) if losses else None

        return optimal

class Revanchism(Skill):
    def __init__(self, player, gs):
        super().__init__("Revanchism", player, gs)
        self.ragePoints = 0
        self.intMod = True
    
    def get_skill_status(self):
        info = 'Operational | ' if self.active else 'Inactive | '
        info += f"Accumulated {self.ragePoints} rage points."
        return info
    
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Revanchism",
            'description': f"What was taken away must be taken back. {self.ragePoints} rage points accumulated.",
            'operational': self.active,
        }, room=self.player)

    def internalStatsMod(self, battle_stats):
        if self.active:
            battle_stats[0] += self.ragePoints//100
            battle_stats[1] += self.ragePoints//100
            battle_stats[2] += self.ragePoints//150
            battle_stats[3] += self.ragePoints//100 * 10
            if battle_stats[3] >= 100:
                battle_stats[3] = 90
            battle_stats[4] += self.ragePoints//150

    def accumulate_rage(self, troop_loss, trty_loss):
        if self.gs.players[self.player].total_troops:
            troop_loss_percentage = math.ceil(troop_loss*100/self.gs.players[self.player].total_troops)
            if troop_loss_percentage > 10:
                self.ragePoints += troop_loss_percentage
        if trty_loss.isCapital:
            self.ragePoints += 25
        if trty_loss.isCity:
            self.ragePoints += 20
        if trty_loss.isMegacity:
            self.ragePoints += 50
        if trty_loss.isFort:
            self.ragePoints += 10
        if trty_loss.isLeyline:
            self.ragePoints += 15
        if trty_loss.isTransportcenter:
            self.ragePoints += 50
        if trty_loss.isHall:
            self.ragePoints += 50
        if trty_loss.isBureau:
            self.ragePoints += 20
        tid = 0
        for trty in self.gs.map.territories:
            if trty.name == trty_loss.name:
                break
            tid += 1
        contlist = None
        contValue = None
        for cont in self.gs.map.conts:
            if tid in self.gs.map.conts[cont]['trtys']:
                contlist = self.gs.map.conts[cont]['trtys']
                contValue = self.gs.map.conts[cont]['bonus']
                break
        tmp_trty = self.gs.players[self.player].territories[:]
        tmp_trty.append(tid)
        if set(contlist).issubset(set(tmp_trty)):
            if contValue < 7:
                self.ragePoints += round(contValue * 3)
            else:
                self.ragePoints += round(contValue * 2.5)
        self.ragePoints += 1

class Usurper(Skill):
    def __init__(self, player, gs):
        super().__init__("Usurper", player, gs)

class Handler_of_Wheel_of_Fate(Skill):
    def __init__(self, player, gs):
        super().__init__("Handler_of_Wheel_of_Fate", player, gs)