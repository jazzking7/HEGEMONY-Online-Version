class Elimination_tracker:

    def __init__(self, ):
        return

    def determine_elimination(self, attacker, victim):
        if len(victim.territories) == 0:
            victim.alive = False
            victim.mission = None
            # take away the victim's resources
            attacker.reserves += victim.reserves
            attacker.stars += victim.stars
            print(f"{victim.name} has been eliminated by {attacker.name}")
        