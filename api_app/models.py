from dataclasses import dataclass


@dataclass
class Storm:
    id: str
    date: str
    # If there are other keys in some dictionaries, you would add them here as attributes


@dataclass
class Storms:
    storms: list[Storm]
