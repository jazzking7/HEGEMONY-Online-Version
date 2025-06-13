# Author: Jasper Wang      Date: 11/10/2022     Goal: Automated Game Runner
import collections

class Territory:

    def __init__(self, name, neighbors):

        self.name = name
        self.neighbors = neighbors
        self.troops = 1
        self.color = None

        self.isCapital = False
        self.isCity = False
        self.isCAD = False

        self.isDeadZone = 0
        

        self.isMegacity = False
        self.isTransportcenter = False
        self.isFort = False
        self.isHall = False
        # self.isSEZ = False
        
        self.owner = None
        self.mem_stats = []


class Map:

    def get_reachable_airspace(self, start, max_depth=3):
        queue = collections.deque([(start, 0)])  # Queue stores (territory, depth)
        visited = set([start])  # To track visited territories
        reachable = set()

        while queue:
            curr, depth = queue.popleft()

            if depth >= max_depth:
                continue  # Stop further exploration beyond max_depth

            for neighbor in self.territories[curr].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    reachable.add(neighbor)
                    queue.append((neighbor, depth + 1))  # Add to queue with updated depth

        return list(reachable)  # Return all reachable territories within max_depth

    def recursive_get_trty(self, curr, owned, curr_list):
        t = self.territories[curr]
        for n in t.neighbors:
            if n not in curr_list and n in owned:
                curr_list.append(n)
                self.recursive_get_trty(n, owned, curr_list)
        return curr_list 

    def get_reachable_trty(self, start, owned):
        t_list = self.recursive_get_trty(start, owned, [])        
        if len(t_list):
            t_list.remove(start)
        return t_list

    def count_cities(self, trtys):
        count = 0
        for trty in trtys:
            if self.territories[trty].isCity:
                count += 1
        return count

    def get_continental_bonus(self, trtys):
        bonus = 0
        for cont in self.conts:
            if self.own_continent(trtys, self.conts[cont]['trtys']):
                bonus += self.conts[cont]['bonus']
        return bonus

    def own_continent(self, t_list, cont_list):
        return set(cont_list).issubset(set(t_list))

    def __init__(self, mapName):
        
        self.tnames = []
        self.tneighbors = []
        self.conts = {}
        self.territories = []
        self.landlocked = []
        self.mappath = f'MAPS/{mapName}'
        
        # Get the number of continents
        file = open(self.mappath+'/properties.txt', 'r')
        lines = file.read().split('\n')
        numContent = int(lines[0])
        hasLandlock = lines[1]
        print(hasLandlock)
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
        
        tid = 0
        t_convert = {}
        # get tid of each territory
        for tname in self.tnames:
            t_convert[tname] = tid
            tid += 1
        # convert neighbors list from name to indexes
        for n in self.tneighbors:
            for i in range(len(n)):
                n[i] = t_convert[n[i]]
        # convert continent trty list from name to indexes
        for c in self.conts:
            cur = self.conts[c]['trtys']
            for i in range(len(cur)):
                cur[i] = t_convert[cur[i]]
        
        # landlock territory names
        if hasLandlock != 'no':
            file = open(self.mappath+f'/landlocked.txt', 'r')
            tnames = [name for name in file.read().split('\n') if name != '']
            self.landlocked += tnames
            file.close()

        # Create territory object for each name + list of neighbors
        for tname, tneighbors in zip(self.tnames, self.tneighbors):
            territory = Territory(tname, tneighbors)
            self.territories.append(territory)
            
        self.num_nations = len(self.territories)

        # self.biohazard = []
        # # For Route Planner
        # self.sea_routes = []
        # self.sea_side_territories = []
        # self.pre_existed_sea_routes = []