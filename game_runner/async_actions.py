from game_runner.GUI_helpers import *
from game_runner.RNG import get_alliance_code
from game_runner.commonwealth_system import *
from PIL import Image, ImageTk
import math as m

# Star Shop
# Reserve Deployment
# Rearrangement
# Skill
# Alliance

class async_menu:

    def __init__(self, G, root, player, rowid, cid):
        self.game = G
        self.player = player
        self.main_frame = Frame(root)
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        # 0, 0
        self.star_shop = star_shop(self.main_frame, G, player, 0, 0)
        # 0, 1
        self.movement_frame = Frame(self.main_frame)
        self.movement_frame.grid(row=0, column=1)
        self.reserve_deployment = reserve_deployer(G, self.movement_frame, player, 0, 1)
        self.direct_transfer = direct_rearrange(G, self.movement_frame, player, 1, 1)
        # 0, 2
        self.alliance_frame = Frame(self.main_frame)
        self.alliance_frame.grid(row=0, column=2)
        if not self.player.hasAllies:
            self.alliance_former = alliance_create(G, self.alliance_frame, player, 0, 0)
        elif len(self.player.allies) < self.game.max_allies - 1:
            self.alliance_former = alliance_create(G, self.alliance_frame, player, 0, 0)
            self.alliance_handle = alliance_handler(G, self.alliance_frame, player, 0, 1)
        else:
            self.alliance_handle = alliance_handler(G, self.alliance_frame, player, 0, 1)
        # 0, 3
        self.skill_handle = skill_handler(G, self.main_frame, player, 0, 3)


class skill_handler:
    def __init__(self, G, root, player, rowid, cid):
        self.game = G
        self.player = player
        self.main_frame = Frame(root)
        self.main_frame.grid(row=rowid, column=cid)
        self.activation_frame = Frame(self.main_frame)
        self.activation_frame.grid(row=0, column=0)
        self.usage_frame = Frame(self.main_frame)
        self.usage_frame.grid(row=0, column=1)
        if self.player.hasSkill:
            self.sync_skill = turn_based_skill_handler(G, self.activation_frame, player, 0, 0, self.usage_frame)
        self.async_skill = off_turn_skill_handler(G, self.activation_frame, 0, 1, self.usage_frame)


# pack
class off_turn_skill_handler:

    def trigger_skill(self, c):
        c.show_effect(self.usage_frame)

    def __init__(self, G, root, rowid, cid, usage_frame):
        self.game = G
        self.main_frame = LabelFrame(root, text="Off-turn skills")
        self.main_frame.grid(row=rowid, column=cid)
        self.usage_frame = usage_frame
        # Problems here
        for player in self.game.players:
            if player.hasSkill:
                curr_skill = player.skill
                if curr_skill.off_turn_usable:
                    Button(self.main_frame, text=player.name,
                           command=lambda c=curr_skill:  self.trigger_skill(c)).pack()

# grid
class turn_based_skill_handler:

    def use_skill(self):
        self.player.skill.show_effect(self.usage_frame)

    def __init__(self, G, root, player, rowid, cid, usage_frame):
        self.game = G
        self.player = player
        self.main_frame = LabelFrame(root, text="Skill Activation")
        self.main_frame.grid(row=rowid, column=cid)
        Button(self.main_frame, text="Use Skill", command=self.use_skill).grid(row=0, column=0)
        self.usage_frame = usage_frame
        return


