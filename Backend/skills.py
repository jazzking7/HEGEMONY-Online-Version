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

        self.turn_stats_mod = False
        self.hasUsageLimit = False
        self.hasCooldown = False
        self.singleTurnActive = False
        self.hasRoundEffect = False

        self.give_troop_bonus = False

        self.hasTurnEffect = False


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
        battle_stats[2] = 1
        battle_stats[3] = 0
        battle_stats[4] = 1

    def externalStatsMod(self, battle_stats):

        battle_stats[0] = 6
        battle_stats[1] = 3
        battle_stats[2] = 1
        battle_stats[3] = 0
        battle_stats[4] = 1

    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Realm of Permafrost",
            'description': "In any battle you engage in, all stats of both you and your enemies are set to default.",
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
        self.hasTurnEffect = True

    def apply_turn_effect(self,):
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

        self.maxcooldown = 3
        self.will_cost = 8
        self.will = 0

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
            self.gs.players[self.player].reserves += math.ceil(0.3*total_troops)
        elif diff < -5:
            self.gs.players[self.player].reserves += math.ceil(0.25*total_troops)
        elif diff < 0:
            self.gs.players[self.player].reserves += math.ceil(0.22*total_troops)
        elif diff < 5:
            self.gs.players[self.player].reserves += math.ceil(0.17*total_troops)
        elif diff < 10:
            self.gs.players[self.player].reserves += math.ceil(0.15*total_troops)
        else:
            self.gs.players[self.player].reserves += math.ceil(0.12*total_troops)

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

        self.hasTurnEffect = True

        for cont in self.gs.map.conts:
            self.freeCityTracker[cont] = 0

    def internalStatsMod(self, battle_stats):
        if self.gs.pids[self.gs.GES.current_player] == self.player: # player is attacker
            if self.turn_stats_mod:   # player stats modded
                return
            else:
                battle_stats[0] += 1
                self.turn_stats_mod = True
                return
        battle_stats[0] += 1
    
    def apply_turn_effect(self,):
        self.turn_stats_mod = False

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
            if self.gs.map.territories[choice].isDeadZone:
                self.gs.server.emit("display_new_notification", {"msg": f"Cannot build on radioactive zone!"}, room=self.player)
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
        if l < 6:
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
        self.limit = math.ceil(nump/2) if math.ceil(nump/2) >= 3 else 3

        self.intMod = True
        self.cooldown = 0

        self.changed_stats = True
        self.activated = False
    
    def internalStatsMod(self, battle_stats):

        if self.activated and not self.changed_stats:
            battle_stats[0] += 2
            battle_stats[1] += 2
            battle_stats[4] += 1
            self.changed_stats = True

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
        self.intMod = True
        
        self.give_troop_bonus = True
        self.hasTurnEffect = True

    def apply_turn_effect(self,):
        self.turn_stats_mod = False

    def internalStatsMod(self, battle_stats):
        if self.gs.pids[self.gs.GES.current_player] == self.player: # player is attacker
            if self.turn_stats_mod:   # player stats modded
                return
            else:
                battle_stats[1] += 1
                self.turn_stats_mod = True
                return
        battle_stats[1] += 1

    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Zealous Expansion",
            'description': "Cost of increasing infrastructure level decrease from 4 to 2 special authorities. Each additional infrastructure level gives 1 bonus troop as reserve at your turn.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.gs.players[self.player].stars//2,
            'btn_msg': "Level up infrastructure by 1"
        }, room=self.player) 

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

