# 21 OCT 2022 by Jasper Wang, separation of blitz_roller from game_loop_GUI
# Handle of battle data, territory transfer and death.
from game_runner.game import *
from tkinter import *
import math as m
from game_runner.death_handler import handle_elimination

def Blitz_roll(attacker, defender, trty_A, trty_D, A, D):
    ####### DATA INITIALIZATION #######
    A_max, A_dice, D_max, D_dice = 0, 0, 0, 0
    A_troops, D_troops = A, D
    # multiplier
    A_mul, D_mul = 1, 1
    # nullification
    A_nul, D_nul = 0, 0

    # if defender is special regions
    if defender is None and D > 0:
        if trty_D.isMegacity:
            D_max, D_dice = 7, 2
        if trty_D.isTransportcenter:
            D_max, D_dice = 6, 3
    # take from player stats
    else:
        D_max, D_dice = defender.industrial, defender.infrastructure - 1
        # SKILL EFFECT FOR DEF
        if defender.hasSkill:
            if defender.skill.give_buff and defender.skill.active and defender.skill.defensive:
                buff = defender.skill.get_buff()
                D_max += buff[0]
                D_dice += buff[1]
                D_mul = buff[2]
                D_nul = buff[3]

    A_max, A_dice = attacker.industrial, attacker.infrastructure
    # SKILL EFFECT FOR ATK
    if attacker.hasSkill:
        if attacker.skill.give_buff and attacker.skill.active and attacker.skill.offensive:
            buff = attacker.skill.get_buff()
            A_max += buff[0]
            A_dice += buff[1]
            A_mul = buff[2]
            A_nul = buff[3]

    # Biohazard
    if [trty_A.name, trty_D.name] in attacker.game.world.biohazard:
        A = m.floor(0.6*A)

    # display parameters
    print(A_max, A_dice, D_max, D_dice, A, D)
    print(A_mul, D_mul, A_nul, D_nul)
    # battle loop
    while not (A <= 0 or D <= 0):

        # Update dice number if player has less troops than dice number
        if A < A_dice:
            A_dice = A
        if D < D_dice:
            D_dice = D

        # get rolls
        A_rolls = get_rolls(A_dice, A_max)
        D_rolls = get_rolls(D_dice, D_max)
        comp = min(len(A_rolls), len(D_rolls))

        # Compare and add up damage
        A_dmg, D_dmg = 0, 0
        for i in range(comp):
            if A_rolls[i] > D_rolls[i]:
                A_dmg += 1
            else:
                D_dmg += 1

        # Apply multiplier:
        A_dmg *= A_mul
        D_dmg *= D_mul

        # Apply Nullification:
        if get_rolls(1, 100)[0] <= A_nul:
            D_dmg = 0
        if get_rolls(1, 100)[0] <= D_nul:
            A_dmg = 0

        print(A_dmg, D_dmg)
        # Deal damage
        A -= D_dmg
        D -= A_dmg

    # overkill handle
    if A <= 0 and D <= 0:
        D = 1

    return [A, D, A_troops, D_troops]


def handle_territorial_change(attacker, defender, trty_A, trty_D, A_remain, A_survived, display_frame):
    # defender pov
    # defender is not neutral force
    if defender is not None:
        # remove trty from player pov
        defender.territories.remove(trty_D.name)
        if defender.hasAllies:
            if trty_D.isCAD:
                # remove trty from defender allies
                # update their stats
                if defender in trty_D.mem_stats:
                    for ally in defender.allies:
                        ally.territories.remove(trty_D.name)
                        # this could be the ally's last territory
                        if len(ally.territories) == 0:
                            ally.alive = False
                            attacker.reserves += ally.reserves
                            attacker.stars += ally.stars
                            ally.reserves -= ally.reserves
                            ally.stars -= ally.stars
                            ally.hasSkill = False
                            ally.skill = None
                            # try to redistribute, could fail
                            ally.ally_socket.fallen_allies.append(ally)
                        ally.update_industrial_level()
                        ally.update_infrastructure()
        # if defender is dead
        if len(defender.territories) == 0:
            Label(display_frame, text=f"{defender.name} has been eliminated").grid(row=3, padx=1, pady=1)
            handle_elimination(defender, attacker, display_frame)
        else:
            # update defender stats
            defender.update_industrial_level()
            defender.update_infrastructure()

    # territory pov
    trty_D.owner = attacker

    # attacker pov
    attacker.territories.append(trty_D.name)
    if attacker.hasAllies:
        if trty_D.isCAD:
            if attacker in trty_D.mem_stats:
                for ally in attacker.allies:
                    ally.territories.append(trty_D.name)

    # remaining troops in territories
    trty_A.troops = A_remain
    trty_D.troops = A_survived
    attacker.conquered = True


# grid policy
def Blitz_result_handle(attacker, defender, trty_A, trty_D, display_frame, result):
    A_survived, D_survived, A_sent_in, D_sent_in = result[0], result[1], result[2], result[3]

    # remaining troops in the attacker's territory:
    A_remain = trty_A.troops - A_sent_in

    # HANDLE ATK FAILURE
    if A_survived <= 0:
        Label(display_frame, text="Defender Won.").grid(row=0, padx=1, pady=1)
        Label(display_frame, text=f"Remaining troops on attacker's territory: {A_remain}").grid(row=1, padx=1, pady=1)
        Label(display_frame, text=f"Remaining troops on defender's territory: {D_survived}").grid(row=2, padx=1, pady=1)
        # NO TERRITORIAL CHANGE
        trty_D.troops = D_survived
        trty_A.troops = A_remain

    # HANDLE ATK SUCCESS
    else:
        Label(display_frame, text="Attacker Won.").grid(row=0, padx=1, pady=1)
        Label(display_frame, text=f"Remaining troops on attacker's territory: {A_remain}").grid(row=1, padx=1, pady=1)
        Label(display_frame, text=f"{A_survived} troops in newly conquered land").grid(row=2, padx=1, pady=1)
        if attacker.hasSkill:
            if attacker.skill.active and attacker.skill.eater:
                attacker.skill.accumulated += D_sent_in
        handle_territorial_change(attacker, defender, trty_A, trty_D, A_remain, A_survived, display_frame)
