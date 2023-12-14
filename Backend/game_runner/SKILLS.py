import math as m
from tkinter import *
from random import randint
from game_runner.RNG import *
from game_runner.civil_war import *
from game_runner.death_handler import handle_death
from game_runner.Blitz_Roller import *

class Skill(object):

    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.name = ""
        self.active = True
        self.used = False
        self.off_turn_usable = False
        self.give_buff = False
        self.has_limit = False
        self.limit = None
        self.has_cool_down = False
        self.cool_down = None
        self.used_round = 0
        self.defensive = False
        self.offensive = False
        self.one_round_duration = False
        self.whole_round_duration = False
        self.eater = False
        self.locked = False

    def get_buff(self):
        # [industrial, infrastructure, multiplier, nullification]
        return

    def show_effect(self, root):
        return

    def get_limit(self):
        return

    def shut_down(self):
        return

# N1
class Sturdy_Defender(Skill):
    # INIT
    def __init__(self, owner, game):
        super().__init__(owner, game)
        self.name = "Sturdy as Steel"
        self.give_buff = True
        self.defensive = True

    def get_buff(self):
        if not self.locked:
            return [0, 0, 2, 25]
        return [0, 0, 1, 0]

# N2
class Usurper(Skill):

    def get_limit(self):
        if self.game.player_number < 8:
            return 2
        else:
            if self.game.player_number < 12:
                return 3
            else:
                return 4 if self.game.player_number < 15 else 5

    def revolution(self, name, ps):
        trty = None
        for terri in self.game.world.territories:
            if terri == name:
                trty = self.game.world.territories[name]
                break
        if trty is None:
            Label(self.root, text="Territory does not exist!").grid(row=5)
            return
        owner = trty.owner
        if owner is None:
            Label(self.root, text="Cannot rebel against neutral force!").grid(row=5)
            return
        if owner in self.vassals:
            Label(self.root, text="Cannot attack your own vassal states!").grid(row=5)
            return
        if owner == self.player:
            Label(self.root, text="Cannot rebel against yourself!").grid(row=5)
            return
        if owner in self.player.allies:
            Label(self.root, text="Cannot attack allies!").grid(row=5)
            return
        if not owner.alive:
            Label(self.root, text="The player is already dead!").grid(row=5)
            return
        if self.locked:
            Label(self.root, text="Skill is locked").grid(row=5)
            return
        if self.limit <= 0:
            Label(self.root, text="Limit Reached!").grid(row=5)
            return

        self.limit -= 1
        self.game.add_puppet_state(ps, self.player.capital_icon, self.player)
        puppet = self.game.players[len(self.game.players)-1]

        self.vassals.append(puppet)
        self.player.vassals.append(puppet)

        affected_territories = self.game.world.get_strictly_connected_regions(owner, name, [], [], owner.allies)
        contested_regions = []
        for terri in affected_territories:
            curr_trty = self.game.world.territories[terri]
            rebel = get_rolls(1, 100)[0]
            if rebel > 45:
                owner.territories.remove(terri)
                if curr_trty.isCAD and owner in curr_trty.mem_stats:
                    for ally in owner.allies:
                        ally.territories.remove(terri)
                if curr_trty.troops < 4:
                    puppet.territories.append(terri)
                    curr_trty.owner = puppet
                else:
                    curr_trty.civil_war = True
                    curr_trty.owner = None
                    rebel_troops = m.ceil((random.randint(20, 50)/100)*curr_trty.troops)
                    govern_troops = curr_trty.troops - rebel_troops
                    curr_trty.internal_dist["R"] = rebel_troops
                    curr_trty.internal_dist["G"] = govern_troops
                    contested_regions.append(curr_trty)
        self.game.map_visualizer.update_all_view()
        cw = civil_war_handler(self.game, contested_regions, owner, puppet)
        pc = puppet_capital_setter(self.game, puppet, cw)
        pc_buffer = cw_buffer(pc)
        if len(puppet.territories) == 0:
            handle_death(puppet, owner)
        if owner.hasAllies:
            for ally in owner.allies:
                if len(ally.territories) == 0:
                    handle_death(owner, puppet)
        if len(owner.territories) == 0:
            handle_death(owner, puppet)
        puppet.update_industrial_level()
        puppet.update_infrastructure()
        owner.update_industrial_level()
        owner.update_infrastructure()
        if owner.hasAllies:
            for ally in owner.allies:
                ally.update_industrial_level()
                ally.update_infrastructure()
        self.game.public_billboard.update_view()
        self.game.world_status.update_view()
        self.game.map_visualizer.update_all_view()

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Enter name of the zeroth rebel region:").grid(row=0)
        e = Entry(self.root)
        e.grid(row=1)
        # NAME GUARD
        Label(self.root, text="Enter name of the puppet state:").grid(row=2)
        e1 = Entry(self.root)
        e1.grid(row=3)
        Button(self.root, text="Start Rebellion", command=lambda: self.revolution(e.get(), e1.get())).grid(row=4)

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Stirrer of Civil Unrest"
        self.has_limit = True
        self.limit = self.get_limit()
        self.root = None
        self.vassals = []

