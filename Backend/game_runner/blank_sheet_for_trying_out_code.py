x = 100
if 90 < x < 110:
    print("Ok")


# import sqlite3 as sq
# import datetime
#
# def init_database():
#     conn = sq.connect("HEGEMONY.db")
#     c = conn.cursor()
#     c.execute("""CREATE TABLE games (GAME_ID, GAME_DATE, PLAYER_DATA, MAP_DATA)""")
#     conn.commit()
#     conn.close()
#
# def save_new_game(game):
#     conn = sq.connect("HEGEMONY.db")
#     c = conn.cursor()
#     curr_date = datetime.date.today()
#     now = curr_date.strftime("%d/%m/%Y")
#     player_data = now + "players"
#     c.execute(f"""CREATE TABLE {player_data} VALUES (NAME, STATUS, TRTYS, SKILL, ALLIES, INDUS, INFRA, STARS, RESERVES)""")
#     conn.commit()
#     for player in game.players:
#         curr_data = (player.name, player.status, player.territories, player.skill,
#                      player.allies, player.indus, player.infra, player.stars, player.reserves)
#         c.execute(f"""INSERT INTO {player_data} {curr_data}""")
#         conn.commit()
#
#     map_data = now + "territories"
#     c.execute(f"""CREATE TABLE {map_data} (trty_name, owner, troops, city, capital, destroyed, sea_route)""")
#     conn.commit()
#     for trty in game.world.territories:
#         curr_trty = game.world.territories[trty]
#         curr_data = (curr_trty.name, curr_trty.owner, curr_trty.troops, curr_trty.isCity, curr_trty.isCapital,
#                      curr_trty.destroyed, curr_trty.is_sea_route)
#         c.execute(f"""INSERT INTO {map_data} VALUES {curr_data}""")
#         conn.commit()
#     conn.close()
#     print("GAME SAVED")
#     exit(100)

"""
from game_runner.map import *

map = Map()
map.load_sea_routes()
for trty in map.territories:
    if map.territories[trty].sea_bound:
        print(map.territories[trty].sea_side_coordinates)
"""

"""
from game_runner.map import *
from game_runner.game import *

G = Game()

G.add_player("A", "visual_assets/INSIGNIAS/insignia4.png", "visual_assets/INSIGNIAS/insignia10.png")
G.add_player("B", "visual_assets/INSIGNIAS/insignia5.png", "visual_assets/INSIGNIAS/insignia11.png")
G.add_player("C", "visual_assets/INSIGNIAS/insignia7.png", "visual_assets/INSIGNIAS/insignia12.png")
"""
#G.add_player("C", "visual_assets/INSIGNIAS/insignia6.png", "visual_assets/INSIGNIAS/insignia12.png")
#G.add_player("D", "visual_assets/INSIGNIAS/insignia7.png", "visual_assets/INSIGNIAS/insignia13.png")
#G.add_player("E", "visual_assets/INSIGNIAS/insignia8.png", "visual_assets/INSIGNIAS/insignia14.png")
#G.add_player("F", "visual_assets/INSIGNIAS/insignia9.png", "visual_assets/INSIGNIAS/insignia15.png")
"""

a = G.distribute_territories()


for pair in zip(G.players, a):
    pair[0].territories = a[pair[1]]

for player in G.players:
    for trty in player.territories:
        G.world.territories[trty].owner = player

G.players[1].allies.append(G.players[2])
G.players[2].allies.append(G.players[1])

name = G.players[1].territories[10]
print(G.world.get_connected_regions(G.players[1], name, [], [], G.players[1].allies))
print(G.world.get_strictly_connected_regions(G.players[1], name, [], [], G.players[1].allies))

"""