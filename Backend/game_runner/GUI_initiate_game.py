import math as m
from game_runner.GUI_helpers import *
from game_runner.SKILLS import *
# Game Step-Up
# Name, Territories, Capital, Cities, Initial Troop Distribution


# Distribution of territories
class TRTY_DIST_PROMPT:

    def enter_data(self):
        f_num = int(self.force_number.get())
        if f_num not in self.choices:
            Label(self.force_prompt, text="Not a valid choice!").grid(row=2)
            return
        for player in self.game.players:
            if player.name == self.name:
                player.territories = self.forces[f"Force {f_num} :"]
                for territory in player.territories:
                    self.game.world.territories[territory].owner = player
                    self.game.map_visualizer.update_view(territory)
                self.choices.remove(f_num)
                self.force_prompt.destroy()
                break

    def __init__(self, G, name, forces, choices):
        self.forces = forces
        self.game = G
        self.name = name
        self.choices = choices
        self.force_prompt = Toplevel()
        self.force_prompt.geometry("500x300")
        self.force_prompt.title("Hegemony")
        Label(self.force_prompt, text=f"{name}'s turn. Select from {choices}: ").grid(row=0, column=0, padx=2, pady=2)
        self.force_number = Entry(self.force_prompt)
        self.force_number.grid(row=0, column=1, padx=2, pady=2)
        self.btn = Button(self.force_prompt, text="Continue", command=self.enter_data)
        self.btn.grid(row=1, column=0, padx=2, pady=2, columnspan=2)