# N3
class Air_Superiority(Skill):

    def shut_down(self):
        self.limit = 3

    def long_arm_jurisdiction(self):
        dist_conts = []
        continents = self.game.world.continents
        for trty in self.player.territories:
            for c in continents:
                if trty in continents[c]:
                    if c not in dist_conts:
                        dist_conts.append(c)
                        continue
        dc = len(dist_conts)
        bonus = 0
        if 1 <= dc <= 4:
            bonus = dc
        elif 5 <= dc <= 7:
            bonus = dc + 1
        elif 8 <= dc <= 9:
            bonus = dc + 2
        elif dc == 10:
            bonus = dc + 3
        elif dc == 11:
            bonus = dc + 4
        print(f'Adding bonus from long-arm jurisdiction {bonus}')
        self.player.reserves += bonus
        self.player.game.world_status.update_view()
        self.player.game.public_billboard.update_view()
        return

    def airdrop(self, dep, des, tam):
        if self.limit == 0:
            Label(self.root, text="Airdrop Limit Reached!").grid(row=0)
            return
        elif self.locked:
            Label(self.root, text="Skill locked!").grid(row=0)
            return
        elif dep not in self.player.territories or des in self.player.territories:
            Label(self.root, text="Invalid coordinates!").grid(row=4)
            return
        elif tam > self.game.world.territories[dep].troops-1:
            Label(self.root, text="Invalid amount of troops entered!").grid(row=4)
            return
        elif des not in self.game.world.get_reachable_airspace(dep, [dep], 1, 5):
            Label(self.root, text="Destination not in the reachable airspace!").grid(row=4)
            return
        self.limit -= 1
        trty_A = self.game.world.territories[dep]
        trty_D = self.game.world.territories[des]
        attacker = trty_A.owner
        defender = trty_D.owner
        if trty_A.isCAD:
            # if current attacker is an ally
            if self.game.players[self.game.turn] in attacker.allies:
                attacker = self.game.players[self.game.turn]
                trty_A.owner = attacker
        defender = trty_D.owner
        if defender is not None:
            # Attacking CAD
            if defender.hasAllies:
                # mistake here:
                # I forgot to add if defender in trty_D.mem_stats
                # the ownership does not change no matter what.
                if trty_D.isCAD and defender in trty_D.mem_stats:
                    defender = defender.get_best_defender()
        results = Blitz_roll(attacker, defender, trty_A, trty_D, tam, trty_D.troops)
        tmp_frame = Toplevel()
        Blitz_result_handle(attacker, defender, trty_A, trty_D, tmp_frame, results)
        # live_map update
        self.game.map_visualizer.update_view(trty_D.name)
        self.game.map_visualizer.update_view(trty_A.name)
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()

    def show_effect(self, root):
        self.root = root
        for widget in root.grid_slaves():
            widget.destroy()
        Label(root, text="Enter departure:").grid(row=0, column=0)
        dep = Entry(root)
        dep.grid(row=0, column=1)
        Label(root, text="Enter Destination:").grid(row=1, column=0)
        des = Entry(root)
        des.grid(row=1, column=1)
        Label(root, text="Amount of troops:").grid(row=2, column=0)
        tam = Entry(root)
        tam.grid(row=2, column=1)
        Button(root, text="Launch Attack", command=lambda: self.airdrop(
            dep.get(), des.get(), int(tam.get())
        )).grid(row=3, column=0, columnspan=2)

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Air Superiority"
        self.has_limit = True
        self.limit = 3
        self.root = None
        self.whole_round_duration = True