class alliance_handler:

    # LOGO
    def set_logo(self, path):
        if self.player.ally_socket.CAD_logo is not None:
            Label(self.event_handler, text="Already has a logo!").pack()
            return
        self.player.ally_socket.CAD_logo = path.get()
        self.game.cads_used.append(path.get())
        for widget in self.event_handler.pack_slaves():
            widget.destroy()

    def handle_logo(self):
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        self.images.clear()
        Label(self.event_handler, text="Choose CAD logo:").pack()
        logo_path = StringVar(value=" ")
        frame = Frame(self.event_handler)
        frame.pack()
        rowid = 0
        cid = 0
        for cad in self.game.cads:
            if cad not in self.game.cads_used:
                new_img = Image.open(cad)
                new_img = new_img.resize((20, 20))
                new_img = ImageTk.PhotoImage(new_img)
                self.images.append(new_img)
                Radiobutton(frame, image=new_img, variable=logo_path, value=cad).grid(row=rowid, column=cid)
                cid += 1
                if cid == 4:
                    cid = 0
                    rowid += 1
        Button(self.event_handler, text="Confirm", command=lambda: self.set_logo(logo_path)).pack()

    # NAME
    def change_name(self, e):
        self.player.ally_socket.name = e.get()
        for widget in self.event_handler.pack_slaves():
            widget.destroy()

    def handle_name(self):
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        Label(self.event_handler, text="Enter the name of the alliance:").pack()
        ER = Entry(self.event_handler)
        ER.pack()
        Button(self.event_handler, text="Confirm", command=lambda: self.change_name(ER)).pack()

    # CAD
    def create_new_CAD(self, ER):
        result = self.player.ally_socket.create_CAD(self.player, ER.get())
        if not result[0]:
            if result[1] == "NE":
                Label(self.event_handler, text="Player does not own such territory!").pack()
                return
            if result[1] == "NOCAD":
                Label(self.event_handler, text="Maximum amount of CAD built!").pack()
                return
            if result[1] == "ALDCAD":
                Label(self.event_handler, text="Already a CAD!").pack()
                return
            if result[1] == "NRT":
                Label(self.event_handler, text="Not the right time!").pack()
                return
            if result[1] == "NCL":
                Label(self.event_handler, text="Choose a CAD logo first!").pack()
                return
        for widget in self.event_handler.pack_slaves():
            widget.destroy()

    def handle_CAD_creation(self):
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        Label(self.event_handler, text="Enter the name of the new CAD:").pack()
        ER = Entry(self.event_handler)
        ER.pack()
        Button(self.event_handler, text="Confirm", command=lambda: self.create_new_CAD(ER)).pack()

    # S
    def transfer_stars(self, ER):
        result = self.player.ally_socket.transfer_stars(self.player, int(ER.get()))
        if not result[0]:
            Label(self.event_handler, text="Invalid Amount!").pack()
            return
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        self.game.world_status.update_view()

    def handle_authority(self):
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        message = f"{self.player.ally_socket.get_retrievable_stars(self.player)}"
        Label(self.event_handler, text=message + " stars available from allies, ask for:").pack()
        ER = Entry(self.event_handler)
        ER.pack()
        Button(self.event_handler, text="Confirm", command=lambda: self.transfer_stars(ER)).pack()

    # R
    def transfer_troops(self, ER):
        result = self.player.ally_socket.transfer_reserves(self.player, int(ER.get()))
        if not result[0]:
            Label(self.event_handler, text="Invalid Amount!").pack()
            return
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        self.game.world_status.update_view()

    def handle_reinforcement(self):
        for widget in self.event_handler.pack_slaves():
            widget.destroy()
        message = f"{self.player.ally_socket.get_retrievable_reserves(self.player)}"
        Label(self.event_handler, text=message + " troops available from allies' reserves, ask for:").pack()
        ER = Entry(self.event_handler)
        ER.pack()
        Button(self.event_handler, text="Confirm", command=lambda: self.transfer_troops(ER)).pack()

    def __init__(self, G, root, player, rowid, cid):

        self.game = G
        self.player = player
        self.images = []
        self.main_frame = LabelFrame(root, text=f"Commonwealth Actions")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.select_menu = Frame(self.main_frame)
        self.select_menu.grid(row=0, column=0)
        self.event_handler = Frame(self.main_frame)
        self.event_handler.grid(row=0, column=1)
        Button(self.select_menu, text="Ask for reinforcement", command=self.handle_reinforcement).pack()
        Button(self.select_menu, text="Ask for special authority", command=self.handle_authority).pack()
        Button(self.select_menu, text="Form new CAD", command=self.handle_CAD_creation).pack()
        if self.player.ally_socket.name is None:
            Button(self.select_menu, text="Name Alliance", command=self.handle_name).pack()
        if self.player.ally_socket.CAD_logo is None:
            Button(self.select_menu, text="Choose CAD logo", command=self.handle_logo).pack()


