# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
from game_runner.GUI_game_loop import *
from game_runner.async_actions import *
from game_runner.GUI_start_menu import *
from game_runner.MAP_VISUALIZE import *
from game_runner.game_status_display import *
from game_runner.public_billboard import *
from datetime import date

# Initialize game
G = Game()
# Initialize window
root = Tk()
root.title("Hegemony")
# Initialize live map
LIVE_MAP = Toplevel()
LIVE_MAP.title("HEGEMONY")

# Temporary Solution
#scaling = 1.63
scaling = 1
dims = str(int(2550 // scaling)) + "x" + str(int(1440 // scaling))
LIVE_MAP.geometry(dims)

# LIVE_MAP.geometry('2550x1400')
Visualizer = map_canvas(LIVE_MAP, G)
G.map_visualizer = Visualizer
# ==================================================START MENU==========================================================
# 0,0
Start_Interface = Start_Menu(root, G, 0, 0)
# ============================================TERRITORY DISTRIBUTION====================================================
Trty_Distributor = TRTY_DISTRIBUTOR(root, G, Start_Interface, 0, 0)
# ================================================CAPITAl SETTING=======================================================
# 0,0
Capital_Setter = CAPITAL_SETTER(root, G, Trty_Distributor, 0, 0)
# ============================================INITIAL CITY PLANNING=====================================================
# 0,0
City_Setter = CITY_SETTER(root, G, Capital_Setter, 0, 0)
# ==========================================INITIAL TROOP DISTRIBUTION==================================================
# 0,0
Troop_Distributor = TROOP_DISTRIBUTOR(root, G, City_Setter, 0, 0)
# ==============================================PLAYER CHOOSE SKILL=====================================================
# 0,0
Skill_Distributor = SKILL_DISTRIBUTOR(root, G, Troop_Distributor, 0, 0)
# =============================================GAME STEP UP COMPLETED===================================================

# ================================================GAME LOOP=============================================================
Visualizer.update_all_view()
G.global_root = root
# Global Status Report
# 0,0
WS = World_Status(G, root, Skill_Distributor, 0, 0)
G.world_status = WS
PB = Public_Billboard(G)
# Frame For Game Loop
# 0,1
LOOP_FRAME = LabelFrame(root, text="Synchronized Actions")
LOOP_FRAME.grid(row=0, column=1, sticky=N + W, padx=2, pady=2)
# Async Actions
# 1,0
ASYNC_FRAME = LabelFrame(root, text="Asynchronous Actions")
ASYNC_FRAME.grid(row=1, column=0, columnspan=2, sticky=N + W, padx=2, pady=2)

def next_turn(pid):
    current_player = G.players[G.turn]
    if current_player.alive and len(current_player.territories) > 0:
        if current_player.hasAllies:
            if len(current_player.ally_socket.fallen_allies) > 0:
                redistribute = ALLY_REDISTRIBUTE(LOOP_FRAME, G, current_player, 0, 0)
                res_buffer = RES_BUFFER(LOOP_FRAME, redistribute.main_frame, 0, 0)
                if not current_player.alive:
                    G.turn += 1
                    if G.turn == G.player_number:
                        print(f"Round {G.round} done.")
                        G.round += 1
                        G.turn = 0
                    next_turn(G.turn)
        curr_async = async_menu(G, ASYNC_FRAME, current_player, 0, 0)
        curr_deployment = REINFORCER(G, LOOP_FRAME, current_player, 0, 0)
        G.curr_reinforcer = curr_deployment
        curr_conquer = CONQUER(G, LOOP_FRAME, current_player, curr_deployment.main_frame, 0, 0)
        G.curr_conqueror = curr_conquer
        curr_rearranger = REARRANGER(G, LOOP_FRAME, current_player, curr_conquer.main_frame, 0, 0)
        Buffer = BUFFER(LOOP_FRAME, curr_rearranger.main_frame, curr_async, 0, 0)
    else:
        print(f"{current_player.name} has been eliminated")
    G.turn += 1
    if G.turn == G.player_number:
        print(f"Round {G.round} done.")
        G.round += 1
        for player in G.players:
            if player.hasSkill:
                if player.skill.whole_round_duration:
                    player.skill.shut_down()
        G.turn = 0
    G.public_billboard.update_view()
    next_turn(G.turn)
    print("Turn Done")

def game_loop():
    START_GAME_BTN.destroy()
    current_player = G.players[G.turn]
    if current_player.alive:
        curr_async = async_menu(G, ASYNC_FRAME, current_player, 0, 0)
        curr_deployment = REINFORCER(G, LOOP_FRAME, current_player, 0, 0)
        G.curr_reinforcer = curr_deployment
        curr_conquer = CONQUER(G, LOOP_FRAME, current_player, curr_deployment.main_frame, 0, 0)
        G.curr_conqueror = curr_conquer
        curr_rearranger = REARRANGER(G, LOOP_FRAME, current_player, curr_conquer.main_frame, 0, 0)
        Buffer = BUFFER(LOOP_FRAME, curr_rearranger.main_frame, curr_async, 0, 0)
    else:
        print(f"{current_player.name} has been eliminated")
    G.turn += 1
    print("Turn Done")
    G.public_billboard.update_view()
    next_turn(G.turn)

START_GAME_BTN = Button(LOOP_FRAME, text="Begin World War", command=game_loop)
START_GAME_BTN.grid(row=0, column=0, padx=2, pady=2)

# closing protocol
# successful, need improvements
def on_closing():
    now = date.today().strftime("%d%m%Y")
    file = open(f"{now}.txt", "w")
    for player in G.players:
        info = player.get_information_for_WS()
        file.write(player.insignia + "\n")
        for data in info:
            file.write(data + "\n")
        file.write("\n")
    file.close()
    root.destroy()
    return

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()