class Frameshifter(Skill):
    def __init__(self, player, gs):
        super().__init__("Frameshifter", player, gs)
    
    def update_current_status(self):

        limit = self.gs.players[self.player].stars//3 if self.gs.players[self.player].min_roll < (self.gs.get_player_industrial_level(self.gs.players[self.player])+6) else 0

        self.gs.server.emit("update_skill_status", {
            'name': "Frameshifter",
            'description': "Able to raise the minimum dice roll. Cost 3 special authority to raise the minimum dice roll by 1",
            'operational': self.active,
            'hasLimit': True,
            'limits': limit,
            'btn_msg': "Increase minimum dice roll"
        }, room=self.player) 

    def activate_effect(self):
        if not self.active:
            self.gs.server.emit('display_new_notification', {'msg': "War art disabled!"}, room=self.player)
            return
        
        self.gs.players[self.player].stars -= 3
        self.gs.players[self.player].min_roll += 1
        self.gs.update_private_status(self.player)

class Necromancer(Skill):
    def __init__(self, player, gs):
        super().__init__("Necromancer", player, gs)
        
        self.hasCooldown = True
        self.hasRoundEffect = True
        self.hasTurnEffect = True

        self.activated = False
        self.cooldown = 0

    def update_current_status(self):

        self.gs.server.emit("update_skill_status", {
            'name': "Necromancer",
            'description': "When opponents attack you and fail, their losses become your reserves. Can activate Blood Harvest, where losses from the enemies during your conquest become your reserves.",
            'operational': self.active,
            'hasLimit': True,
            'limits': "infinite amount of",
            'btn_msg': "FETCH ME THEIR SOULS!",
            'cooldown': self.cooldown,
            'inUseMsg': "BLOOD HARVEST ACTIVE"
        }, room=self.player) 
    
    def apply_round_effect(self,):
        if self.cooldown:
            self.cooldown -= 1
    
    def apply_turn_effect(self,):
        self.activated = False

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
        self.energy_cost = 3
        self.limit = len(gs.players)
        self.finished_bombardment = True

        if self.limit > len(gs.map.territories)//len(gs.players):
            self.limit = len(gs.map.territories)//len(gs.players) - 2
            self.energy_cost = 2

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

            self.gs.map.territories[choice].isCity = False
            self.gs.map.territories[choice].isDeadZone = True

            casualties = self.gs.map.territories[choice].troops
            self.gs.map.territories[choice].troops = 0

            # update total troop
            for player in self.gs.players:
                if choice in self.gs.players[player].territories:
                    self.gs.players[player].total_troops -= casualties

                    # visual effect
                    self.gs.server.emit('battle_casualties', {
                        f'{choice}': {'tid': choice, 'number': casualties},
                    }, room=self.gs.lobby)
                    break

            self.gs.server.emit('update_trty_display', {choice: {'hasDev': '', 'troops': 0, 'hasEffect': 'nuke'}}, room=self.gs.lobby)
        
        self.gs.update_player_stats()
        
        self.gs.update_LAO(self.player)
        self.gs.update_TIP(self.player)

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

        self.limit = 3

        self.hasTurnEffect = True
        self.energy = 0

    def apply_turn_effect(self,):
        self.limit = 3

    def calculate_bonuses(self, x):
        # Constants for the polynomial function
        a = 0.1
        b = 0.6
        c = 0.5

        # Calculate the bonus using the quadratic function and round up
        bonus = math.ceil(a * x ** 2 + b * x + c)
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
            self.gs.update_private_status(self.player)
    
    def update_current_status(self):
        self.gs.server.emit("update_skill_status", {
            'name': "Air Superiority",
            'description': "Able to jump over territory to attack, 3 times per turn, not skipping over more than 3 territories per jump. Long-Arm Jurisdiction give you extra reserves based on how many distinct continents your troops are stationed on.",
            'operational': self.active,
            'hasLimit': True,
            'limits': self.limit,
            'btn_msg': "LAUNCH PARATROOPER ATTACK",
        }, room=self.player)

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
        
        if t2 not in self.gs.map.get_reachable_airspace(t1):
            self.gs.server.emit("display_new_notification", {"msg": f"Invalid attack option!"}, room=self.player)
            return
        
        # if this is a air strike or not
        if t2 not in self.gs.map.territories[t1].neighbors:
            self.limit -= 1

        self.gs.handle_battle(data)