# N4
class Mass_Mobilization(Skill):

    def get_limit(self):
        if 7 < self.game.player_number < 14:
            return 3
        elif self.game.player_number > 14:
            return 4
        return 2

    def show_effect(self, root):
        for widget in root.grid_slaves():
            widget.destroy()
        if self.limit == 0:
            Label(root, text="MM Limit Reached!").grid(row=0)
            return
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(root, text="Skill in cool down!").grid(row=0)
            return
        elif self.locked:
            Label(root, text="Skill deactivated!").grid(row=0)
            return
        else:
            total_force = self.player.get_total_force()
            global_average = self.game.get_total_troops() / self.game.get_active_player()
            if total_force < m.ceil(0.9 * global_average):
                self.player.reserves += m.ceil(self.game.get_total_troops() * 0.22)
            elif m.ceil(0.9 * global_average) < total_force < m.ceil(1.1 * global_average):
                self.player.reserves += m.ceil(self.game.get_total_troops() * 0.18)
            else:
                self.player.reserves += m.ceil(self.game.get_total_troops() * 0.15)
            self.limit -= 1
            self.used_round = self.game.round
            self.used = True
            self.game.world_status.update_view()
            if self.game.stage == 1:
                self.game.curr_reinforcer.update_info()
            Label(root, text="MM Activated").grid(row=0)

    def __init__(self, player, game):
        # INIT
        super().__init__(player, game)
        self.name = "Mass Mobilization"
        self.has_cool_down = True
        self.cool_down = 1
        self.has_limit = True
        self.limit = self.get_limit()

# N7 NEED IMPROVEMENT
class Divine_Punishment(Skill):

    def get_limit(self):
        if self.game.player_number < 7:
            return 5
        elif self.game.player_number < 10:
            return 6
        elif 11 <= self.game.player_number < 15:
            return 7
        return 8

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Divine Punishment"
        self.whole_round_duration = True
        self.has_limit = True
        self.limit = self.get_limit()
        self.root = None
        self.capital_hit = 0

    def shut_down(self):
        self.capital_hit = 0

    def handle_removal(self, territory):
        n_trtys = []
        neighbors = territory.neighbors
        for ne in neighbors:
            n_trtys.append(self.game.world.territories[ne])
        for n_trty in n_trtys:
            for n in neighbors:
                if n not in n_trty.neighbors and n != n_trty.name:
                    n_trty.neighbors.append(n)
                    self.game.world.biohazard.append([n_trty.name, n])
        for n_trty in n_trtys:
            n_trty.neighbors.remove(territory.name)

    def mega_blast(self, name):
        territory = self.game.world.territories[name]
        if self.locked:
            Label(self.root, text="Skill is locked!").grid(row=2)
            return
        elif name not in self.game.world.territories:
            Label(self.root, text="Territory does not exist!").grid(row=2)
            return
        elif self.capital_hit > 0 and territory.isCapital:
            Label(self.root, text="Cannot hit more than 1 capital!").grid(row=2)
            return
        elif self.limit <= 0:
            Label(self.root, text="Limit reached!").grid(row=2)
            return
        elif name in self.player.territories:
            Label(self.root, text="Cannot attack yourself!").grid(row=2)
            return
        if self.player.hasAllies:
            for ally in self.player.allies:
                if name in ally.territories:
                    Label(self.root, text="Cannot attack ally!").grid(row=2)
                    return
        territory.destroyed = True
        if territory.isCapital:
            self.capital_hit += 1
        if territory.hasBomb:
            for player in self.game.players:
                if player.hasSkill:
                    if player.skill.name == "Tactical Blasting":
                        if name in player.skill.bombs:
                            player.skill.bombs.remove(name)
        for player in self.game.players:
            if name in player.territories:
                player.territories.remove(name)
                player.update_industrial_level()
                player.update_infrastructure()
                if len(player.territories) == 0:
                    handle_death(player, self.player)
        if territory.isCAD:
            territory.mem_stats[0].ally_socket.CAD.remove(territory)
            territory.mem_stats[0].ally_socket.CAD_destroyed += 1
        for c in self.game.world.continents:
            if name in self.game.world.continents[c]:
                self.game.world.continents[c].remove(name)
                if len(self.game.world.continents[c]) == 0:
                    self.game.world.continents[c].append("TOTAL WASTELAND")
        self.handle_removal(territory)
        del self.game.world.territories[name]
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        self.game.map_visualizer.update_destroyed_view(name)
        self.limit -= 1

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Enter name of the territory to be destroyed:").grid(row=0, column=0)
        e = Entry(self.root)
        e.grid(row=0, column=1)
        Button(self.root, text="Obliterate Territory", command=lambda: self.mega_blast(e.get())).grid(row=1)

