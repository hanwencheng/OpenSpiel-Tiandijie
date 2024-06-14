from open_spiel.python.games.Tiandijie.primitives.formation.FormationTemp import FormationTemp


class Formation:
    def __init__(self, player_id: int, temp: FormationTemp):
        self.player_id = player_id
        self.temp = temp
        self.is_active = False

    def check_active(self):
        # TODO
        return False

    def active_formation(self):
        self.is_active = True
