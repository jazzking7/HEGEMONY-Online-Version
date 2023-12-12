from game_runner.GUI_initiate_game import *
from game_runner.RNG import *
from game_runner.Blitz_Roller import *
import math as m

# LOOP WINDOWS:
class REINFORCER:

    def update_info(self):
        message = f"{self.player.name}'s turn, {self.deployable_troops} troops available from territorial control and\n"
        message += f"{self.player.reserves} troops in reserve."
        self.announcement.grid_remove()
        self.announcement = Label(self.main_frame, text=message)
        self.announcement.grid(row=0, column=0, padx=2, pady=2)

    def enter_data(self):
        amount = 0
        for e in self.entries:
            amount += int(e.get())
        if amount != self.deployable_troops:
            if amount < self.deployable_troops:
                Label(self.main_frame, text=f"Must deploy at least {self.deployable_troops} soldiers!").grid(row=0,
                                                                                                             column=1)
                return
            if self.player.reserves < amount - self.deployable_troops:
                Label(self.main_frame, text="Too much troops!").grid(row=0, column=1)
                return
            self.player.reserves -= amount - self.deployable_troops

        for i in range(len(self.entries)):
            change = int(self.entries[i].get())
            self.game.world.territories[self.player.territories[i]].troops += change
            self.game.map_visualizer.update_view(self.player.territories[i])
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        self.main_frame.destroy()

    def __init__(self, game, root, player, rowid, cid):
        self.game = game
        # 19/10/22 (C310試験前　マジふざけている)
        # こちらの変化は周りと違って、同期されている。つまり、１にセットされたら、すぐしたのコードで２に変更されているということ。
        # 故に、例えしたのプリントは１を出したとしても、都市を作ることはできない。　本当の価値はすでに2になったのだ。
        # この問題の解決策の一つは、ゲームステージの変更は２と３に任せて、使える価値はゼロと１のみ。
        # 19/10/22 (C310試験後)
        # 新たな解決策を見つかった、ゲームステージの変更は、次のウィンドウ待機の後で行うこと。
        self.game.stage = 1
        self.player = player
        self.main_frame = Frame(root)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.deployable_troops = self.player.get_deployable_troops()
        message = f"{player.name}'s turn, {self.deployable_troops} troops available from territorial control and\n"
        message += f"{player.reserves} troops in reserve."
        self.announcement = Label(self.main_frame, text=message)
        self.announcement.grid(row=0, column=0, padx=2, pady=2)
        self.options = VSF(self.main_frame, 1, 0)
        self.entries = []
        rowid = 0
        for territory in self.player.territories:
            Label(self.options.show_frame, text=f"{territory}: +").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(self.options.show_frame)
            e.grid(row=rowid, column=1, padx=2, pady=2)
            e.insert(0, "0")
            self.entries.append(e)
            rowid += 1
        Button(self.main_frame, text="Deploy", command=self.enter_data).grid(row=2, column=0, padx=2, pady=2)


