from reamber.base.HitObj import HitObj
from dataclasses import dataclass


@dataclass
class SMHitObj(HitObj):
    STRING: str = "1"
    pass