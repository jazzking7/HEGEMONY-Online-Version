from game_runner.GUI_helpers import *
from PIL import ImageTk, Image
class Public_Billboard:

    def update_view(self):

        for widget in self.global_status.pack_slaves():
            widget.destroy()
        for widget in self.player_info.show_frame.grid_slaves():
            widget.destroy()
        self.images.clear()

        # Global Status:
        Label(self.global_status, text=f"总兵力：{self.game.get_total_troops()}", font=self.label_format).pack()
        Label(self.global_status, text=f"活跃势力：{self.game.get_active_player()}", font=self.label_format).pack()
        Label(self.global_status, text=f"平均兵力: {round(self.game.total_troops/self.game.get_active_player(),3)}"
              , font=self.label_format).pack()
        Label(self.global_status, text=f"进攻顺序:", font=self.label_format).pack()
        message = ""
        for player in self.game.players:
            if player.alive:
                message += player.name+"  "
        Label(self.global_status, text=message, font=self.label_format).pack()
        Label(self.global_status, text="工业化势力：", font=self.label_format).pack()
        ind_ps = self.game.get_industrialized_forces_map()
        tmp_message = ""
        for player in ind_ps:
            tmp_message += player.name + "  "
        Label(self.global_status, text=tmp_message, font=self.label_format).pack()
        powers = self.game.get_superpowers()
        Label(self.global_status, text=f"兵力最多: {powers[0]}", font=self.label_format).pack()
        Label(self.global_status, text=f"领土最多: {powers[1]}", font=self.label_format).pack()
        Label(self.global_status, text=f"第{self.game.round}轮", font=self.label_format).pack()
        new_img = Image.open(self.game.players[self.game.turn].insignia)
        new_img = new_img.resize((20, 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.images.append(new_img)
        Label(self.global_status, text=f"目前轮到:", font=self.label_format).pack()
        Label(self.global_status, image=new_img).pack()
        # Player Status
        sf = self.player_info.show_frame
        rowid = 0
        for player in self.game.players:
            new_img = Image.open(player.insignia)
            new_img = new_img.resize((20, 20))
            new_img = ImageTk.PhotoImage(new_img)
            self.images.append(new_img)
            Label(sf, image=new_img).grid(row=rowid, column=0, padx=2)
            Label(sf, text=f"{player.name}", font=self.label_format).grid(row=rowid, column=1, padx=2)
            rowid += 1
            Label(sf, text=f"状态：{'活跃' if player.alive else '灭亡'}",
                  font=self.label_format).grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
            Label(sf, text=f"兵力：{player.get_total_force()}",
                  font=self.label_format).grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
            Label(sf, text=f"领土数量：{len(player.territories)}",
                  font=self.label_format).grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
        # buffer
        for i in range(100):
            Label(sf, text="").grid(row=rowid)
            rowid += 1
        """
        # Need new function to switch between english and chinese
        # Global Status:
        Label(self.global_status, text=f"Total Troops：{self.game.get_total_troops()}").pack()
        Label(self.global_status, text=f"Number of active forces：{self.game.get_active_player()}").pack()
        Label(self.global_status, text=f"Average troops per player: 
        {round(self.game.total_troops/self.game.get_active_player(),3)}").pack()
        Label(self.global_status, text=f"Attack order:").pack()
        message = ""
        for player in self.game.players:
            if player.alive:
                message += player.name+"  "
        Label(self.global_status, text=message).pack()
        Label(self.global_status, text="Industrialized forces：").pack()
        ind_ps = self.game.get_industrialized_forces()
        tmp_message = ""
        for player in ind_ps:
            tmp_message += player.name + "  "
        Label(self.global_status, text=tmp_message).pack()
        powers = self.game.get_superpowers()
        Label(self.global_status, text=f"Largest army: {powers[0]}").pack()
        Label(self.global_status, text=f"Most territories owned: {powers[1]}").pack()
        # Player Status
        sf = self.player_info.show_frame
        rowid = 0
        for player in self.game.players:
            new_img = Image.open(player.insignia)
            new_img = new_img.resize((20, 20))
            new_img = ImageTk.PhotoImage(new_img)
            self.images.append(new_img)
            Label(sf, image=new_img).grid(row=rowid, column=0, padx=2)
            Label(sf, text=f"{player.name}").grid(row=rowid, column=1, padx=2)
            rowid += 1
            Label(sf, text=f"Status：{'Alive' if player.alive else 'Eliminated'}").grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
            Label(sf, text=f"Army size：{player.get_total_force()}").grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
            Label(sf, text=f"Amount of territories controlled：{len(player.territories)}").grid(row=rowid, columnspan=2, padx=2)
            rowid += 1
        """

    def __init__(self, G):
        self.game = G
        self.game.public_billboard = self
        self.images = []

        self.main_frame = Toplevel()
        self.label_format = ("Helvetica", 15)

        self.global_status = LabelFrame(self.main_frame, text="全球状况")
        self.global_status.grid(row=0, column=0, padx=2)

        self.player_status = LabelFrame(self.main_frame, text="玩家状况")
        self.player_status.grid(row=0, column=1, padx=2)
        self.player_info = VSFL(self.player_status, 0, 0)

        self.update_view()
        """
        self.global_status = LabelFrame(self.main_frame, text="Global Status")
        self.global_status.pack()

        self.player_status = LabelFrame(self.main_frame, text="Player Status")
        self.player_status.pack()
        """