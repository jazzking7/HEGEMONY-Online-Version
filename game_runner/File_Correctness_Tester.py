# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
class Territory:

    def __init__(self, name, neighbors):
        self.name = name
        self.neighbors = neighbors
        self.isCapital = False
        self.isCity = False
        self.troops = 1
        self.owner = None
        self.isMegacity = False
        self.isTransportcenter = False

class Map:

    # determines the connected regions of a player
    def get_connected_regions(self, territory, visited):
        to_be_visited = []
        trty = self.territories[territory]
        for neighbor in trty.neighbors:
            if self.territories[neighbor].owner == trty.owner:
                if neighbor not in visited:
                    visited.append(neighbor)
                    to_be_visited.append(neighbor)
        for neighbor in to_be_visited:
            self.get_connected_regions(neighbor, visited)
        return visited

    def initialize_world(self):

        file1 = open("territories.txt", "r")
        file2 = open("neighbors.txt", "r")

        countries = file1.readlines()
        neighbors = file2.readlines()
        self.num_nations = len(countries)

        for country in range(100):
            name = countries[country].replace('\n', '')
            voisins = neighbors[country].split(",")
            voisins[len(voisins)-1] = voisins[len(voisins)-1].replace('\n', '')
            self.voisins.append(voisins)
            new_territory = Territory(name, voisins)
            if name == "Lugnica" or name == "Edinburgh" or name == "Mongolia":
                new_territory.isMegacity = True
                new_territory.troops = 10
            if name == "Alberta" or name == "Kazakhstan":
                new_territory.isTransportcenter = True
                new_territory.troops = 10
            self.names.append(name)
            self.territories[name] = new_territory
        file1.close()
        file2.close()

    def __init__(self):
        self.territories = {}
        self.names = []
        self.voisins = []
        self.num_nations = 0
        self.initialize_world()
        # Continents
        self.NA = ["Alaska", "British-Colombia", "California", "Johanville",
                   "New-York", "Ontario", "Alberta", "Nunavut", "Northern Territory"]
        self.CA = ["Nicaragua", "Mexico", "Colombia", "Haiti", "Port-au-Prince", "Aztec", "Panama"]
        self.SA = ["Peru", "Venezuela", "Argentina", "Brazil", "Uruguay"]
        self.SNOW = ["Yeti", "Mujik", "Jornik", "Objika"]
        self.ATL = ["Kassyria", "Emmett", "Kylo", "Lugnica", "Burkina Faso", "Avalon", "Akasha",
                    "Valka", "Lucana", "Roland", "Gastark", "Allepo", "Atis"]
        self.FA = ["Greenland", "Floro", "Fjord", "Iceland"]
        self.EU = ["Denmark", "Rotterdam", "Neuschberg", "Heisenberg", "Otter", "Britain", "Saint-Jean",
                   "Flandre", "Edinburgh", "Ukraine", "Zurich", "Dusseldorf", "Italia", "Rome", "Normandie", "Munich"]
        self.AF = ["Algeria", "Sahara", "Egypt", "Nigeria", "Kenya", "Angola", "Botswana", "South Africa",
                   "Zimbabwe", "Madagascar"]
        self.AS = ["Iran", "Pakistan", "Ural", "Omsk", "Sochi", "Siberia", "Yakutsk", "Bering", "Tunguska", "Israel",
                   "Kazakhstan", "Middle-East", "Sri Lanka", "India", "Kashmir", "Tarim", "Tibet", "Siam", "China",
                   "Mongolia", "Joseon", "Tokugawa", "Edo"]
        self.OC = ["Darwin", "Canberra", "Townsville", "Sydney"]
        self.JA = ["Javana", "Brunei", "Guinea", "Palau", "Hawaii"]

        for voisin in self.voisins:
            for item in voisin:
                if item not in self.names:
                    print("NOT CORRECT")
        for item in self.NA:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.CA:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.SA:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.SNOW:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.ATL:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.FA:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.EU:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.AF:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.AS:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.OC:
            if item not in self.names:
                print("NOT CORRECT")
        for item in self.JA:
            if item not in self.names:
                print("NOT CORRECT")
        print("No mistakes, all good.")
m = Map()
