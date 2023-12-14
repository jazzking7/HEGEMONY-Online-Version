# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
class Territory:

    def __init__(self, name, neighbors):
        self.name = name
        self.neighbors = neighbors
        self.isCapital = False
        self.isCity = False
        self.troops = 1
        self.owner = None
        self.isCAD = False
        self.mem_stats = []
        self.isMegacity = False
        self.isTransportcenter = False
        self.isSEZ = False

        self.cap_pos = None
        self.cap_dim = None

        self.city_pos = None
        self.city_dim = None

        self.insig_pos = None
        self.insig_dim = None

        self.text_pos = None
        self.text_font = None

        # Tactical blasting
        self.hasBomb = False
        # Divine punishment
        self.radio_pos = None
        self.radio_dims = None
        self.destroyed = False
        # Civil War
        self.civil_war = False
        self.internal_dist = {"R": 0, "G": 0}
        # Sea-route
        self.sea_bound = False
        self.sea_side_coordinates = []

class Map:

    # SEARCH FUNCTIONS
    # determines the connected regions of a player
    # allies included
    # visited more like selected
    # caution, territory pov
    def get_connected_regions(self, player, territory, selected, visited, allies):
        to_be_visited = []
        trty = self.territories[territory]
        # look at the neighbors
        for neighbor in trty.neighbors:
            # If the neighbor is the player's
            if self.territories[neighbor].owner == player:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if neighbor not in selected:
                        selected.append(neighbor)
            # If the neighbor is an ally
            elif self.territories[neighbor].owner in allies:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if self.territories[neighbor].isCAD and player in self.territories[neighbor].mem_stats:
                        selected.append(neighbor)
        for neighbor in to_be_visited:
            self.get_connected_regions(player, neighbor, selected, visited, allies)
        return selected

    # Temporary solution for divine punishment's radioactive effect
    def get_safely_connected_regions(self, player, territory, selected, visited, allies):
        to_be_visited = []
        trty = self.territories[territory]
        # look at the neighbors
        for neighbor in trty.neighbors:
            # If the neighbor is the player's
            if self.territories[neighbor].owner == player and [territory, neighbor] not in self.biohazard:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if neighbor not in selected:
                        selected.append(neighbor)
            # If the neighbor is an ally
            elif self.territories[neighbor].owner in allies and [territory, neighbor] not in self.biohazard:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if self.territories[neighbor].isCAD and player in self.territories[neighbor].mem_stats:
                        selected.append(neighbor)
        for neighbor in to_be_visited:
            self.get_safely_connected_regions(player, neighbor, selected, visited, allies)
        return selected

    def get_uncontested_regions(self, player, territory, selected, visited, allies):
        to_be_visited = []
        trty = self.territories[territory]
        # look at the neighbors
        for neighbor in trty.neighbors:
            # If the neighbor is the player's
            if self.territories[neighbor].owner == player:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if neighbor not in selected:
                        selected.append(neighbor)
            # If the neighbor is an ally
            elif self.territories[neighbor].owner in allies:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if self.territories[neighbor].isCAD and player in self.territories[neighbor].mem_stats:
                        selected.append(neighbor)
        for neighbor in to_be_visited:
            self.get_uncontested_regions(player, neighbor, selected, visited, allies)
        safe = []
        for trty in selected:
            if not self.territories[trty].civil_war:
                safe.append(trty)
        return safe

    # For rebellion
    def get_strictly_connected_regions(self, player, territory, selected, visited, allies):
        to_be_visited = []
        trty = self.territories[territory]
        # look at the neighbors
        for neighbor in trty.neighbors:
            # If the neighbor is the player's
            if self.territories[neighbor].owner == player:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
                    if neighbor not in selected:
                        selected.append(neighbor)
        for neighbor in to_be_visited:
            self.get_strictly_connected_regions(player, neighbor, selected, visited, allies)
        return selected

    # For airdrop
    def get_reachable_airspace(self, dep, visited, curr_depth, max_depth):
        if curr_depth > max_depth:
            return
        to_be_visited = []
        trty = self.territories[dep]
        for neighbor in trty.neighbors:
            if neighbor not in visited:
                visited.append(neighbor)
                to_be_visited.append(neighbor)
        for neighbor in to_be_visited:
            self.get_reachable_airspace(neighbor, visited, curr_depth+1, max_depth)
        return visited

    # WORLD INITIALIZATION
    def initialize_world(self):

        mapping = self.get_mapping()

        file1 = open("territories.txt", "r")
        file2 = open("neighbors.txt", "r")

        countries = file1.readlines()
        neighbors = file2.readlines()
        self.num_nations = len(countries)
        for country in range(100):
            name = countries[country].replace('\n', '')
            voisins = neighbors[country].split(",")
            voisins[len(voisins)-1] = voisins[len(voisins)-1].replace('\n', '')
            new_territory = Territory(name, voisins)
            info = mapping[name]
            if len(info) == 4:
                new_territory.insig_pos = [info[0][0], info[0][1]]
                new_territory.insig_dim = [info[0][2], info[0][3]]
                new_territory.cap_pos = [info[1][0], info[1][1]]
                new_territory.cap_dim = [info[1][2], info[1][3]]
                new_territory.city_pos = [info[2][0], info[2][1]]
                new_territory.city_dim = [info[2][2], info[2][3]]
                new_territory.text_pos = [info[3][0],  info[3][1]]
                new_territory.text_font = info[3][2]
            else:
                new_territory.insig_pos = [info[0][0], info[0][1]]
                new_territory.insig_dim = [info[0][2], info[0][3]]
                new_territory.text_pos = [info[1][0], info[1][1]]
                new_territory.text_font = info[1][2]
            if name == "Lugnica" or name == "Edinburgh" or name == "Mongolia":
                new_territory.isMegacity = True
                new_territory.troops = 10
            if name == "Alberta" or name == "Kazakhstan":
                new_territory.isTransportcenter = True
                new_territory.troops = 10
            self.names.append(name)
            self.territories[name] = new_territory
        # RADIOACTIVE
        names, display_info = self.get_radio_active_sites()
        for pair in zip(names, display_info):
            x, y = int(pair[1][0]), int(pair[1][1])
            dims = pair[1][2].split("x")
            self.territories[pair[0]].radio_pos = [x, y]
            self.territories[pair[0]].radio_dims = [int(dims[0]), int(dims[1])]
        file1.close()
        file2.close()

    def __init__(self):
        self.territories = {}
        self.names = []
        self.num_nations = 0
        self.initialize_world()
        self.biohazard = []
        # For Route Planner
        self.sea_routes = []
        self.sea_side_territories = []
        self.pre_existed_sea_routes = []
        # Continents
        self.continents = {"NA": ["Alaska", "British-Colombia", "California", "Johanville",
                                  "New-York", "Ontario", "Alberta", "Nunavut", "Northern Territory"],
                           "CA": ["Nicaragua", "Mexico", "Colombia", "Haiti", "Port-au-Prince", "Aztec", "Panama"],
                           "SA": ["Peru", "Venezuela", "Argentina", "Brazil", "Uruguay"],
                           "SNOW": ["Yeti", "Mujik", "Jornik", "Objika"],
                           "ATL": ["Kassyria", "Emmett", "Kylo", "Lugnica", "Burkina Faso", "Avalon", "Akasha",
                                   "Valka", "Lucana", "Roland", "Gastark", "Allepo", "Atis"],
                           "FA": ["Greenland", "Floro", "Fjord", "Iceland"],
                           "EU": ["Denmark", "Rotterdam", "Neuschberg", "Heisenberg", "Otter", "Britain", "Saint-Jean",
                                  "Flandre", "Edinburgh", "Ukraine", "Zurich", "Dusseldorf", "Italia", "Rome",
                                  "Normandie", "Munich"],
                           "AF": ["Algeria", "Sahara", "Egypt", "Nigeria", "Kenya", "Angola", "Botswana",
                                  "South Africa",
                                  "Zimbabwe", "Madagascar"],
                           "AS": ["Iran", "Pakistan", "Ural", "Omsk", "Sochi", "Siberia", "Yakutsk", "Bering",
                                  "Tunguska", "Israel",
                                  "Kazakhstan", "Middle-East", "Sri Lanka", "India", "Kashmir", "Tarim", "Tibet",
                                  "Siam", "China",
                                  "Mongolia", "Joseon", "Tokugawa", "Edo"],
                           "OC": ["Darwin", "Canberra", "Townsville", "Sydney"],
                           "JA": ["Javana", "Brunei", "Guinea", "Palau", "Hawaii"]}

    # set map version here
    @staticmethod
    def get_mapping():
        file3 = open("c_trty_coordinates.txt", "r")
        lines = file3.readlines()
        data = []
        for line in lines:
            line = line.replace("\n", "")
            data.append(line)
        names = []
        display_info = []
        flag = 0
        for line in data:
            if 65 <= ord(line[0]) <= 90:
                names.append(line)
                display_info.append([])
            else:
                line = line.lower()
                line = line.split(",")
                numbers = None
                if "x" in line[2]:
                    dimension = line[2].split("x")
                    numbers = [int(line[0]), int(line[1]), int(dimension[0]), int(dimension[1])]
                else:
                    numbers = [int(line[0]), int(line[1]), int(line[2])]
                display_info[len(display_info)-1].append(numbers)
        mapping = {}
        for pair in zip(names, display_info):
            mapping[pair[0]] = pair[1]
        return mapping

    # set map version here
    # RADIOACTIVE
    @staticmethod
    def get_radio_active_sites():
        file = open("trty_radio_active_site.txt", "r")
        lines = file.readlines()
        data = []
        for line in lines:
            line = line.replace("\n", "")
            data.append(line)
        names = []
        display_info = []
        for line in data:
            if 65 <= ord(line[0]) <= 90:
                names.append(line)
            else:
                line = line.split(",")
                display_info.append(line)
        return names, display_info

    # set map version here
    # LOAD_SEA_ROUTES
    def load_sea_routes(self,):
        self.sea_routes = []
        file = open("sea_side_trty_coordinates.txt", "r")
        data = file.readlines()
        parsed_data = []
        for line in data:
            line_data = line.split(": ")
            line_data[1] = line_data[1].split(" ")
            parsed_data.append(line_data)
        print(parsed_data)
        for data in parsed_data:
            self.territories[data[0]].sea_bound = True
            self.territories[data[0]].sea_side_coordinates = [int(data[1][0]), int(data[1][1])]
        return