# N8
class Tactical_Blasting(Skill):
    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Tactical Blasting"
        self.off_turn_usable = True
        self.root = None
        self.cool_down = 0
        self.bombs = []

    def set_off(self, trty):
        territory = None
        for t in self.game.world.territories:
            if t == trty:
                territory = self.game.world.territories[t]
                break
        if territory is None:
            Label(self.root, text="The territory ceased to exist!").grid(row=4)
            self.bombs.remove(trty)
            return
        if self.locked:
            Label(self.root, text="Skill locked, unable to set off").grid(row=4)
            return
        if trty not in self.bombs:
            Label(self.root, text="Bomb already set-off!").grid(row=4)
            return
        if territory.civil_war:
            Label(self.root, text="Cannot meddle internal affair!").grid(row=4)
            return
        tmp = territory.troops
        # apply damage
        damage_scale = randint(80, 100)
        survivor = m.floor(tmp - (tmp*damage_scale/100))
        territory.troops = survivor
        if territory.isCity:
            territory.isCity = False
        territory.hasBomb = False
        self.bombs.remove(trty)
        self.game.world_status.update_view()
        if territory.owner is not None:
            territory.owner.update_industrial_level()
        self.game.map_visualizer.update_view(trty)
        return

    def set_bomb(self, trty):
        pid = 0
        for player in self.game.players:
            if player == self.player:
                break
            pid += 1
        if self.locked:
            Label(self.root, text="Skill deactivated!").grid(row=4)
            return
        elif trty not in self.player.territories:
            Label(self.root, text="Not a valid territory!").grid(row=4)
            return
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(self.root, text="Cannot place more than 1 bomb per turn!").grid(row=4)
            return
        elif len(self.bombs) >= 4:
            Label(self.root, text="Max amount of on-field bombs reached!").grid(row=4)
            return
        elif trty in self.bombs:
            Label(self.root, text="Already has a bomb!").grid(row=4)
            return
        elif pid != self.game.turn:
            Label(self.root, text="Cannot place bomb outside your turn!").grid(row=4)
            return
        territory = self.game.world.territories[trty]
        if territory.hasBomb:
            Label(self.root, text="Already have bomb planted!").grid(row=4)
            return
        self.used = True
        self.bombs.append(trty)
        self.used_round = self.game.round
        territory.hasBomb = True
        Label(self.root, text="Bomb placed!").grid(row=4)
        return

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Place bomb at:").grid(row=0, column=0)
        e = Entry(self.root)
        e.grid(row=0, column=1)
        Button(self.root, text="Set bomb", command=lambda: self.set_bomb(e.get())).grid(row=1, columnspan=2)
        Label(self.root, text="Bombs ready to set off:").grid(row=2)
        cid = 0
        for trty in self.bombs:
            Button(self.root, text=f"{trty}", command=lambda t=trty: self.set_off(t)).grid(row=3, column=cid)
            cid += 1

