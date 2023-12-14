from game_runner.GUI_helpers import *
from PIL import Image, ImageTk
# GLOBAL STATUS DISPLAY
class World_Status:

    def update_view(self):
        # PACK POLICY
        # Clear the previous content of the show frames
        g = self.global_status_display
        for widget in g.show_frame.pack_slaves():
            widget.destroy()
        # Clear the previous content of the show frames
        p = self.player_status_display
        for widget in p.show_frame.pack_slaves():
            widget.destroy()

        # Update Global Status
        # total troops of active players
        # tracking troop changes is too tiring, we just sum up the total force of active players
        self.game.total_troops = self.game.get_total_troops()
        Label(g.show_frame, text=f"Total troops: {self.game.total_troops}").pack()
        # number of active forces
        Label(g.show_frame, text=f"Number of active forces: {self.game.get_active_player()}").pack()
        # industrialized nations
        ind_ps = self.game.get_industrialized_forces()
        Label(g.show_frame, text=f"Industrialized Nations:").pack()
        tmp_message = ""
        for player in ind_ps:
            tmp_message += player.name + "  "
        Label(g.show_frame, text=tmp_message).pack()
        # average amount of troops per force
        tmp_message = f"Average amount of troops per player: {round(self.game.total_troops/self.game.get_active_player(), 3)}"
        Label(g.show_frame, text=tmp_message).pack()
        # regional powers
        powers = self.game.get_superpowers()
        Label(g.show_frame, text=f"Nation that controls the largest army: {powers[0]}").pack()
        Label(g.show_frame, text=f"Nation that controls the most territory: {powers[1]}").pack()
        Label(g.show_frame, text=f"The most technologically advanced nation: {powers[2]}").pack()
        Label(g.show_frame, text=f"Nation with the best transport system: {powers[3]}").pack()
        Label(g.show_frame, text=f"Superpower: {powers[4]}").pack()
        # [htp, htrtyp, hip, hinfra, superpower]
        # Update Player Status
        self.player_images.clear()
        for player in self.game.players:
            new_img = Image.open(player.insignia)
            new_img = new_img.resize((20, 20))
            new_img = ImageTk.PhotoImage(new_img)
            self.player_images.append(new_img)
            Label(p.show_frame, image=new_img).pack()
            for info in player.get_information_for_WS():
                Label(p.show_frame, text=info).pack()
            Label(p.show_frame, text="").pack()
        for i in range(200):
            Label(p.show_frame, text="").pack()
        return

    def __init__(self, game, root, signal, rowid, cid):

        self.game = game
        self.main_frame = Frame(root)
        self.main_frame.wait_window(signal.main_frame)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)

        self.global_status = LabelFrame(self.main_frame, text="World Status")
        self.global_status.grid(row=0, column=0, padx=2, pady=2)
        self.global_status_display = VSF(self.global_status, 0, 0)

        self.player_status = LabelFrame(self.main_frame, text="Status by player")
        self.player_status.grid(row=1, column=0, padx=2, pady=2)
        self.player_status_display = VSF(self.player_status, 0, 0)
        self.player_images = []
        self.update_view()