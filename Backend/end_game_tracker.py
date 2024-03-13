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
            vp = None
            for p in gs.pids:
                if gs.players[p].alive:
                    vp = gs.players[p] 
            gs.GES.halt_events()
            gs.signal_view_clear()
            gs.server.emit('set_up_announcement', {'msg': f"GAME OVER\n{vp.name}'s victory!"})