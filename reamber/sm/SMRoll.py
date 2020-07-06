from reamber.base.Hold import Hold, HoldTail
from dataclasses import dataclass, field


@dataclass
class SMRollTail(HoldTail):
    pass

@dataclass
class SMRoll(Hold):

    _tail: SMRollTail = field(init=False)

    def _upcastTail(self, **kwargs) -> SMRollTail:
        return SMRollTail(**kwargs)

