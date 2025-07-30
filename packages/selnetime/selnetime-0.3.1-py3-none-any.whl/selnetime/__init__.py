from enum import Enum
from collections import namedtuple

class TransModel(Enum):
    BwS = "BwS"
    WF = "WF"

TransParam = namedtuple("TransParam", "dt N s h")

Moments = namedtuple("Moments", "mu var pfix0 pfix1 a b")
