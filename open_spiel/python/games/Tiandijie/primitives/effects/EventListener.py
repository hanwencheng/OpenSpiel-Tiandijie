from functools import partial

from primitives.effects.Event import EventTypes


class EventListener:
    def __init__(
        self,
        event_type: EventTypes,
        priority: int,
        requirement: partial or None,
        listener_effects: partial,
    ):
        if requirement is None:
            self.requirement = lambda x, y, z: 1
        self.event_type = event_type
        self.priority = priority
        self.listener_effects = listener_effects
        self.requirement = requirement
