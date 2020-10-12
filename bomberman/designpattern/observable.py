"""Provides the Observable class of the design pattern observer/observable."""

from typing import List

from . import observer
from . import event


class Observable:
    def __init__(self) -> None:
        self.observers: List[observer.Observer] = []

    def add_observer(self, observer_: observer.Observer) -> None:
        self.observers.append(observer_)

    def changed(self, event_: event.Event) -> None:
        for observer_ in self.observers:
            observer_.notify(event_)
