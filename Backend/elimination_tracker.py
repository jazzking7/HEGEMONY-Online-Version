class Elimination_tracker:

    def __init__(self, ):
        return

    def determine_elimination(self, gs, a_pid, d_pid):

        attacker = gs.players[a_pid]
        victim = gs.players[d_pid]

        # victim died
        if len(victim.territories) == 0:
            victim.alive = False
            if victim.skill:
                victim.skill.active = False
                if victim.skill.name == 'Collusion':
                    victim.skill.secret_control_list = []
                    gs.get_TIP()
                    gs.update_player_stats()
                    gs.get_SUP()
                    gs.update_global_status()
                    gs.signal_MTrackers('indus')
                
            # take away the victim's resources
            attacker.reserves += victim.reserves
            attacker.stars += victim.stars
            victim.stars = 0
            victim.reserves = 0
            gs.update_private_status(a_pid)
            gs.update_private_status(d_pid)
            print(f"{victim.name} has been eliminated by {attacker.name}")
            # victim is one of original players
            if d_pid in gs.oriPlayers and d_pid not in gs.perm_elims:
                gs.perm_elims.append(d_pid)
            # update kill logs if player not dead by mission failure
            if d_pid not in gs.death_logs:
                gs.death_logs[d_pid] = a_pid
            # check death dependent mission
            gs.signal_MTrackers('death')

        