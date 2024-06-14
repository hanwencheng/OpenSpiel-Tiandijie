class ItemPlace:
    def __init__(
        self,
        item_place_id: str,
        bspanning: bool,
    ):
        self.id = item_place_id
        self.bspanning: bool = bspanning
