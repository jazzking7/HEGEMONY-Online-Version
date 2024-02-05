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
        self.conts = {}
        self.territories = []
        self.mappath = f'MAPS/{mapName}'
        
        # Get the number of continents
        file = open(self.mappath+'/properties.txt', 'r')
        numContent = int(file.read().split('\n')[0])
        file.close()

        # Get the territory names and neighbor list continent by continent
        for i in range(1, numContent+1):
            # get continent properties
            file = open(self.mappath+f'/C{i}/c{i}p.txt', 'r')
            contp = [p for p in file.read().split('\n') if p != '']
            file.close()

            # get name of territories belonging to the continent
            file = open(self.mappath+f'/C{i}/c{i}tnames.txt', 'r')
            tnames = [name for name in file.read().split('\n') if name != '']
            self.tnames += tnames
            file.close()

            # get neighbor relationship of territories
            file = open(self.mappath+f'/C{i}/c{i}nt.txt', 'r')
            tneighbors = [name.split(',') for name in file.read().split('\n') if name != '']
            self.tneighbors += tneighbors
            file.close()

            # add continent
            self.conts[contp[0]] = {'bonus': int(contp[1]), 'trtys': tnames}
        
        # Create territory object for each name + list of neighbors
        for tname, tneighbors in zip(self.tnames, self.tneighbors):
            territory = Territory(tname, tneighbors)
            self.territories.append(territory)
        
        # self.tnames = None
        # self.tneighbors = None
        self.num_nations = len(self.territories)

        # self.biohazard = []
        # # For Route Planner
        # self.sea_routes = []
        # self.sea_side_territories = []
        # self.pre_existed_sea_routes = []
    