class TRTY_DISTRIBUTOR:

    def __init__(self, root, game, signal, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Territory Distribution")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal.main_frame)
        # Game distribute territories randomly according to the given number of players
        forces = self.game.distribute_territories()
        cid = 0
        choices = []
        for fid in forces:
            choice = f"{fid}\n"
            for name in forces[fid]:
                choice += name + "\n"
            Label(self.main_frame, text=choice).grid(row=0, column=cid, padx=2, pady=2)
            cid += 1
            choices.append(cid)
        # Shuffle and display distribution order
        order = self.game.shuffle_order()
        order_display = "Distribution Order: "
        for player in order:
            order_display += player + "\t"
        Label(self.main_frame, text=order_display).grid(row=1, columnspan=cid, padx=2, pady=2)
        # Show forces using random insigs
        self.game.map_visualizer.distribution_view(forces)

        # Function to start distribution
        def distribute():
            DIST_BTN['state'] = 'disabled'
            for p in order:
                distributor = TRTY_DIST_PROMPT(self.game, p, forces, choices)
                self.main_frame.wait_window(distributor.force_prompt)
            self.main_frame.destroy()

        DIST_BTN = Button(self.main_frame, text="Start Distribution", command=distribute)
        DIST_BTN.grid(row=2, columnspan=cid, padx=2, pady=2)


# Setting capitals
class CAP_DIST_PROMPT:

    def enter_data(self):
        invalid = True
        for i in range(len(self.entries)):
            update = False if self.entries[i].get() == "0" else True
            self.game.world.territories[self.player.territories[i]].isCapital = update
            if update:
                invalid = False
                self.player.capital = self.player.territories[i]
                self.game.map_visualizer.update_view(self.player.territories[i])
                break
        if invalid:
            Label(self.distributor, text="Choose a capital!").grid(row=0, column=1, padx=2, pady=2)
            return
        self.distributor.destroy()

    def __init__(self, G, p):
        self.player = p
        self.game = G
        self.distributor = Toplevel()
        self.distributor.title("Hegemony")
        Label(self.distributor, text=f"{self.player.name}'s turn").grid(row=0, column=0, padx=2, pady=2)
        self.entries = []
        rowid = 1
        for territory in self.player.territories:
            Label(self.distributor, text=f"{territory}: set as capital =>").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(self.distributor)
            e.insert(0, "0")
            e.grid(row=rowid, column=1, padx=2, pady=2)
            self.entries.append(e)
            rowid += 1
        Button(self.distributor,
               text="Update Territory Status",
               command=self.enter_data).grid(row=rowid, columnspan=2, padx=2, pady=2)

class CAPITAL_SETTER:

    def __init__(self, root, game, signal, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Capital Setting")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal.main_frame)
        # Display Current Status

        Label(self.main_frame, text="Current Status:").grid(row=0, column=0, padx=2, pady=2)
        cid = 0
        for player in self.game.players:
            '''
            status = f"{player.name}:\n"
            for territory in player.territories:
                trty = self.game.world.territories[territory]
                status += f"{territory}: Capital Status => {trty.isCapital}\n"
            Label(self.main_frame, text=status).grid(row=1, column=cid, padx=2, pady=2)
            '''
            cid += 1

        # Shuffle and display distribution order
        order = self.game.shuffle_order()
        order_display = "Distribution Order: "
        for player in order:
            order_display += player + "\t"
        Label(self.main_frame, text=order_display).grid(row=2, columnspan=cid, padx=2, pady=2)

        # Start Distribution
        def cap_distribute():
            DIST_BTN['state'] = 'disabled'
            for player in self.game.players:
                distributor = CAP_DIST_PROMPT(self.game, player)
                self.main_frame.wait_window(distributor.distributor)
            self.main_frame.destroy()

        DIST_BTN = Button(self.main_frame, text="Start Distribution", command=cap_distribute)
        DIST_BTN.grid(row=3, columnspan=cid, padx=2, pady=2)


# Setting cities
class C_DIST_PROMPT:

    def enter_data(self):
        c = 0
        for i in range(len(self.entries)):
            update = False if self.entries[i].get() == "0" else True
            if update:
                c += 1
        if c != 2:
            Label(self.distributor, text=f"Wrong amount of cities built!").grid(row=0, column=1, padx=2, pady=2)
            return
        for i in range(len(self.entries)):
            update = False if self.entries[i].get() == "0" else True
            self.game.world.territories[self.player.territories[i]].isCity = update
            self.game.map_visualizer.update_view(self.player.territories[i])

        self.distributor.destroy()

    def __init__(self, G, p):
        self.player = p
        self.game = G
        self.distributor = Toplevel()
        self.distributor.title("Hegemony")
        Label(self.distributor, text=f"{self.player.name}'s turn").grid(row=0, column=0, padx=2, pady=2)
        self.entries = []
        rowid = 1
        for territory in self.player.territories:
            Label(self.distributor, text=f"{territory}: set as city =>").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(self.distributor)
            e.insert(0, "0")
            e.grid(row=rowid, column=1, padx=2, pady=2)
            self.entries.append(e)
            rowid += 1
        Button(self.distributor,
               text="Update Territory Status",
               command=self.enter_data).grid(row=rowid, columnspan=2, padx=2, pady=2)

class CITY_SETTER:
    def __init__(self, root, game, signal, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Initial City Planning")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal.main_frame)
        # Display Current Status

        Label(self.main_frame, text="Current Status:").grid(row=0, column=0, padx=2, pady=2)
        cid = 0
        for player in self.game.players:
            '''
            status = f"{player.name}:\n"
            for territory in player.territories:
                trty = self.game.world.territories[territory]
                status += f"{territory}: City Status => {trty.isCity}\n"
            Label(self.main_frame, text=status).grid(row=1, column=cid, padx=2, pady=2)
                    '''
            cid += 1
        # Shuffle and display distribution order
        order = [player.name for player in self.game.players]
        order_display = "Distribution Order: "
        for player in order:
            order_display += player + "\t"
        Label(self.main_frame, text=order_display).grid(row=2, columnspan=cid, padx=2, pady=2)

        # Start Distribution
        def c_distribute():
            DIST_BTN['state'] = 'disabled'
            for player in self.game.players:
                distributor = C_DIST_PROMPT(self.game, player)
                self.main_frame.wait_window(distributor.distributor)
            self.main_frame.destroy()

        DIST_BTN = Button(self.main_frame, text="Start Distribution", command=c_distribute)
        DIST_BTN.grid(row=4, columnspan=cid, padx=2, pady=2)

# Troops distribution
class T_DIST_PROMPT:

    def enter_data(self):
        troops = 0
        for e in self.entries:
            change = int(e.get())
            troops += change
        if troops != self.distributable_force:
            Label(self.distributor, text="Wrong amount of troops deployed").grid(row=0, column=1, padx=2, pady=2)
            return
        for i in range(len(self.entries)):
            change = int(self.entries[i].get())
            self.game.world.territories[self.player.territories[i]].troops += change
            self.game.map_visualizer.update_view(self.player.territories[i])
        self.distributor.destroy()

    def __init__(self, G, name):
        self.game = G
        self.name = name
        self.distributor = Toplevel()
        self.distributor.title("Hegemony")
        # Determine rank of a player
        rank = 0
        for player in G.players:
            rank += 1
            if player.name == self.name:
                self.player = player
                break
        # Initial average when the 5 specialized territories are not conquered
        average = m.ceil((len(self.game.world.territories) - 5) / self.game.get_active_player())
        self.distributable_force = average
        if rank > m.ceil(len(G.players) / 2):
            self.distributable_force += 3
        message = f"{name}'s turn, {self.distributable_force} distributable."
        # Update the total troops of the game right away
        self.game.total_troops += self.distributable_force
        Label(self.distributor, text=message).grid(row=0, padx=2, pady=2)
        rowid = 1
        self.entries = []
        for territory in self.player.territories:
            Label(self.distributor, text=f"{territory}: +").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(self.distributor)
            e.insert(0, "0")
            e.grid(row=rowid, column=1, padx=2, pady=2)
            self.entries.append(e)
            rowid += 1
        self.btn = Button(self.distributor, text="Reinforce", command=self.enter_data)
        self.btn.grid(row=rowid + 1, columnspan=2, padx=2, pady=2)

class TROOP_DISTRIBUTOR:

    def __init__(self, root, game, signal, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Initial Reinforcement")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal.main_frame)
        # Display Current Status
        Label(self.main_frame, text="Current Status:").grid(row=0, column=0, padx=2, pady=2)
        cid = 0
        for player in self.game.players:
            '''
            status = f"{player.name}:\n"
            for territory in player.territories:
                trty = self.game.world.territories[territory]
                status += f"{territory}: {trty.troops}\n"
            Label(self.main_frame, text=status).grid(row=1, column=cid, padx=2, pady=2)
                         '''
            cid += 1
        # Last change in order, this will be the attack order.
        order = self.game.shuffle_order()
        order_display = "Distribution Order: "
        for player in order:
            order_display += player + "\t"
        Label(self.main_frame, text=order_display).grid(row=2, columnspan=cid, padx=2, pady=2)

        # Start Distribution
        def t_distribute():
            DIST_BTN['state'] = 'disabled'
            for p in order:
                distributor = T_DIST_PROMPT(self.game, p)
                self.main_frame.wait_window(distributor.distributor)
            self.main_frame.destroy()

        DIST_BTN = Button(self.main_frame, text="Start Distribution", command=t_distribute)
        DIST_BTN.grid(row=3, columnspan=cid, padx=2, pady=2)

class SKILL_DISTRIBUTOR:

    def set_skills(self):
        for e in self.entries:
            if e.get() == "N":
                Label(self.main_frame, text="All players must have skills!").grid(row=self.rowid+1, padx=2, pady=2,
                                                                                  columnspan=2)
                return
            try:
                a = int(e.get())
            except:
                Label(self.main_frame, text="Invalid Input!").grid(row=self.rowid + 1, padx=2, pady=2, columnspan=2)
                return
        for pair in zip(self.entries, self.game.players):
            skill, player = pair[0].get(), pair[1]
            if skill == "1":
                player.hasSkill = True
                player.skill = Sturdy_Defender(player, self.game)
            elif skill == "2":
                player.hasSkill = True
                player.skill = Usurper(player, self.game)
            elif skill == "3":
                player.hasSkill = True
                player.skill = Air_Superiority(player, self.game)
            elif skill == "4":
                player.hasSkill = True
                player.skill = Mass_Mobilization(player, self.game)
            elif skill == "6":
                player.hasSkill = True
                player.skill = Route_Planner(player, self.game)
            elif skill == "7":
                player.hasSkill = True
                player.skill = Divine_Punishment(player, self.game)
            elif skill == "8":
                player.hasSkill = True
                player.skill = Tactical_Blasting(player, self.game)
            elif skill == "10":
                player.hasSkill = True
                player.skill = Industrial_Revolution(player, self.game)
            elif skill == "11":
                player.hasSkill = True
                player.skill = Zealous_Expansion(player, self.game)
            elif skill == "12":
                player.hasSkill = True
                player.skill = Ares_Blessing(player, self.game)
            elif skill == "13":
                player.hasSkill = True
                player.skill = Laplace_Demon(player, self.game)
            elif skill == "18":
                player.hasSkill = True
                player.skill = Necromancer(player, self.game)
            elif skill == "19":
                player.hasSkill = True
                player.skill = Operation_Prometheus(player, self.game)
            elif skill == "20":
                player.hasSkill = True
                player.skill = Handler_of_Wheel_of_Fortune(player, self.game)
            elif skill == "21":
                player.hasSkill = True
                player.skill = Dictator(player, self.game)
        self.main_frame.destroy()

    def __init__(self, root, game, signal, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Skill Distribution")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.main_frame.wait_window(signal.main_frame)
        self.entries = []
        self.rowid = 0
        for player in self.game.players:
            Label(self.main_frame, text=f"{player.name}: ").grid(row=self.rowid, column=0, padx=2, pady=2)
            e = Entry(self.main_frame)
            e.grid(row=self.rowid, column=1, padx=2, pady=2)
            e.insert(0, "N")
            self.entries.append(e)
            self.rowid += 1
        Button(self.main_frame, text="Set skills", command=self.set_skills).grid(row=self.rowid, columnspan=2,
                                                                                 padx=2, pady=2)








