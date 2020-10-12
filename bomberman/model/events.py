"""All the events used by the model based on the observer/observable event."""

from __future__ import annotations

from . import entity
from ..designpattern.event import Event


class EntityEvent(Event):
    def __init__(self, entity_: entity.Entity):
        super().__init__()
        self.entity = entity_


class NewEntityEvent(EntityEvent):
    pass


class ForwardTimeEvent(EntityEvent):
    pass


class MovedEntityEvent(EntityEvent):
    pass


class HitEntityEvent(EntityEvent):
    pass


class RemovingEntityEvent(EntityEvent):
    pass


class RemovedEntityEvent(EntityEvent):
    pass
