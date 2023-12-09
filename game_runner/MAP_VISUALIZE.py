from tkinter import *
from PIL import Image, ImageTk

class map_canvas:

    def __init__(self, root, game):
        self.game = game

        # dimension (temp solution)
        self.scaling = 1
        # self.scaling = 1.63
        # set map version here
        new_img = Image.open("visual_assets/MAP/mapc.png")
        # new_img = new_img.resize((int(2550 // 1.63),
        #                            int(1400 // 1.81)))
        new_img = ImageTk.PhotoImage(new_img)
        self.Map = new_img

        # self.Map = PhotoImage(file="visual_assets/MAP/mapc.png")

        self.canvas = Canvas(root, width=int(2550//self.scaling), height=int(1400//self.scaling))

        # self.canvas = Canvas(root, width=2550, height=1400)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.Map, anchor='nw')
        self.industrial_logo = "visual_assets/LOGOS/city.png"
        self.territories_to_display = {}
        for territory in self.game.world.territories:
            self.territories_to_display[territory] = territorial_display(game.world.territories[territory])

    def update_all_view(self):
        for display in self.territories_to_display:
            img_s = self.territories_to_display[display]
            trty = img_s.trty
            owner = trty.owner

            if trty.destroyed:
                new_img = Image.open("visual_assets/RADIOACTIVE/radioactive.PNG")
                new_img = new_img.resize((int(img_s.trty.radio_dims[0]//self.scaling),
                                          int(img_s.trty.radio_dims[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_ra = new_img
                new_img = self.canvas.create_image(int(img_s.trty.radio_pos[0]//self.scaling),
                                                   int(img_s.trty.radio_pos[1]//self.scaling),
                                                   image=img_s.curr_ra, anchor='nw')
                img_s.curr_ra_id = new_img
                continue

            if owner is None:
                if trty.civil_war:
                    new_img = Image.open("visual_assets/CIVIL_WAR/cw.PNG")
                    new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                              int(img_s.trty.insig_dim[1]//self.scaling)))
                    new_img = ImageTk.PhotoImage(new_img)
                    img_s.curr_insig = new_img
                    new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                       int(img_s.trty.insig_pos[1]//self.scaling),
                                                       image=img_s.curr_insig, anchor='nw')
                    img_s.curr_insig_id = new_img
                else:
                    new_img = Image.open("visual_assets/INSIGNIAS/neutral.PNG")
                    new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                              int(img_s.trty.insig_dim[1]//self.scaling)))
                    new_img = ImageTk.PhotoImage(new_img)
                    img_s.curr_insig = new_img
                    new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                       int(img_s.trty.insig_pos[1]//self.scaling),
                                                       image=img_s.curr_insig, anchor='nw')
                    img_s.curr_insig_id = new_img
            elif trty.isCAD and owner in trty.mem_stats:
                new_img = Image.open(owner.ally_socket.CAD_logo)
                new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                          int(img_s.trty.insig_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_insig = new_img
                new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                   int(img_s.trty.insig_pos[1]//self.scaling),
                                                   image=img_s.curr_insig, anchor='nw')
                img_s.curr_insig_id = new_img
            else:
                new_img = Image.open(owner.insignia)
                new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                          int(img_s.trty.insig_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_insig = new_img
                new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                   int(img_s.trty.insig_pos[1]//self.scaling),
                                                   image=img_s.curr_insig, anchor='nw')
                img_s.curr_insig_id = new_img

            if trty.isCapital and trty.owner is not None:
                new_img = Image.open(owner.capital_icon)
                new_img = new_img.resize((int(img_s.trty.cap_dim[0]//self.scaling),
                                          int(img_s.trty.cap_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_cap = new_img
                new_img = self.canvas.create_image(int(img_s.trty.cap_pos[0]//self.scaling),
                                                   int(img_s.trty.cap_pos[1]//self.scaling),
                                                   image=img_s.curr_cap, anchor='nw')
                img_s.curr_cap_id = new_img

            if trty.isCity:
                new_img = Image.open("visual_assets/LOGOS/city.png")
                new_img = new_img.resize((int(img_s.trty.city_dim[0]//self.scaling),
                                          int(img_s.trty.city_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_city = new_img
                new_img = self.canvas.create_image(int(img_s.trty.city_pos[0]//self.scaling),
                                                   int(img_s.trty.city_pos[1]//self.scaling),
                                                   image=img_s.curr_city, anchor='nw')
                img_s.curr_city_id = new_img
            self.canvas.delete(img_s.curr_troops)
            img_s.curr_troops = self.canvas.create_text(int(trty.text_pos[0]//self.scaling),
                                                       int(trty.text_pos[1]//self.scaling),
                                                       text=f"{trty.troops}",
                                                        # tmp_font
                                                        font=("Helvetica",
                                                              int(trty.text_font//self.scaling)+2))
                                                              # int(trty.text_font // self.scaling)))

    # pass in name
    def update_view(self, territory):
        img_s = self.territories_to_display[territory]
        trty = img_s.trty
        owner = trty.owner

        if owner is None:
            if trty.civil_war:
                new_img = Image.open("visual_assets/CIVIL_WAR/cw.PNG")
                new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                          int(img_s.trty.insig_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_insig = new_img
                new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                   int(img_s.trty.insig_pos[1]//self.scaling),
                                                   image=img_s.curr_insig, anchor='nw')
                img_s.curr_insig_id = new_img
            else:
                new_img = Image.open("visual_assets/INSIGNIAS/neutral.PNG")
                new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                          int(img_s.trty.insig_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_insig = new_img
                new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                   int(img_s.trty.insig_pos[1]//self.scaling),
                                                   image=img_s.curr_insig, anchor='nw')
                img_s.curr_insig_id = new_img
        elif trty.isCAD and owner in trty.mem_stats:
            new_img = Image.open(owner.ally_socket.CAD_logo)
            new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                      int(img_s.trty.insig_dim[1]//self.scaling)))
            new_img = ImageTk.PhotoImage(new_img)
            img_s.curr_insig = new_img
            new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                               int(img_s.trty.insig_pos[1]//self.scaling),
                                               image=img_s.curr_insig, anchor='nw')
            img_s.curr_insig_id = new_img
        else:
            new_img = Image.open(owner.insignia)
            new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                      int(img_s.trty.insig_dim[1]//self.scaling)))
            new_img = ImageTk.PhotoImage(new_img)
            img_s.curr_insig = new_img
            new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                               int(img_s.trty.insig_pos[1]//self.scaling),
                                               image=img_s.curr_insig, anchor='nw')
            img_s.curr_insig_id = new_img

        if trty.isCapital:
            new_img = Image.open(owner.capital_icon)
            new_img = new_img.resize((int(img_s.trty.cap_dim[0]//self.scaling),
                                      int(img_s.trty.cap_dim[1]//self.scaling)))
            new_img = ImageTk.PhotoImage(new_img)
            img_s.curr_cap = new_img
            new_img = self.canvas.create_image(int(img_s.trty.cap_pos[0]//self.scaling),
                                               int(img_s.trty.cap_pos[1]//self.scaling),
                                               image=img_s.curr_cap, anchor='nw')
            img_s.curr_cap_id = new_img

        if trty.isCity:
            new_img = Image.open("visual_assets/LOGOS/city.png")
            new_img = new_img.resize((int(img_s.trty.city_dim[0]//self.scaling),
                                      int(img_s.trty.city_dim[1]//self.scaling)))
            new_img = ImageTk.PhotoImage(new_img)
            img_s.curr_city = new_img
            new_img = self.canvas.create_image(int(img_s.trty.city_pos[0]//self.scaling),
                                               int(img_s.trty.city_pos[1]//self.scaling),
                                               image=img_s.curr_city, anchor='nw')
            img_s.curr_city_id = new_img
        if not trty.isCity and img_s.curr_city is not None:
            img_s.curr_city = None
            img_s.curr_city_id = None

        self.canvas.delete(img_s.curr_troops)
        img_s.curr_troops = self.canvas.create_text(int(trty.text_pos[0]//self.scaling),
                                                    int(trty.text_pos[1]//self.scaling),
                                                    text=f"{trty.troops}",
                                                    font=("Helvetica",
                                                          # tmp_font
                                                          int(trty.text_font // self.scaling) + 2))
                                                          # int(trty.text_font//self.scaling)))

    def update_destroyed_view(self, name):
        img_s = self.territories_to_display[name]
        img_s.curr_insig = None
        img_s.curr_insig_id = None
        img_s.curr_cap = None
        img_s.curr_cap_id = None
        img_s.curr_city = None
        img_s.curr_city_id = None
        self.canvas.delete(img_s.curr_troops)
        new_img = Image.open("visual_assets/RADIOACTIVE/radioactive.PNG")
        new_img = new_img.resize((int(img_s.trty.radio_dims[0]//self.scaling),
                                  int(img_s.trty.radio_dims[1]//self.scaling)))
        new_img = ImageTk.PhotoImage(new_img)
        img_s.curr_ra = new_img
        new_img = self.canvas.create_image(int(img_s.trty.radio_pos[0]//self.scaling),
                                           int(img_s.trty.radio_pos[1]//self.scaling),
                                           image=img_s.curr_ra, anchor='nw')
        img_s.curr_ra_id = new_img

    def distribution_view(self, forces):

        l = len(forces)
        tmp_insig = self.game.get_random_insig(l)
        i = 0
        for fid in forces:
            for name in forces[fid]:
                img_s = self.territories_to_display[name]
                new_img = Image.open(tmp_insig[i])
                new_img = new_img.resize((int(img_s.trty.insig_dim[0]//self.scaling),
                                          int(img_s.trty.insig_dim[1]//self.scaling)))
                new_img = ImageTk.PhotoImage(new_img)
                img_s.curr_insig = new_img
                new_img = self.canvas.create_image(int(img_s.trty.insig_pos[0]//self.scaling),
                                                   int(img_s.trty.insig_pos[1]//self.scaling),
                                                   image=img_s.curr_insig, anchor='nw')
                img_s.curr_insig_id = new_img
            i += 1

class territorial_display:

    def __init__(self, territory):
        self.trty = territory
        self.curr_insig = None
        self.curr_insig_id = None
        self.curr_cap = None
        self.curr_cap_id = None
        self.curr_city = None
        self.curr_city_id = None
        self.curr_troops = None
        self.curr_ra = None
        self.curr_ra_id = None