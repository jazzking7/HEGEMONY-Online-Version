# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
class Territory:

    def __init__(self, name, neighbors):

        self.name = name
        self.neighbors = neighbors
        self.troops = 1
        self.color = None

        self.isCapital = False
        self.isCity = False
        self.isCAD = False

        self.isMegacity = False
        self.isTransportcenter = False
        # self.isSEZ = False
        
        self.owner = None
        self.mem_stats = []


class Map:

    def __init__(self, mapName):

        self.tnames = []
        self.tneighbors = []
        self.territories = []
        self.mappath = f'MAPS/{mapName}'
        
        # Get the number of continents
        file = open(self.mappath+'/properties.txt', 'r')
        numContent = int(file.read().split('\n')[0])
        file.close()

        # Get the territory names and neighbor list continent by continent
        for i in range(1, numContent+1):
            file = open(self.mappath+f'/C{i}/c{i}tnames.txt', 'r')
            tnames = [name for name in file.read().split('\n') if name != '']
            self.tnames += tnames
            file.close()
            file = open(self.mappath+f'/C{i}/c{i}nt.txt', 'r')
            tneighbors = [name.split(',') for name in file.read().split('\n') if name != '']
            self.tneighbors += tneighbors
            file.close()

        # Create territory object for each name + list of neighbors
        for tname, tneighbors in zip(self.tnames, self.tneighbors):
            territory = Territory(tname, tneighbors)
            self.territories.append(territory)
        
        

        self.num_nations = 0
        # self.initialize_world()
        # self.biohazard = []
        # # For Route Planner
        # self.sea_routes = []
        # self.sea_side_territories = []
        # self.pre_existed_sea_routes = []
        # # Continents
        # self.continents = {"NA": ["Alaska", "British-Colombia", "California", "Johanville",
        #                           "New-York", "Ontario", "Alberta", "Nunavut", "Northern Territory"],
        #                    "CA": ["Nicaragua", "Mexico", "Colombia", "Haiti", "Port-au-Prince", "Aztec", "Panama"],
        #                    "SA": ["Peru", "Venezuela", "Argentina", "Brazil", "Uruguay"],
        #                    "SNOW": ["Yeti", "Mujik", "Jornik", "Objika"],
        #                    "ATL": ["Kassyria", "Emmett", "Kylo", "Lugnica", "Burkina Faso", "Avalon", "Akasha",
        #                            "Valka", "Lucana", "Roland", "Gastark", "Allepo", "Atis"],
        #                    "FA": ["Greenland", "Floro", "Fjord", "Iceland"],
        #                    "EU": ["Denmark", "Rotterdam", "Neuschberg", "Heisenberg", "Otter", "Britain", "Saint-Jean",
        #                           "Flandre", "Edinburgh", "Ukraine", "Zurich", "Dusseldorf", "Italia", "Rome",
        #                           "Normandie", "Munich"],
        #                    "AF": ["Algeria", "Sahara", "Egypt", "Nigeria", "Kenya", "Angola", "Botswana",
        #                           "South Africa",
        #                           "Zimbabwe", "Madagascar"],
        #                    "AS": ["Iran", "Pakistan", "Ural", "Omsk", "Sochi", "Siberia", "Yakutsk", "Bering",
        #                           "Tunguska", "Israel",
        #                           "Kazakhstan", "Middle-East", "Sri Lanka", "India", "Kashmir", "Tarim", "Tibet",
        #                           "Siam", "China",
        #                           "Mongolia", "Joseon", "Tokugawa", "Edo"],
        #                    "OC": ["Darwin", "Canberra", "Townsville", "Sydney"],
        #                    "JA": ["Javana", "Brunei", "Guinea", "Palau", "Hawaii"]}

a = Map("MichaelMap1")