class alliance_create:

    def form_alliance(self, EA, code, playerwanted):
        c_code = EA.get()
        if c_code != code:
            Label(self.create_frame, text=f"Wrong confirmation code!").pack()
            return
        for widget in self.create_frame.pack_slaves():
            widget.destroy()

        # both player doesn't have alliance
        if not self.player.hasAllies and not playerwanted.hasAllies:
            New_alliance = Alliance(self.player, playerwanted, self.game)
        elif self.player.hasAllies:
            self.player.ally_socket.add_member(playerwanted)
        else:
            playerwanted.ally_socket.add_member(self.player)
        for widget in self.create_frame.pack_slaves():
            widget.destroy()
        self.game.world_status.update_view()
        alliance_handle = alliance_handler(self.game, self.root, self.player, 0, 1)

    def create_alliance(self, e):
        playername = e.get()
        playerwanted = None
        for player in self.game.players:
            if player.name == playername:
                playerwanted = player
        if playerwanted is None:
            Label(self.create_frame, text="Player does not exist!").pack()
            return
        for widget in self.create_frame.pack_slaves():
            widget.destroy()
        # Verify if player is a dictator
        if playerwanted.hasSkill:
            if playerwanted.skill.name == "Dictator":
                Label(self.create_frame, text="Player already in an alliance!").pack()
                return
        if self.player.hasSkill:
            if self.player.skill.name == "Dictator":
                Label(self.create_frame, text="Cannot form alliance!").pack()
                return
        # Verify if player is yourself
        if playername == self.player.name:
            Label(self.create_frame, text="Cannot be ally with yourself!").pack()
            return
        # If already has allies
        if self.player.hasAllies:
            if playerwanted.hasAllies:
                Label(self.create_frame, text="Player already in an alliance!").pack()
                return
            elif len(self.player.allies) + 1 == self.game.max_allies:
                Label(self.create_frame, text="Alliance full!").pack()
                return
        if playerwanted.hasAllies:
            if len(playerwanted.allies) + 1 == self.game.max_allies:
                Label(self.create_frame, text="Alliance full!").pack()
                return
        code = get_alliance_code()
        Label(self.create_frame, text=f"Enter the confirmation code: {code}").pack()
        EA = Entry(self.create_frame)
        EA.pack()
        Button(self.create_frame, text=f"Confirm", command=lambda: self.form_alliance(EA, code, playerwanted)).pack()

    def __init__(self, G, root, player, rowid, cid):
        self.game = G
        self.player = player
        self.root = root
        self.main_frame = LabelFrame(root, text=f"Form Alliance")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        self.prompt_frame = Frame(self.main_frame)
        self.prompt_frame.grid(row=0, column=0, padx=1, pady=1)
        self.create_frame = Frame(self.main_frame)
        self.create_frame.grid(row=0, column=1, padx=1, pady=1)
        Label(self.prompt_frame, text="Form alliance with:").pack()
        e = Entry(self.prompt_frame)
        e.pack()
        Button(self.prompt_frame, text="Confirm", command=lambda: self.create_alliance(e)).pack()
        return


