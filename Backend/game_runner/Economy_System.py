from game_runner.game import *
from tkinter import *

class Economy_Updater:

    def __init__(self, game):
        self.game = game

    def add_gdp_to_player(self, player):
        total_value = 0
        for trty in player.territories:
            territory = self.game.world.territories[trty]
            if territory.isCapital:
                total_value += 5
            if territory.isCity:
                total_value += 2
            elif territory.isMegacity:
                total_value += 3
            elif territory.isTransportcenter:
                total_value += 3
            elif territory.isSEZ:
                total_value += 3
            else:
                total_value += 1
        player.cumulative_gdp += total_value

    def add_gdp_to_players(self,):
        for player in self.game.players:
            if player.alive:
                self.add_gdp_to_player(player)

class Economy_User:

    def __init__(self, game):
        self.game = game
        self.interface = Tk()
        self.menu = LabelFrame(root=self.interface, text="Management Menu")
        self.menu.grid(row=0, column=0)
        Label(root=self.menu, text="Options: ", padx=2, pady=2).grid(row=0, column=0)
        Label(root=self.menu, text="Actions to be taken:", padx=2, pady=2).grid(row=1, column=0)