class CONQUER:

    # CRUCIAL
    def blitz_result(self, e, Roller, attacker, defender):
        # Airdrop
        if defender in self.airdrop_options:
            if self.player.hasSkill:
                if self.player.skill.name == "Air Superiority":
                    if self.player.skill.limit == 0:
                        Label(self.battle_result, text="Airdrop limit reached!").grid(row=0, column=0, padx=2, pady=2)
                        return
                    else:
                        self.player.skill.limit -= 1
        trty_A = self.game.world.territories[attacker]
        trty_D = self.game.world.territories[defender]
        attacker = trty_A.owner
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

        A = int(e.get())
        if A >= trty_A.troops:
            Label(self.battle_result, text="Too much troops!").grid(row=0, column=0, padx=2, pady=2)
            return
        D = trty_D.troops
        Roller.destroy()

        # get battle results
        result = Blitz_roll(attacker, defender, trty_A, trty_D, A, D)

        # clear previous battle results
        for widget in self.battle_result.grid_slaves():
            widget.destroy()

        # update new battle results
        Blitz_result_handle(attacker, defender, trty_A, trty_D, self.battle_result, result)

        # live_map update
        self.game.map_visualizer.update_view(trty_D.name)
        self.game.map_visualizer.update_view(trty_A.name)
        # show new attack options
        self.refresh()

    def refresh(self):
        # reflect territorial changes on attack options
        self.get_attack_options()
        # Show defender stat change and territorial change
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()

    def get_roller(self, attacker, defender):
        for widget in self.battle_ready.grid_slaves():
            widget.destroy()
        Roller = Frame(self.battle_ready)
        Roller.grid(row=0, column=0, padx=2, pady=2)
        if self.game.world.territories[attacker].troops <= 1:
            Label(self.battle_result, text="Unable to attack!").grid(row=0, column=0, padx=2, pady=2)
            return
        Label(Roller, text="Send in: ").grid(row=0, column=0, padx=2, pady=2)
        e = Entry(Roller)
        e.grid(row=0, column=1, padx=2, pady=2)
        e.insert(0, f"{self.game.world.territories[attacker].troops - 1}")
        Button(Roller, text="Battle", command=lambda: self.blitz_result(e, Roller, attacker, defender)).grid(row=1,
                                                                                                        columnspan=2,
                                                                                                             padx=2,
                                                                                                             pady=2)

    # Function that actually computes who can be attacked
    def show_neighbors(self, territory):
        for widget in self.battle_ready.grid_slaves():
            widget.destroy()
        valid_attack = []
        for neighbor in self.game.world.territories[territory].neighbors:
            # Not owned by player
            if neighbor not in self.player.territories:
                # Not an ally
                if self.game.world.territories[neighbor].owner not in self.player.allies:
                    valid_attack.append(neighbor)
        if self.player.hasSkill:
            if self.player.skill.name == "Air Superiority":
                all_options = self.game.world.get_reachable_airspace(territory, [territory], 1, 5)
                airdrop_options = []
                for option in all_options:
                    if option not in valid_attack and option not in self.player.territories:
                        if self.game.world.territories[option].owner not in self.player.allies:
                            airdrop_options.append(option)
                self.airdrop_options = airdrop_options
                valid_attack += airdrop_options
        rowid = 0
        cid = 0
        for option in valid_attack:
            Button(self.battle_ready, text=option, command=lambda op=option: self.get_roller(territory, op)).grid(
                row=rowid, column=cid, padx=2, pady=2)
            cid += 1
            if cid == 3:
                cid = 0
                rowid += 1

    def get_attack_options(self):
        for widget in self.options.show_frame.grid_slaves():
            widget.destroy()
        rowid = 0
        cid = 0
        for territory in self.player.territories:
            Button(self.options.show_frame, text=f"{territory}",
                   command=lambda t=territory: self.show_neighbors(t)).grid(row=rowid, column=cid, padx=2, pady=2)
            cid += 1
            if cid == 3:
                cid = 0
                rowid += 1
        rowid += 1
        # To fix a bug where the vertical scroll bar has a fixed size that
        # is prefixed at the start of every turn
        for i in range(10):
            Label(self.options.show_frame, text="").grid(row=rowid)
            rowid += 1
        return

    def update_player_stats(self):
        # keep player stats up-to-date
        self.player.update_industrial_level()
        self.player.update_infrastructure()
        # turn off one round duration skills
        if self.player.hasSkill:
            if self.player.skill.one_round_duration:
                self.player.skill.shut_down()
        if self.player.hasAllies:
            for ally in self.player.allies:
                ally.update_industrial_level()
                ally.update_infrastructure()
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        self.main_frame.destroy()

    def __init__(self, game, root, player, signal, rowid, cid):
        self.game = game
        self.player = player
        self.main_frame = Frame(root)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal)
        self.player.update_industrial_level()
        self.player.update_infrastructure()
        self.game.stage = 2
        self.airdrop_options = []
        # 0, 0
        message = f"{player.name}'s turn, conquering time"
        Label(self.main_frame, text=message).grid(row=0, column=0, padx=2, pady=2)
        # 1, 0
        self.options = VSF(self.main_frame, 1, 0)
        # 1, 2
        self.battle_result = LabelFrame(self.main_frame, text="Battle Result")
        self.battle_result.grid(row=1, column=2, padx=2, pady=2)
        # 1, 1
        # attack options
        self.battle_ready = LabelFrame(self.main_frame, text="Battle Prep")
        self.battle_ready.grid(row=1, column=1, padx=2, pady=2)
        self.get_attack_options()
        # 2, 0
        # Update current player's stat at the end of the turn
        Button(self.main_frame, text="Attack Terminated", command=self.update_player_stats).grid(row=2, column=0,
                                                                                                 padx=2, pady=2)