# N10
class Industrial_Revolution(Skill):
    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Industrial Revolution"
        self.has_limit = True
        self.give_buff = True
        self.defensive = True
        self.offensive = True
        self.root = None
        self.continent_counter = {}
        # initialize counter
        self.initialize_counter()

    def initialize_counter(self):
        self.continent_counter["NA"] = 0
        self.continent_counter["CA"] = 0
        self.continent_counter["SA"] = 0
        self.continent_counter["SNOW"] = 0
        self.continent_counter["ATL"] = 0
        self.continent_counter["FA"] = 0
        self.continent_counter["EU"] = 0
        self.continent_counter["AF"] = 0
        self.continent_counter["AS"] = 0
        self.continent_counter["OC"] = 0
        self.continent_counter["JA"] = 0

    def get_continent_from(self, trty):
        for key in self.game.world.continents:
            if trty in self.game.world.continents[key]:
                return key

    def get_buff(self):
        if not self.locked:
            return [1, 0, 1, 0]
        return [0, 0, 1, 0]

    def build_city(self, trty):
        cont = self.get_continent_from(trty)
        if self.locked:
            Label(self.root, text="Skill deactivated!").grid(row=2)
            return
        if trty not in self.player.territories:
            Label(self.root, text="Territory not found!").grid(row=2)
            return
        if self.used and self.used_round == self.game.round:
            Label(self.root, text="Cannot build more than 1 city per turn!").grid(row=2)
            return
        elif self.continent_counter[cont] >= 2:
            Label(self.root, text="Cannot build more than 2 cities per continent!").grid(row=2)
            return
        terri = self.game.world.territories[trty]
        if terri.isCity or terri.isMegacity or terri.isTransportcenter:
            Label(self.root, text="Cannot build city here!").grid(row=2)
            return
        terri.isCity = True
        self.player.update_industrial_level()
        if terri.isCAD and self.player in terri.mem_stats:
            for ally in self.player.allies:
                ally.update_industrial_level()
        self.game.world_status.update_view()
        self.game.map_visualizer.update_view(trty)
        self.used = True
        self.used_round = self.game.round
        self.continent_counter[cont] += 1
        Label(self.root, text="City built").grid(row=2)

    def show_effect(self, root):
        # update root
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Enter location of the city: ").grid(row=0, column=0, padx=2, pady=2)
        e = Entry(self.root)
        e.grid(row=0, column=1)
        Button(self.root, text="Build city", command=lambda: self.build_city(e.get())).grid(row=1)


# N11
class Zealous_Expansion(Skill):
    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Zealous Expansion"
        self.give_buff = True
        self.defensive = True
        self.offensive = True
        self.root = None

    def get_buff(self):
        if not self.locked:
            return [0, 1, 1, 0]
        return [0, 0, 1, 0]

    def upgrade_level(self, level):
        if level == "":
            Label(self.root, text="Action cancelled.").grid(row=2)
        level = int(level)
        if self.locked:
            Label(self.root, text=f"Skill deactivated!").grid(row=2)
            return
        if level * 2 > self.player.stars or level <= 0:
            Label(self.root, text=f"Invalid Amount!").grid(row=2)
            return
        for i in range(level):
            self.player.stars -= 2
            self.player.upgrade_infrastructure(1)
        self.player.update_infrastructure()
        self.game.world_status.update_view()
        for widget in self.root.grid_slaves():
            widget.destroy()

    def show_effect(self, root):
        # update root
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Skill discount, 2 stars per upgrade， upgrade level by: ").grid(row=0, column=0, padx=2,
                                                                                              pady=2)
        e = Entry(self.root)
        e.grid(row=0, column=1)
        Button(self.root, text="Upgrade infrastructure", command=lambda: self.upgrade_level(e.get())).grid(row=1)


# N12
class Ares_Blessing(Skill):

    def shut_down(self):
        self.active = False

    def get_limit(self):
        if self.game.player_number < 8:
            return 4
        elif self.game.player_number < 13:
            return 5
        else:
            return 6

    def get_buff(self):
        if not self.locked:
            return [2, 2, 2, 0]
        return [0, 0, 1, 0]

    def activate(self):
        if self.locked:
            Label(self.root, text="Skill deactivated!").grid(row=1)
            return
        if self.game.stage == 3:
            Label(self.root, text="Too late to activate!").grid(row=1)
            return
        elif self.limit <= 0:
            Label(self.root, text="Limit Reached").grid(row=1)
            return
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(self.root, text="In cool-down!").grid(row=1)
            return
        elif self.active:
            Label(self.root, text="Already Activated").grid(row=1)
            return
        self.active = True
        self.used = True
        self.limit -= 1
        self.used_round = self.game.round
        Label(self.root, text="Ares' Blessing Activated").grid(row=1)

    def show_effect(self, root):
        # update root
        self.root = root
        for widget in root.grid_slaves():
            widget.destroy()
        Button(root, text="Begin Rampage", command=self.activate).grid(row=0)

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Ares' Blessing"
        self.active = False
        self.one_round_duration = True
        self.offensive = True
        self.give_buff = True
        self.has_limit = True
        self.cool_down = 1
        self.limit = self.get_limit()
        self.root = None


