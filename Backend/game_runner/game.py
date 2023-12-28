# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
# Player Object
# Game Object
# World Status Display
from game_runner.map import *
from game_runner.RNG import *
from game_runner.preload_game import *

class Player:

    def __init__(self, name, sid, G):
        self.name = name
        self.territories = []
        self.industrial = 6
        self.infrastructure = 3
        self.infrastructure_upgrade = 0
        self.infrastructure_base_value = 3
        self.stars = 0
        self.reserves = 0
        self.skill = None
        self.hasAllies = False
        self.allies = []
        self.ally_socket = None
        self.alive = True
        self.capital = None
        self.conquered = False
        self.game = G
        self.sid
        # visuals
        self.insignia = None
        self.capital_icon = None
        # skills
        self.hasSkill = False
        self.skill = None
        # puppet state
        self.puppet = False
        self.master = None
        self.vassals = []
        # economy
        self.cumulative_gdp = 0

    # take best from all -> best infra, indus from all players
    def get_best_defender(self):
        hip = self.industrial
        hinfp = self.infrastructure
        best_defender = self
        for ally in self.allies:
            if ally.industrial > hip and ally.infrastructure > hinfp:
                best_defender = ally
                hip = ally.industrial
                hinfp = ally.infrastructure
            elif ally.industrial > hip and ally.infrastructure == hinfp:
                best_defender = ally
                hip = ally.industrial
                hinfp = ally.infrastructure
            elif ally.industrial == hip and ally.infrastructure > hinfp:
                best_defender = ally
                hip = ally.industrial
                hinfp = ally.infrastructure
            elif ally.industrial - hip > 2 or ally.infrastructure - hinfp > 2:
                best_defender = ally
                hip = ally.industrial
                hinfp = ally.infrastructure
        return best_defender

    def get_information_for_WS(self):
        message = ""
        CAD_report = ""
        if self.hasAllies:
            for ally in self.allies:
                message += f"|{ally.name}| "
            for trty in self.ally_socket.CAD:
                CAD_report += f"{trty.name} "
        information = [f"{self.name}",
                       f"Status: {'Alive' if self.alive else 'Eliminated'}",
                       f"Capital: {self.capital}",
                       f"Skill: {'None' if not self.hasSkill else self.skill.name}",
                       f"Industrial power: {self.industrial}",
                       f"Infrastructure power: {self.infrastructure}",
                       f"Army size: {self.get_total_force()}",
                       f"Number of territories controlled: {len(self.territories)}",
                       f"Number of cities controlled: {self.get_city_controlled()}",
                       f"Number of troops in reserve: {self.reserves}",
                       f"Amount of political power controlled: {self.stars}",
                       f"Megacities controlled: {self.get_megacities()}",
                       f"Transport hubs controlled: {self.get_transportcenters()}",
                       f"Allies: {'None' if self.allies == [] else message}",
                       f"Commonwealth Administrative Districts: ",
                       f"{CAD_report}"
                       ]
        return information

    def get_megacities(self):
        count = 0
        for territory in self.territories:
            if self.game.world.territories[territory].isMegacity:
                count += 1
        return count

    def get_transportcenters(self):
        count = 0
        for territory in self.territories:
            if self.game.world.territories[territory].isTransportcenter:
                count += 1
        return count

    def get_total_force(self):
        amount = 0
        for territory in self.territories:
            trty = self.game.world.territories[territory]
            if trty.isCAD and self in trty.mem_stats:
                amount += round(trty.troops/len(trty.mem_stats))
            else:
                amount += trty.troops
        return amount

    @staticmethod
    def get_level(city_amount):
        indus = 6
        if city_amount < 3:
            return indus
        else:
            indus += 1
            city_amount -= 3
            while city_amount >= 2:
                indus += 1
                city_amount -= 2
            return indus

    def get_city_controlled(self):
        city_amount = 0
        for territory in self.territories:
            if self.game.world.territories[territory].isCity:
                city_amount += 1
        return city_amount

    def own_continent(self, continent):
        owned = 0
        for territory in self.territories:
            if territory in continent:
                owned += 1
        return owned == len(continent)

    def get_continental_bonus(self):
        amount = 0
        if self.own_continent(self.game.world.continents["NA"]):
            amount += 7
        if self.own_continent(self.game.world.continents["CA"]):
            amount += 5
        if self.own_continent(self.game.world.continents["SA"]):
            amount += 4
        if self.own_continent(self.game.world.continents["SNOW"]):
            amount += 2
        if self.own_continent(self.game.world.continents["ATL"]):
            amount += 14
        if self.own_continent(self.game.world.continents["FA"]):
            amount += 3
        if self.own_continent(self.game.world.continents["EU"]):
            amount += 16
        if self.own_continent(self.game.world.continents["AF"]):
            amount += 10
        if self.own_continent(self.game.world.continents["AS"]):
            amount += 19
        if self.own_continent(self.game.world.continents["OC"]):
            amount += 3
        if self.own_continent(self.game.world.continents["JA"]):
            amount += 3
        return amount

    def get_deployable_troops(self):
        score = 0
        troops = 0
        for territory in self.territories:
            nation = self.game.world.territories[territory]
            if nation.isCity:
                score += 1
            if nation.isCapital:
                troops += 1
            if nation.isMegacity:
                troops += 1
            if nation.isTransportcenter:
                troops += 1
            score += 1
        if self.hasSkill:
            if self.skill.name == "Air Superiority" and self.skill.active:
                self.skill.long_arm_jurisdiction()
        troops += self.get_continental_bonus()
        if score < 9:
            return troops + 3
        troops += score//3
        return troops

    # Only update at the beginning of a turn
    def update_industrial_level(self):
        level = self.get_level(self.get_city_controlled())
        for territory in self.territories:
            if self.game.world.territories[territory].isMegacity:
                level += 1
        self.industrial = level
        return level

    def upgrade_infrastructure(self, change):
        self.infrastructure_upgrade += change

    def update_infrastructure(self):
        level = self.infrastructure_base_value + self.infrastructure_upgrade
        for territory in self.territories:
            if self.game.world.territories[territory].isTransportcenter:
                level += 1
        self.infrastructure = level