class REARRANGER:

    def transfer(self, e, s, d):
        departure = self.game.world.territories[s]
        destination = self.game.world.territories[d]
        amount = int(e.get())
        if amount >= departure.troops or amount == 0:
            Label(self.connected_regions.show_frame, text="Invalid Amount!").grid(row=3)
            return
        departure.troops -= amount
        if d not in self.game.world.get_safely_connected_regions(self.player, s, [], [], self.player.allies):
            amount = m.floor(0.6*amount)
        destination.troops += amount
        for widget in self.connected_regions.show_frame.grid_slaves():
            widget.destroy()
        # Update Views
        self.game.map_visualizer.update_view(s)
        self.game.map_visualizer.update_view(d)
        self.game.public_billboard.update_view()

    def transfer_prompt(self, s, d):
        for widget in self.connected_regions.show_frame.grid_slaves():
            widget.destroy()
        Label(self.connected_regions.show_frame, text="Enter transfer amount:").grid(row=0)
        e = Entry(self.connected_regions.show_frame)
        e.grid(row=1)
        e.insert(0, str(self.game.world.territories[s].troops - 1))
        Button(self.connected_regions.show_frame, text="Transfer", command=lambda: self.transfer(e, s, d)).grid(row=2)

    def displayer_c(self, territory):
        for widget in self.connected_regions.show_frame.grid_slaves():
            widget.destroy()
        rowid = 0
        cid = 0
        for connected in self.game.world.get_connected_regions(self.player, territory, [], [], self.player.allies):
            Button(self.connected_regions.show_frame, text=connected,
                   command=lambda s=territory, d=connected: self.transfer_prompt(s, d)).grid(row=rowid, column=cid)
            cid += 1
            if cid == 4:
                rowid += 1
                cid = 0
        for i in range(10):
            Label(self.connected_regions.show_frame, text="").grid(row=rowid)
            rowid += 1

    def show_starting_territories(self):
        rowid, cid = 0, 0
        for territory in self.player.territories:
            Button(self.starting_territories.show_frame, text=territory,
                   command=lambda t=territory: self.displayer_c(t)).grid(row=rowid, column=cid, padx=2, pady=2)
            cid += 1
            if cid == 3:
                rowid += 1
                cid = 0

    def __init__(self, game, root, player, signal, rowid, cid):
        self.game = game
        self.player = player
        self.main_frame = Frame(root)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal)
        self.game.stage = 3
        # 0, 1
        self.connected_regions = VSF(self.main_frame, 0, 1)
        # 0, 0
        self.starting_territories = VSF(self.main_frame, 0, 0)
        self.show_starting_territories()
        # 1, 0
        Button(self.main_frame, text="Finished Rearranging", command=self.star_distribution).grid(row=1, columnspan=2,
                                                                                                  padx=2, pady=2)

    def star_distribution(self):
        if self.player.hasSkill and self.player.skill.name == "Dictator":
            if self.player.conquered:
                self.player.skill.amass_power()
            else:
                self.player.stars += 2
        elif self.player.conquered:
            self.player.stars += get_stars()
            self.player.conquered = False
            if self.player.puppet:
                self.player.master.stars += self.player.stars
                self.player.stars -= self.player.stars
        self.game.world_status.update_view()
        self.main_frame.destroy()

# for turn changes
class BUFFER:
    def __init__(self, root, signal, destroy, rowid, cid):
        self.frame = Frame(root)
        self.frame.grid(row=rowid, column=cid)
        self.frame.wait_window(signal)
        # Kill the async of current player
        destroy.main_frame.destroy()
        self.frame.destroy()