# changed into universal transfer
class direct_rearrange:

    def transfer(self, e1, e2, e3):
        departure = e1.get()
        destination = e2.get()
        amount = int(e3.get())
        DEPART = self.game.world.territories[departure]
        owner = DEPART.owner
        if departure not in owner.territories or destination not in owner.territories:
            Label(self.transfer_prompt, text="Destination not available!").grid(row=3)
            return
        if destination not in owner.game.world.get_connected_regions(owner, departure, [], [], owner.allies):
            Label(self.transfer_prompt, text="Territories Disconnected!").grid(row=3)
            return
        if amount >= self.game.world.territories[departure].troops:
            Label(self.transfer_prompt, text="Invalid Amount of Troops!").grid(row=3)
            return
        self.game.world.territories[departure].troops -= amount
        if destination not in self.game.world.get_safely_connected_regions(owner, departure, [], [], owner.allies):
            amount = m.floor(0.6*amount)
        self.game.world.territories[destination].troops += amount
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        self.game.map_visualizer.update_view(departure)
        self.game.map_visualizer.update_view(destination)
        for widget in self.transfer_prompt.grid_slaves():
            widget.destroy()

    def show_prompt(self):
        for widget in self.transfer_prompt.grid_slaves():
            widget.destroy()
        Label(self.transfer_prompt, text=f"From: ").grid(row=0, column=0)
        e1 = Entry(self.transfer_prompt)
        e1.grid(row=0, column=1)
        Label(self.transfer_prompt, text=f"To: ").grid(row=0, column=2)
        e2 = Entry(self.transfer_prompt)
        e2.grid(row=0, column=3)
        Label(self.transfer_prompt, text=f"Amount: ").grid(row=1, column=0)
        e3 = Entry(self.transfer_prompt)
        e3.grid(row=1, column=1)
        Button(self.transfer_prompt, text="Confirm", command=lambda: self.transfer(e1, e2, e3)).grid(row=2)

    def __init__(self, G, root, player, rowid, cid):
        self.game = G
        self.player = player
        self.main_frame = LabelFrame(root, text="Troop Transfer")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        Button(self.main_frame, text="Transfer Troops", command=self.show_prompt).grid(row=0, column=0, padx=2, pady=2)
        self.transfer_prompt = Frame(self.main_frame)
        self.transfer_prompt.grid(row=0, column=1)


class reserve_deployer:

    def deploy(self, entries, TL):
        amounts = []
        for e in entries:
            amounts.append(int(e.get()))
        if sum(amounts) > self.player.reserves:
            Label(TL, text="Invalid amount of reserves entered!").grid(row=3, column=0)
            return
        for i in range(len(entries)):
            self.game.world.territories[self.player.territories[i]].troops += amounts[i]
            # update view on map
            self.game.map_visualizer.update_view(self.player.territories[i])
            self.player.reserves -= amounts[i]
        if self.game.stage == 1:
            self.game.curr_reinforcer.update_info()
        # Update Views
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()
        TL.destroy()

    def deployment(self):
        TL = LabelFrame(self.game.global_root, text="Emergency Deployment")
        TL.grid(row=0, column=0)
        Label(TL, text=f"{self.player.reserves} available:").grid(row=0, column=0)
        options = VSF(TL, 1, 0)
        entries = []
        rowid = 0
        for territory in self.player.territories:
            Label(options.show_frame, text=f"{territory}: +").grid(row=rowid, column=0, padx=2, pady=2)
            e = Entry(options.show_frame)
            e.grid(row=rowid, column=1, padx=2, pady=2)
            e.insert(0, "0")
            entries.append(e)
            rowid += 1
        Button(TL, text="Deploy troops", command=lambda: self.deploy(entries, TL)).grid(row=2, column=0)

    def __init__(self, G, root, player, rowid, cid):
        self.game = G
        self.player = player
        self.main_frame = LabelFrame(root, text="Reserve Deployment")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2)
        Button(self.main_frame, text="Deploy Reserves", command=self.deployment).grid(row=0, column=0, padx=2, pady=2)