# N18
class Necromancer(Skill):

    def shut_down(self):
        self.active = False
        if not self.locked:
            self.player.reserves += self.accumulated
        self.accumulated = 0

    def activate(self):
        if self.locked:
            Label(self.root, text="Skill deactivated!").grid(row=1)
            return
        if self.game.stage == 3:
            Label(self.root, text="Too late to activate!").grid(row=1)
            return
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(self.root, text="In cool-down!").grid(row=1)
            return
        elif self.active:
            Label(self.root, text="Already Activated").grid(row=1)
            return
        self.active = True
        self.used = True
        self.used_round = self.game.round
        Label(self.root, text="Necromancer Activated").grid(row=1)

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Button(root, text="Fetch their souls", command=self.activate).grid(row=0)

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Necromancer"
        self.active = False
        self.one_round_duration = True
        self.cool_down = 1
        self.eater = True
        self.accumulated = 0
        self.root = None

# N19
class Operation_Prometheus(Skill):

    def shut_down(self):
        if len(self.locked_player) > 0:
            if self.locked_player[0].hasSkill:
                self.locked_player[0].skill.locked = False
                self.locked_player.clear()

    def deactivate(self, name):
        player = None
        for p in self.game.players:
            if p.name == name:
                player = p
        if player not in self.game.players:
            Label(self.root, text="Player does not exist!").grid(row=2)
            return
        elif not player.hasSkill:
            Label(self.root, text="Player does not have skill!").grid(row=2)
            return
        elif player == self.player:
            Label(self.root, text="Cannot deactivate your own skill!").grid(row=2)
            return
        elif self.locked:
            Label(self.root, text="Skill currently locked!").grid(row=2)
            return
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(self.root, text="Skill in cool-down!").grid(row=2)
            return
        elif self.limit <= 0:
            Label(self.root, text="Skill limit reached!").grid(row=2)
            return
        self.locked_player.append(player)
        player.skill.locked = True
        self.used = True
        self.limit -= 1
        self.used_round = self.game.round
        Label(self.root, text=f"{name}'s skill has been sealed.").grid(row=2)
        return

    def show_effect(self, root):
        self.root = root
        for widget in root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Enter target player: ").grid(row=0, column=0)
        e = Entry(self.root)
        e.grid(row=0, column=1)
        Button(self.root, text="Deactivate Player's Skill", command=lambda: self.deactivate(e.get())).grid(row=1,
                                                                                                        columnspan=2)

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Operation Prometheus"
        self.off_turn_usable = True
        self.has_limit = True
        self.whole_round_duration = True
        self.limit = 7 if self.game.player_number < 12 else 10
        self.cool_down = 0
        self.root = None
        self.locked_player = []
        return

