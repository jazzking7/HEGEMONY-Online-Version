class Elimination_tracker:

    def __init__(self, ):
        return

    def determine_elimination(self, gs, a_pid, d_pid):

        attacker = gs.players[a_pid]
        victim = gs.players[d_pid]

        # victim died
        if len(victim.territories) == 0:
            victim.alive = False
            # take away the victim's resources
            attacker.reserves += victim.reserves
            attacker.stars += victim.stars
            print(f"{victim.name} has been eliminated by {attacker.name}")
            # victim is one of original players
            if d_pid in gs.oriPlayers:
                gs.perm_elims.append(d_pid)
            # update kill logs
            gs.death_logs[d_pid] = a_pid
            # check death dependent mission
            gs.signal_MTrackers('death')

        