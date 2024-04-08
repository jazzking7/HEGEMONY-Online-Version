class Mission:
    def __init__(self, name, player, gs):
        self.name = name
        self.player = player
        self.gs = gs
        self.type = None

    def check_conditions(self, player):
        raise NotImplementedError("Subclasses must implement check_conditions method")

class Pacifist(Mission):

    def __init__(self, player, gs):
        super().__init__("Pacifist", player, gs)
        self.death_count = 0
        self.round = 0
        self.type = 't_based'

    def check_conditions(self, player):
        # Implement specific conditions for Mission 1
        pass

class Warmonger(Mission):
    def __init__(self, player, gs):
        super().__init__("Warmonger", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Loyalist(Mission):
    def __init__(self, player, gs):
        super().__init__("Loyalist", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Bounty_Hunter(Mission):
    def __init__(self, player, gs):
        super().__init__("Bounty_Hunter", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass
        
class Unifier(Mission):
    def __init__(self, player, gs):
        super().__init__("Unifier", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Polarizer(Mission):
    def __init__(self, player, gs):
        super().__init__("Polarizer", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Fanatic(Mission):
    def __init__(self, player, gs):
        super().__init__("Fanatic", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 1
        pass

class Industrialist(Mission):
    def __init__(self, player, gs):
        super().__init__("Industrialist", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Expansionist(Mission):
    def __init__(self, player, gs):
        super().__init__("Expansionist", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Populist(Mission):
    def __init__(self, player, gs):
        super().__init__("Populist", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass
        
class Dominator(Mission):
    def __init__(self, player, gs):
        super().__init__("Dominator", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass

class Guardian(Mission):
    def __init__(self, player, gs):
        super().__init__("Guardian", player, gs)

    def check_conditions(self, player):
        # Implement specific conditions for Mission 2
        pass