# N20
class Handler_of_Wheel_of_Fortune(Skill):

    # INIT
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Handler of Wheel of Fortune"
        self.off_turn_usable = True
        self.has_limit = True
        self.limit = 7 if self.game.player_number < 12 else 10
        self.cool_down = 0
        self.root = None
        return

    def get_player_information(self, player):
        for i in range(len(self.game.players)):
            curr_p = self.game.players[i]
            if curr_p.name == player:
                player = curr_p
                return [player, i]
        return ["Not Found"]

    def swap(self, p1, p2):
        # get the names of the players to be swapped
        player1, player2 = p1.get(), p2.get()
        # get the actual player object
        player1 = self.get_player_information(player1)
        player2 = self.get_player_information(player2)
        if self.locked:
            Label(self.root, text="Skill deactivated!").grid(row=3)
            return
        # valid player names
        if player1[0] not in self.game.players or player2[0] not in self.game.players:
            Label(self.root, text="Invalid player name entered!").grid(row=3)
            return
        # skill not in cool-down
        elif self.used and self.game.round - self.used_round <= self.cool_down:
            Label(self.root, text="Skill in cool-down!").grid(row=3)
            return
        # player in their turn and not last player
        elif self.game.turn == player1[1] or self.game.turn == player2[1]:
            if self.game.turn != self.game.player_number - 1:
                Label(self.root, text="Player started their turn already!").grid(row=3)
                return
        # Not skipping player's turn
        elif player1[1] <= self.game.turn <= player2[1]:
            Label(self.root, text="Cannot skip turns!").grid(row=3)
            return
        elif player2[1] <= self.game.turn <= player1[1]:
            Label(self.root, text="Cannot skip turns!").grid(row=3)
            return
        elif self.limit <= 0:
            Label(self.root, text="Limit Reached!").grid(row=3)
            return
        self.used = True
        self.used_round = self.game.round
        self.limit -= 1
        # swap
        temp = self.game.players[player1[1]]
        self.game.players[player1[1]] = self.game.players[player2[1]]
        self.game.players[player2[1]] = temp
        # update info
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        #
        Label(self.root, text="W of F turned").grid(row=3)
        return

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Player 1: ").grid(row=0, column=0)
        p1 = Entry(self.root)
        p1.grid(row=0, column=1)
        Label(self.root, text="Player 2: ").grid(row=1, column=0)
        p2 = Entry(self.root)
        p2.grid(row=1, column=1)
        Button(self.root, text="Change their fate", command=lambda: self.swap(p1, p2)).grid(row=2, columnspan=2)

# N13
class Laplace_Demon(Skill):

    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Laplace's Demon"
        return

# N6
# UNDER CONSTRUCTION
class Route_Planner(Skill):

    def get_limit(self):
        return 4 if len(self.game.players) < 8 else 5

    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Route Planner"
        self.limit = self.get_limit()
        self.game.world.load_sea_routes()
        self.root = None

    def create_sea_route(self, trty1, trty2):
        if self.locked:
            Label(self.root, text="Skill currently sealed!").grid(row=0, pady=2)
            return
        elif self.limit <= 0:
            Label(self.root, text="Out of usage!").grid(row=0, pady=2)
            return

    def csr_interface(self):
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Territory 1: ").grid(row=0, column=0, pady=2)
        Label(self.root, text="Territory 2: ").grid(row=1, column=0)
        trty1 = Entry(self.root)
        trty1.grid(row=0, column=1, pady=2)
        trty2 = Entry(self.root)
        trty2.grid(row=1, column=1)
        Button(self.root, text="Create new sea route", command=lambda: self.create_sea_route(
            trty1.get(), trty2.get())).grid(row=2, columnspan=2)

    def erase_sea_route(self, trty1, trty2):
        if self.locked:
            Label(self.root, text="Skill currently sealed!").grid(row=0, pady=2)
            return
        elif self.limit <= 0:
            Label(self.root, text="Out of usage!").grid(row=0, pady=2)
            return

    def rsr_interface(self):
        for widget in self.root.grid_slaves():
            widget.destroy()
        Label(self.root, text="Territory 1: ").grid(row=0, column=0, pady=2)
        Label(self.root, text="Territory 2: ").grid(row=1, column=0)
        trty1 = Entry(self.root)
        trty1.grid(row=0, column=1, pady=2)
        trty2 = Entry(self.root)
        trty2.grid(row=1, column=1)
        Button(self.root, text="Erase sea route", command=lambda: self.erase_sea_route(
            trty1.get(), trty2.get())).grid(row=2, columnspan=2)

    def show_effect(self, root):
        self.root = root
        for widget in self.root.grid_slaves():
            widget.destroy()
        Button(self.root, text="Create Sea-route", command=self.csr_interface).grid(row=0, pady=1)
        Button(self.root, text="Erase Sea-route", command=self.rsr_interface).grid(row=1, pady=1)

# N21
# DONE
class Dictator(Skill):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.name = "Dictator"

    def amass_power(self,):
        power = random.choices([4, 5, 6], weights=(50, 30, 20), k=1)[0]
        self.player.stars += power