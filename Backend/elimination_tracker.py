class Elimination_tracker:

    def __init__(self, ):
        return

    def determine_elimination(self, player):
        if len(player.territories) == 0:
            player.alive = False
            player.mission = None
        