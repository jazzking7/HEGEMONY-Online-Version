# Author: Jasper Wang
# Goal: civil war handler
# Date: 17 Nov 2022
from game_runner.map import *
from game_runner.game import *
from tkinter import *
from game_runner.RNG import *

class civil_war_handler:

    def civil_war_roller(self, trty):
        R = trty.internal_dist["R"]
        G = trty.internal_dist["G"]

        R_max = self.rebel_stats[0]
        R_max_dice = self.rebel_stats[1]

        G_max = self.owner_stats[0]
        G_max_dice = self.owner_stats[1]
        print(R_max, G_max, R_max_dice, G_max_dice)
        while R > 0 and G > 0:

            if R < R_max_dice:
                R_max = R
            if G < G_max_dice:
                G_max = G

            # get rolls
            R_rolls = get_rolls(R_max_dice, R_max)
            G_rolls = get_rolls(G_max_dice, G_max)
            comp = min(len(R_rolls), len(G_rolls))

            # Compare and add up damage
            R_dmg, G_dmg = 0, 0
            for i in range(comp):
                if R_rolls[i] > G_rolls[i]:
                    R_dmg += 1
                else:
                    G_dmg += 1

            R -= G_dmg
            G -= R_dmg

        if R <= 0 and G <= 0:
            G = 1

        trty.civil_war = False
        if R > 0:
            trty.owner = self.rebel
            self.rebel.territories.append(trty.name)
            trty.troops = R
        else:
            trty.owner = self.owner
            self.owner.territories.append(trty.name)
            trty.troops = G
            if trty.isCAD and self.owner in trty.mem_stats:
                for ally in self.owner.allies:
                    ally.territories.append(trty.name)
        self.game.map_visualizer.update_view(trty.name)

    # need debugging
    def settle_cw(self):
        for event in zip(self.entries, self.contested_regions):
            if event[0].get() == "1":
                self.civil_war_roller(event[1])
            else:
                safe_zone = self.game.world.get_uncontested_regions(self.owner, event[1].name,
                                                                    [], [], self.owner.allies)
                #print(safe_zone)
                if len(safe_zone) > 0:
                    event[1].civil_war = False
                    self.game.world.territories[safe_zone[0]].troops += event[1].internal_dist["G"]
                    event[1].owner = self.rebel
                    event[1].troops = event[1].internal_dist["R"]
                    self.rebel.territories.append(event[1].name)
                else:
                    self.civil_war_roller(event[1])
        self.main_frame.destroy()

    def get_stats(self, player):
        c = 0
        ind = 6
        for trty in player.territories:
            if self.game.world.territories[trty].isCity:
                c += 1
        if c > 2:
            ind += 1
            while c > 1:
                ind += 1
                c -= 2
        for trty in player.territories:
            if self.game.world.territories[trty].isMegacity:
                ind += 1
        level = player.infrastructure_base_value + player.infrastructure_upgrade
        for territory in player.territories:
            if self.game.world.territories[territory].isTransportcenter:
                level += 1
        return [ind, level]

    def __init__(self, game, contested_regions, owner, rebel):
        self.game = game
        self.contested_regions = contested_regions
        self.owner = owner
        self.rebel = rebel
        self.main_frame = Toplevel()
        self.entries = []
        self.owner_stats = self.get_stats(owner)
        self.rebel_stats = self.get_stats(rebel)

        self.rowid = 0
        for trty in contested_regions:
            r = trty.internal_dist['R']
            g = trty.internal_dist['G']
            Label(self.main_frame, text=trty.name+f": {r} vs {g}").grid(row=self.rowid, column=0)
            e = Entry(self.main_frame)
            e.grid(row=self.rowid, column=1)
            e.insert(0, "1")
            self.entries.append(e)
            self.rowid += 1

        Button(self.main_frame, text="Settle Civil War", command=self.settle_cw).grid(row=self.rowid, columnspan=2)

class puppet_capital_setter:

    def __init__(self, game, player, signal):
        self.game = game
        self.player = player
        self.main_frame = Toplevel()
        self.main_frame.wait_window(signal.main_frame)
        self.entries = []
        self.rowid = 0

        for trty in self.player.territories:
            Label(self.main_frame, text=trty+": ").grid(row=self.rowid, column=0)
            e = Entry(self.main_frame)
            e.grid(row=self.rowid, column=1)
            e.insert(0, "0")
            self.entries.append(e)
            self.rowid += 1

        Button(self.main_frame, text="Set capital", command=self.set_capital).grid(row=self.rowid, columnspan=2)

    def set_capital(self):
        c_set = False
        for event in zip(self.entries, self.player.territories):
            if event[0].get() != "0":
                self.player.capital = event[1]
                self.game.world.territories[event[1]].isCapital = True
                c_set = True
                break
        if not c_set and len(self.player.territories) > 0:
            Label(self.main_frame, text="Pick a capital!").grid(row=self.rowid+1)
            return
        self.main_frame.destroy()


class cw_buffer:

    def __init__(self, signal):
        self.main_frame = Toplevel()
        self.main_frame.wait_window(signal.main_frame)
        self.main_frame.destroy()
        return

