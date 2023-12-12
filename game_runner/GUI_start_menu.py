# Author: Jasper Wang      Date: 19/10/2022     Goal: Start Menu and preload game option
from game_runner.GUI_helpers import *
from PIL import Image, ImageTk
# Name prompt for register player's name at game start
class name_prompt:

    def enter_data(self):
        name = self.name_e.get()
        insig, cap = self.INSIGNIA.get(), self.CAPITAL.get()
        if insig == " " or cap == " ":
            Label(self.main_frame, text="Incomplete selection!").grid(row=3, padx=2, pady=2)
        if insig in self.game.insignias_used or cap in self.game.capitals_used:
            Label(self.main_frame, text="Duplicate selection!").grid(row=3, padx=2, pady=2)
            return
        self.game.add_player(name, insig, cap)
        self.main_frame.destroy()

    def __init__(self, PID, G, root):
        self.game = G
        self.main_frame = Frame(root)
        self.main_frame.pack()
        self.imgs = []
        Label(self.main_frame, text=f"Enter player {PID}'s name: ").grid(row=0, column=0, padx=2, pady=2)

        self.name_e = Entry(self.main_frame)
        self.name_e.grid(row=0, column=1, padx=2, pady=2)

        self.INSIGNIA = StringVar(value=" ")
        self.CAPITAL = StringVar(value=" ")

        self.insignia_selection = LabelFrame(self.main_frame)
        self.insignia_selection.grid(row=1, column=0, padx=2, pady=2)
        rowid, cid = 0, 0
        for insig_path in self.game.insignias:
            img = Image.open(insig_path)
            img = img.resize((30, 30))
            img = ImageTk.PhotoImage(img)
            self.imgs.append(img)
            Radiobutton(self.insignia_selection, variable=self.INSIGNIA, value=insig_path, image=img).grid(row=rowid,
                                                                                                           column=cid)
            cid += 1
            if cid == 4:
                cid = 0
                rowid += 1

        self.capital_selection = LabelFrame(self.main_frame)
        self.capital_selection.grid(row=1, column=1, padx=2, pady=2)
        rowid, cid = 0, 0
        for cap_path in self.game.capitals:
            img = Image.open(cap_path)
            img = img.resize((30, 30))
            img = ImageTk.PhotoImage(img)
            self.imgs.append(img)
            Radiobutton(self.capital_selection, variable=self.CAPITAL, value=cap_path, image=img).grid(row=rowid,
                                                                                                       column=cid)
            cid += 1
            if cid == 4:
                cid = 0
                rowid += 1
        self.btn = Button(self.main_frame, text="Continue", command=self.enter_data)
        self.btn.grid(row=2, columnspan=2, padx=2, pady=2)

class Start_Menu:

    def __init__(self, root, game, rowid, cid):
        self.game = game
        self.main_frame = LabelFrame(root, text="Start Menu")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.selection_frame = Frame(root)
        self.selection_frame.grid(row=1, padx=2, pady=1)

        Label(self.main_frame, text="Enter the number of players: ").grid(row=0, column=0, padx=2, pady=2)
        num_of_players_entry = Entry(self.main_frame)
        num_of_players_entry.grid(row=0, column=1, padx=2, pady=2)

        OPTIONS = IntVar()
        OPTIONS.set(0)
        Radiobutton(self.main_frame, text="Randomized Game", variable=OPTIONS, value=0).grid(row=1)
        Radiobutton(self.main_frame, text="Load Pre-Set Game", variable=OPTIONS, value=1).grid(row=2)

        def start_game():
            START_BTN['state'] = 'disabled'
            self.game.preload = OPTIONS.get()
            num_p = int(num_of_players_entry.get())
            num_of_players_entry.delete(0, END)

            for i in range(1, num_p + 1):
                n_p = name_prompt(i, self.game, self.selection_frame)
                self.main_frame.wait_window(n_p.main_frame)

            # For alliance size limit
            if 7 < num_p < 12:
                self.game.max_allies = 3
            elif 11 < num_p < 15:
                self.game.max_allies = 4
            else:
                self.game.max_allies = 5

            # Signals the next frame to enter
            self.main_frame.destroy()

        START_BTN = Button(self.main_frame, text="Start Game", command=start_game)
        START_BTN.grid(row=3, columnspan=2, padx=2, pady=2)