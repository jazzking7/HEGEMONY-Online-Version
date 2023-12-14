# 20 Oct 2022 by Jasper Wang to create inter-player-communication
# Alliance and puppet state
from tkinter import *
class Alliance:

    def add_member(self, new_player):
        # Update member states
        # Establish relation with all member states
        new_player.hasAllies = True
        for player in self.member_states:
            new_player.allies.append(player)
            player.allies.append(new_player)
        self.member_states.append(new_player)
        # Player has access to socket
        new_player.ally_socket = self

        # Update max CAD
        new_limit = self.get_max_CAD(len(self.member_states))
        self.CAD_deployable = new_limit - len(self.CAD) - self.CAD_destroyed

        # player know CAD
        for territory in self.CAD:
            # CAD know legitimate rulers
            territory.mem_stats = self.member_states
            # if CAD is not invaded
            if territory.owner in self.member_states:
                # if CAD is not in player.territories
                if territory.name not in new_player.territories:
                    new_player.territories.append(territory.name)
        new_player.update_industrial_level()
        new_player.update_infrastructure()
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        return

    def create_CAD(self, player, territory_name):
        # initial clearance
        if territory_name not in player.territories:
            return [False, "NE"]
        if self.CAD_deployable <= 0:
            return [False, "NOCAD"]
        # get territory
        territory = self.game.world.territories[territory_name]
        # avoid duplicate and overwrite
        if territory.isCAD:
            return [False, "ALDCAD"]
        if self.game.stage == 2:
            return [False, "NRT"]
        if self.CAD_logo is None:
            return [False, "NCL"]
        # update territory knows member states
        territory.isCAD = True
        territory.mem_stats = self.member_states
        # update member states know territory
        for mem_sts in self.member_states:
            if territory_name not in mem_sts.territories:
                mem_sts.territories.append(territory_name)
        # Decrement the count
        self.CAD_deployable -= 1
        self.CAD.append(territory)

        # Update Views
        for player in self.member_states:
            player.update_industrial_level()
            player.update_infrastructure()
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        self.game.map_visualizer.update_view(territory_name)
        return [True, "Creation Successful"]

    def get_retrievable_reserves(self, demander):
        amount = 0
        for player in self.member_states:
            if player.name != demander.name:
                amount += player.reserves
        return amount

    def get_retrievable_stars(self, demander):
        amount = 0
        for player in self.member_states:
            if player.name != demander.name:
                amount += player.stars
        return amount

    def transfer_reserves(self, demander, amount):
        if amount > self.get_retrievable_reserves(demander):
            return [False, "EXCESS"]
        # Demander gain reserves
        demander.reserves += amount
        # Member states transfer troops
        for member in self.member_states:
            if member.name != demander.name:
                if member.reserves == 0:
                    continue
                else:
                    if member.reserves >= amount:
                        member.reserves -= amount
                        break
                    else:
                        amount -= member.reserves
                        member.reserves = 0
        return [True, "Transfer Successful"]

    def transfer_stars(self, demander, amount):
        if amount > self.get_retrievable_stars(demander):
            return [False, "EXCESS"]
        # Demander gain stars
        demander.stars += amount
        # Member states transfer troops
        for member in self.member_states:
            if member.name != demander.name:
                if member.stars == 0:
                    continue
                else:
                    if member.stars >= amount:
                        member.stars -= amount
                        break
                    else:
                        amount -= member.stars
                        member.stars = 0
        return [True, "Transfer Successful"]

    @staticmethod
    def get_max_CAD(number_of_allies):
        if number_of_allies == 2:
            return 4
        elif number_of_allies == 3:
            return 5
        else:
            return 6

    def __init__(self, player1, player2, game):

        # Initial stats
        self.name = None
        self.CAD_logo = None
        self.game = game
        self.member_states = [player1, player2]
        self.CAD_deployable = self.get_max_CAD(len(self.member_states))
        # holds territory objects
        self.CAD = []
        # signals for redistribution
        self.fallen_allies = []
        self.CAD_destroyed = 0

        # Let members connect to each other
        player1.hasAllies = True
        player1.allies.append(player2)
        player1.ally_socket = self

        player2.hasAllies = True
        player2.allies.append(player1)
        player2.ally_socket = self

        return

