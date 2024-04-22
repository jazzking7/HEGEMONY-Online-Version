class End_game_tracker:

    def __init__(self,):
        return
    
    def determine_end_game(self, gs):
        # 1 player alive
        count = 0
        for p in gs.pids:
            if gs.players[p].alive:
                count += 1
                if count == 2:
                    break
        if count < 2:
            gs.GES.halt_events()