class star_shop:

    # Infrastructure upgrade
    def infra_upgraded(self, e):
        amount = int(e.get())
        if amount * 4 > self.player.stars or amount <= 0:
            Label(self.select_frame, text=f"Invalid Amount!").pack()
            return
        if self.game.stage == 2:
            Label(self.select_frame, text=f"Not the right timing!").pack()
            return
        for i in range(amount):
            self.player.stars -= 4
            self.player.upgrade_infrastructure(1)
        self.player.update_infrastructure()
        self.game.world_status.update_view()
        for widget in self.select_frame.pack_slaves():
            widget.destroy()

    def upgrade_infra(self):
        for widget in self.select_frame.pack_slaves():
            widget.destroy()
        Label(self.select_frame, text="4 stars required to level up infrastructure by 1").pack()
        Label(self.select_frame, text=f"{self.player.stars} available, enter how many levels to upgrade:").pack()
        e = Entry(self.select_frame)
        e.pack()
        Button(self.select_frame, text="Upgrade", command=lambda: self.infra_upgraded(e)).pack()

    # City planning
    def construct(self, entries):
        terri = []
        for e in entries:
            terri.append(e.get())
        for widget in self.select_frame.pack_slaves():
            widget.destroy()
        for trtyA in terri:
            for trtyB in self.player.territories:
                if trtyA == trtyB:
                    if self.game.world.territories[trtyA].isCity:
                        continue
                    if self.game.world.territories[trtyA].isMegacity:
                        continue
                    if self.game.world.territories[trtyA].isTransportcenter:
                        continue
                    self.game.world.territories[trtyA].isCity = True
                    self.player.stars -= 3
                    self.game.map_visualizer.update_view(trtyA)
                    if self.game.world.territories[trtyA].isCAD:
                        if self.player in self.game.world.territories[trtyA].mem_stats:
                            for ally in self.player.allies:
                                ally.update_industrial_level()
        # Update Views
        self.player.update_industrial_level()
        self.game.world_status.update_view()
        self.game.public_billboard.update_view()

    def set_city(self, e):
        amount = int(e.get())
        for widget in self.select_frame.pack_slaves():
            widget.destroy()
        if amount * 3 > self.player.stars or amount <= 0:
            Label(self.select_frame, text="Invalid Amount!").pack()
            return
        if self.game.stage != 2:
            entries = []
            for i in range(amount):
                Label(self.select_frame, text=f"City {i + 1} in: ").pack()
                e = Entry(self.select_frame)
                e.pack()
                entries.append(e)
            Button(self.select_frame, text="Construct", command=lambda: self.construct(entries)).pack()
        else:
            Label(self.select_frame, text="Not the right timing!").pack()

    def build_cities(self):
        for widget in self.select_frame.pack_slaves():
            widget.destroy()
        Label(self.select_frame, text=f"Cost: 3 stars per city").pack()
        Label(self.select_frame, text=f"{self.player.stars} stars available, enter how many cities to build: ").pack()
        e = Entry(self.select_frame)
        e.pack()
        Button(self.select_frame, text="Construct", command=lambda: self.set_city(e)).pack()

    # Troop conversion
    def convert_stars_for_troops(self, e):
        amount = int(e.get())
        if amount <= 1 or amount > self.player.stars or amount > 15:
            Label(self.select_frame, text="Invalid amount of stars used!").pack()
            return
        self.player.stars -= amount
        self.player.reserves += self.conversion_rate[amount]
        self.game.world_status.update_view()
        if self.game.stage == 1:
            self.game.curr_reinforcer.update_info()
        for widget in self.select_frame.pack_slaves():
            widget.destroy()

    def troop_convert(self, ):
        for widget in self.select_frame.pack_slaves():
            widget.destroy()
        Label(self.select_frame, text=f"{self.player.stars} stars available, use:").pack()
        e = Entry(self.select_frame)
        e.pack()
        Button(self.select_frame, text="Convert", command=lambda: self.convert_stars_for_troops(e)).pack()

    def __init__(self, root, G, player, rowid, cid):

        self.conversion_rate = {
            2: 3,
            3: 4,
            4: 7,
            5: 10,
            6: 13,
            7: 17,
            8: 21,
            9: 25,
            10: 30,
            11: 34,
            12: 39,
            13: 46,
            14: 53,
            15: 60
        }

        self.game = G
        self.player = player
        # MAIN_FRAME
        self.main_frame = LabelFrame(root, text="Special Execution")
        self.main_frame.grid(row=rowid, column=cid, padx=2, pady=2, rowspan=2)
        # MENU_FRAME
        self.menu_frame = Frame(self.main_frame)
        self.menu_frame.grid(row=0, column=0, padx=2, pady=2)
        # SELECTION_FRAME
        self.select_frame = Frame(self.main_frame)
        self.select_frame.grid(row=0, column=1, padx=2, pady=2)
        # INSIDE MENU:
        # troop conversion
        Button(self.menu_frame, text="Exchange troops", command=self.troop_convert).grid(row=0, column=0,
                                                                                         padx=2, pady=2)
        # city planning
        Button(self.menu_frame, text="Build cities", command=self.build_cities).grid(row=1, column=0,
                                                                                     padx=2, pady=2)
        # infrastructure upgrade
        Button(self.menu_frame, text="Improve Infrastructure", command=self.upgrade_infra).grid(row=2, column=0,
                                                                                                padx=2, pady=2)
