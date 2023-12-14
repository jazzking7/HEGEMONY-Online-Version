# AUTHOR: JASPER WANG   DATE: 19 DEC 2022   GOAL: SEPARATION OF DEATH HANDLER FROM BLITZ_ROLLER
from tkinter import *

def handle_elimination(defender, attacker, display_frame):

    # Elimination of a single player
    defender.alive = False
    attacker.reserves += defender.reserves
    attacker.stars += defender.stars
    defender.reserves -= defender.reserves
    defender.stars -= defender.stars
    defender.hasSkill = False
    defender.skill = None
    if len(defender.vassals) > 0:
        new_master = defender.vassals[0]
        new_master.puppet = False
        for vassal in defender.vassals:
            if vassal != new_master:
                vassal.master = new_master

    # Handle alliance
    if defender.hasAllies:
        counted = []
        for ally in defender.allies:
            for territory in ally.territories:
                if territory not in counted:
                    counted.append(territory)
        # No more territories, alliance is eliminated
        if len(counted) == 0:
            Label(display_frame, text=f"{defender.ally_socket.name} has been eliminated").grid(row=4, padx=1, pady=1)
            # remove all CADs
            for trty in defender.ally_socket.CAD:
                trty.isCAD = False
                trty.mem_stats = []
        # Not enough territories
        elif len(counted) < len(defender.allies)+1:
            rowid = 4
            for ally in defender.allies:
                if len(ally.territories) == 0:
                    Label(display_frame, text=f"{ally.name} has been eliminated").grid(row=rowid, padx=1, pady=1)
                    ally.alive = False
                    attacker.reserves += ally.reserves
                    attacker.stars += ally.stars
                    ally.reserves -= ally.reserves
                    ally.stars -= ally.stars
                    ally.hasSkill = False
                    ally.skill = None
                    rowid += 1
                    if len(ally.vassals) > 0:
                        new_master = ally.vassals[0]
                        new_master.puppet = False
                        for vassal in ally.vassals:
                            if vassal != new_master:
                                vassal.master = new_master
        else:
            # redistribute territories
            defender.ally_socket.fallen_allies.append(defender)
            rowid = 4
            for ally in defender.allies:
                if len(ally.territories) == 0:
                    if ally not in defender.ally_socket.fallen_allies:
                        Label(display_frame, text=f"{ally.name} has been eliminated").grid(row=rowid, padx=1, pady=1)
                        ally.alive = False
                        attacker.reserves += ally.reserves
                        attacker.stars += ally.stars
                        ally.reserves -= ally.reserves
                        ally.stars -= ally.stars
                        defender.ally_socket.fallen_allies.append(ally)
                        ally.hasSkill = False
                        ally.skill = None
                        if len(ally.vassals) > 0:
                            new_master = ally.vassals[0]
                            new_master.puppet = False
                            for vassal in ally.vassals:
                                if vassal != new_master:
                                    vassal.master = new_master
                        rowid += 1
    if attacker.puppet:
        attacker.master.reserves += attacker.reserves
        attacker.reserves -= attacker.reserves
        attacker.master.stars += attacker.stars
        attacker.stars -= attacker.stars
    return

def handle_death(defender, attacker):

    # Elimination of a single player
    defender.alive = False
    attacker.reserves += defender.reserves
    attacker.stars += defender.stars
    defender.reserves -= defender.reserves
    defender.stars -= defender.stars
    defender.hasSkill = False
    defender.skill = None
    if len(defender.vassals) > 0:
        new_master = defender.vassals[0]
        new_master.puppet = False
        for vassal in defender.vassals:
            if vassal != new_master:
                vassal.master = new_master
    # Handle alliance
    if defender.hasAllies:
        counted = []
        for ally in defender.allies:
            for territory in ally.territories:
                if territory not in counted:
                    counted.append(territory)
        # No more territories, alliance is eliminated
        if len(counted) == 0:
            # remove all CADs
            for trty in defender.ally_socket.CAD:
                trty.isCAD = False
                trty.mem_stats = []
        # Not enough territories
        elif len(counted) < len(defender.allies)+1:

            for ally in defender.allies:
                if len(ally.territories) == 0:
                    ally.alive = False
                    attacker.reserves += ally.reserves
                    attacker.stars += ally.stars
                    ally.reserves -= ally.reserves
                    ally.stars -= ally.stars
                    ally.hasSkill = False
                    ally.skill = None
                    if len(ally.vassals) > 0:
                        new_master = ally.vassals[0]
                        new_master.puppet = False
                        for vassal in ally.vassals:
                            if vassal != new_master:
                                vassal.master = new_master
        else:
            # redistribute territories
            defender.ally_socket.fallen_allies.append(defender)

            for ally in defender.allies:
                if len(ally.territories) == 0:
                    if ally not in defender.ally_socket.fallen_allies:
                        ally.alive = False
                        attacker.reserves += ally.reserves
                        attacker.stars += ally.stars
                        ally.reserves -= ally.reserves
                        ally.stars -= ally.stars
                        defender.ally_socket.fallen_allies.append(ally)
                        ally.hasSkill = False
                        ally.skill = None
                        if len(ally.vassals) > 0:
                            new_master = ally.vassals[0]
                            new_master.puppet = False
                            for vassal in ally.vassals:
                                if vassal != new_master:
                                    vassal.master = new_master
    if attacker.puppet:
        attacker.master.reserves += attacker.reserves
        attacker.reserves -= attacker.reserves
        attacker.master.stars += attacker.stars
        attacker.stars -= attacker.stars
    return