class Game:

    def __init__(self):
        # Number of players and players are related
        self.player_number = 0
        # Map
        self.world = Map()
        self.total_troops = 95
        self.players = []
        # world status/billboard
        self.world_status = None
        # global root
        self.global_root = None
        # turn counter
        self.turn = 0
        self.stage = 0
        # preload-game
        self.preload = 0
        self.pre_set_game = game_generator()
        # max number of allies allowed in an alliance
        self.max_allies = 2
        # public billboard
        self.public_billboard = None
        # Map visualizer
        self.map_visualizer = None
        # All logos
        self.insignias = ["visual_assets/INSIGNIAS/insignia1.png", "visual_assets/INSIGNIAS/insignia2.png",
        "visual_assets/INSIGNIAS/insignia3.png", "visual_assets/INSIGNIAS/insignia4.png",
        "visual_assets/INSIGNIAS/insignia5.png", "visual_assets/INSIGNIAS/insignia6.png",
        "visual_assets/INSIGNIAS/insignia7.png", "visual_assets/INSIGNIAS/insignia8.png",
        "visual_assets/INSIGNIAS/insignia9.png", "visual_assets/INSIGNIAS/insignia10.png",
        "visual_assets/INSIGNIAS/insignia11.png", "visual_assets/INSIGNIAS/insignia12.png",
        "visual_assets/INSIGNIAS/insignia13.png", "visual_assets/INSIGNIAS/insignia14.png",
        "visual_assets/INSIGNIAS/insignia15.png", "visual_assets/INSIGNIAS/insignia16.png",
        "visual_assets/INSIGNIAS/insignia17.png", "visual_assets/INSIGNIAS/insignia18.png",
        "visual_assets/INSIGNIAS/insignia19.png", "visual_assets/INSIGNIAS/insignia20.png",
        "visual_assets/INSIGNIAS/insignia21.png", "visual_assets/INSIGNIAS/insignia22.png",
        "visual_assets/INSIGNIAS/insignia23.png", "visual_assets/INSIGNIAS/insignia24.png",
        "visual_assets/INSIGNIAS/insignia25.png", "visual_assets/INSIGNIAS/insignia26.png",
        "visual_assets/INSIGNIAS/insignia27.png", "visual_assets/INSIGNIAS/insignia28.png",
        "visual_assets/INSIGNIAS/insignia29.png", "visual_assets/INSIGNIAS/insignia30.png"]
        self.capitals = [
            "visual_assets/CAPITALS/capital1.png",
            "visual_assets/CAPITALS/capital2.png",
            "visual_assets/CAPITALS/capital3.png",
            "visual_assets/CAPITALS/capital4.png",
            "visual_assets/CAPITALS/capital5.png",
            "visual_assets/CAPITALS/capital6.png",
            "visual_assets/CAPITALS/capital7.png",
            "visual_assets/CAPITALS/capital8.png",
            "visual_assets/CAPITALS/capital9.png",
            "visual_assets/CAPITALS/capital10.png",
            "visual_assets/CAPITALS/capital11.png",
            "visual_assets/CAPITALS/capital12.png",
            "visual_assets/CAPITALS/capital13.png",
            "visual_assets/CAPITALS/capital14.png",
            "visual_assets/CAPITALS/capital15.png",
            "visual_assets/CAPITALS/capital16.png",
            "visual_assets/CAPITALS/capital17.png",
            "visual_assets/CAPITALS/capital18.png",
            "visual_assets/CAPITALS/capital19.png",
            "visual_assets/CAPITALS/capital20.png",
            "visual_assets/CAPITALS/capital21.png",
            "visual_assets/CAPITALS/capital22.png",
            "visual_assets/CAPITALS/capital23.png",
            "visual_assets/CAPITALS/capital24.png",
            "visual_assets/CAPITALS/capital25.png",
            "visual_assets/CAPITALS/capital26.png",
            "visual_assets/CAPITALS/capital27.png",
            "visual_assets/CAPITALS/capital28.png",
        ]
        self.cads = [
            "visual_assets/CAD/CAD1.png",
            "visual_assets/CAD/CAD2.png",
            "visual_assets/CAD/CAD3.png",
            "visual_assets/CAD/CAD4.png",
            "visual_assets/CAD/CAD5.png",
            "visual_assets/CAD/CAD6.png",
            "visual_assets/CAD/CAD7.png"
        ]
        self.ps = [
            "visual_assets/PUPPET_STATES/ps1.png",
            "visual_assets/PUPPET_STATES/ps2.png",
            "visual_assets/PUPPET_STATES/ps3.png",
            "visual_assets/PUPPET_STATES/ps4.png",
            "visual_assets/PUPPET_STATES/ps5.png",
            "visual_assets/PUPPET_STATES/ps6.png",
            "visual_assets/PUPPET_STATES/ps7.png",
            "visual_assets/PUPPET_STATES/ps8.png",
            "visual_assets/PUPPET_STATES/ps9.png",
            "visual_assets/PUPPET_STATES/ps10.png"
        ]
        self.insignias_used = []
        self.capitals_used = []
        self.cads_used = []
        self.p_counter = 0
        # loop elements update on async
        self.curr_reinforcer = None
        self.curr_conqueror = None
        # for skills
        self.round = 0

    # Territory distribution
    def distribute_territories(self):
        forces = {}
        if self.preload:
            pre_set_forces = self.pre_set_game.games[self.player_number]
            for fid in range(1, self.player_number + 1, 1):
                forces[f"Force {fid} :"] = pre_set_forces[fid-1]
            return forces
        nations = self.world.names
        indexes = [i for i in range(0, 95)]
        random.shuffle(indexes)
        for fid in range(1, self.player_number + 1, 1):
            forces[f"Force {fid} :"] = []
        curr = 1
        while len(indexes) != 0:
            forces[f"Force {curr} :"].append(nations[indexes.pop(0)])
            curr += 1
            if curr > self.player_number:
                curr = 1
        return forces

    def add_player(self, name, insig, cap):
        player = Player(name, self)
        player.insignia = insig
        player.capital_icon = cap
        self.insignias_used.append(insig)
        self.capitals_used.append(cap)
        self.p_counter += 1
        self.players.append(player)
        # update player number
        self.player_number = len(self.players)

    # CU
    def add_puppet_state(self, name, cap, master):
        player = Player(name, self)
        insig = get_ps(self.ps)
        player.insignia = insig
        player.capital_icon = cap
        player.puppet = True
        player.master = master
        self.p_counter += 1
        self.players.append(player)
        self.player_number = len(self.players)
        self.public_billboard.update_view()
        self.world_status.update_view()

    def shuffle_order(self):
        random.shuffle(self.players)
        return [player.name for player in self.players]

    @staticmethod   # takes in a player object
    def get_total_force_of(player):
        return player.get_total_force()

    def get_industrialized_forces(self):
        return [p for p in self.players if p.industrial > 6]

    def get_industrialized_forces_map(self):
        return [p for p in self.players if p.get_city_controlled() > 2 or p.get_megacities() > 0]

    def get_superpowers(self):
        highest_troops = 0
        highest_territories = 0
        highest_industrial = 0
        highest_infrastructure = 0
        htp = None
        htrtyp = None
        hip = None
        hinfra = None
        superpower = "Yet to be born"
        for player in self.players:
            tmp_t = player.get_total_force()
            tmp_trty = len(player.territories)
            tmp_indus = player.industrial
            tmp_infra = player.infrastructure
            if tmp_t > highest_troops:
                highest_troops = tmp_t
                htp = player.name
            if tmp_trty > highest_territories:
                highest_territories = tmp_trty
                htrtyp = player.name
            if tmp_indus > highest_industrial:
                highest_industrial = tmp_indus
                hip = player.name
            if tmp_infra > highest_infrastructure:
                highest_infrastructure = tmp_infra
                hinfra = player.name
        names = [htp, hip, htrtyp, hinfra]
        for name in names:
            if names.count(name) >= 3:
                superpower = name
                break
        return [htp, htrtyp, hip, hinfra, superpower]

    def get_active_player(self):
        amount = 0
        for player in self.players:
            if player.alive:
                amount += 1
        return amount

    # For initial view
    @staticmethod
    def get_random_insig(num):
        return get_insignias(num)

    def get_total_troops(self):
        self.total_troops = 0
        for trty in self.world.territories:
            trty = self.world.territories[trty]
            if trty.owner in self.players:
                self.total_troops += trty.troops
        return self.total_troops