class REDIST_PROMPT:

    def distribute(self, DATA):
        for i in range(len(DATA.territories)):
            trty = self.player.game.world.territories[DATA.territories[i]]
            if DATA.entries[i].get() != "0":
                if trty.name not in self.player.territories:
                    self.player.territories.append(DATA.territories[i])
                    trty.owner = self.player
                    if trty.isCAD and self.player in trty.mem_stats:
                        for ally in self.player.allies:
                            if trty.name not in ally.territories:
                                ally.territories.append(trty.name)
        if len(self.player.territories) > 0:
            self.player.alive = True
            if self.player in self.player.ally_socket.fallen_allies:
                self.player.ally_socket.fallen_allies.remove(self.player)
        else:
            self.player.alive = False
            if self.player not in self.player.ally_socket.fallen_allies:
                self.player.ally_socket.fallen_allies.append(self.player)

        new_options = []
        for trty in DATA.territories:
            if trty not in self.player.territories:
                new_options.append(trty)
        DATA.territories = new_options
        DATA.game.world_status.update_view()
        # Update Views
        self.main_frame.destroy()
        DATA.game.map_visualizer.update_all_view()
        DATA.game.public_billboard.update_view()

    def __init__(self, DATA, mem, rowid, cid):
        self.main_frame = Frame(DATA.main_frame)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.player = mem
        # refresh choices
        DATA.show_options()
        Button(self.main_frame, text="Confirm", command=lambda:self.distribute(DATA)).grid(row=0, column=0)
        return

class ALLY_REDISTRIBUTE:

    def obligated_territorial_gain(self, mem):
        for trty in self.territories:
            terri = self.game.world.territories[trty]
            if trty not in mem.territories:
                mem.territories.append(trty)
                terri.owner = mem
                if terri.isCAD and mem in terri.mem_stats:
                    for ally in mem.allies:
                        if trty not in ally.territories:
                            ally.territories.append(trty)
        if len(mem.territories) > 0:
            mem.alive = True
            if mem in mem.ally_socket.fallen_allies:
                mem.ally_socket.fallen_allies.remove(mem)
        else:
            mem.alive = False
            if mem not in mem.ally_socket.fallen_allies:
                mem.ally_socket.fallen_allies.append(mem)
        # Update Views
        self.game.map_visualizer.update_all_view()

    def show_options(self):
        for widget in self.options.show_frame.grid_slaves():
            widget.destroy()
        self.entries = []
        rowid = 0
        for territory in self.territories:
            Label(self.options.show_frame, text=f"{territory}: +").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(self.options.show_frame)
            e.grid(row=rowid, column=1, padx=2, pady=2)
            e.insert(0, "0")
            self.entries.append(e)
            rowid += 1
        for i in range(30):
            Label(self.options.show_frame, text=" ").grid(row=rowid)
            e = Entry(self.options.show_frame)
            e.grid(row=rowid, column=1)
            rowid += 1

    def redistribute(self):
        self.button.destroy()
        for mem in self.members:
            Label(self.main_frame, text=f"{mem.name}'s turn: ").grid(row=0, column=0, padx=2, pady=2)
            # last member
            if mem == self.members[len(self.members)-1]:
                self.obligated_territorial_gain(mem)
                break
            R = REDIST_PROMPT(self, mem, 2, 0)
            self.main_frame.wait_window(R.main_frame)
        self.main_frame.destroy()
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()

    def __init__(self, root, game, player, rowid, cid):
        self.main_frame = LabelFrame(root, text="Territory Redistribution For Fallen Allies")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.game = game
        self.player = player
        self.territories = []
        self.entries = []
        self.members = player.ally_socket.member_states
        for mem in self.members:
            for trty in mem.territories:
                if trty not in self.territories:
                    self.territories.append(trty)
        for trty in self.territories:
            self.game.world.territories[trty].owner.territories.remove(trty)
            self.game.world.territories[trty].owner = None
        self.options = VSF(self.main_frame, 1, 0)
        self.button = Button(self.main_frame, text="START", command=self.redistribute)
        self.button.grid(row=2, column=0)
        return

# for emergency
class RES_BUFFER:
    def __init__(self, root, signal, rowid, cid):
        self.frame = Frame(root)
        self.frame.grid(row=rowid, column=cid)
        self.frame.wait_window(signal)
        self.frame.destroy()