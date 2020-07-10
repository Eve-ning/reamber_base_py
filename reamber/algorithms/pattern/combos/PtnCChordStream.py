from __future__ import annotations
from typing import List
from reamber.base.Hold import HoldTail
from reamber.algorithms.pattern.filters.PtnFilter import PtnFilterType, PtnFilterCombo, PtnFilterChord
from reamber.algorithms.pattern.combos.PtnCombo import PtnCombo
import numpy as np


class PtnCChordStream:
    """ Fragment of PtnCombo """

    @staticmethod
    def templateChordStream(primary:int, secondary:int,
                            keys:int, groups: List[np.ndarray],
                            andLower: bool = False,
                            includeJack: bool = False) -> np.ndarray:
        """ A template to quickly create chordstream lines

        The Primary and Secondary sizes are the size of each chord, then the subsequent one, the order doesn't matter.
        Jacks are automatically excluded unless

        All chord sizes below it are also included if ``andBelow is True``

        E.g. 1 a Jumpstream has ``primary=2, secondary=1``

        E.g. 2 a Handstream detection can use ``primary=3, secondary=2, andLower=True``. This means that you also accept
        ``primary=2, secondary=2``, ``primary=2, secondary=1``, ``primary=1, secondary=1``.

        :param primary: The primary chord size for each chord stream.
        :param secondary: The secondary chord size for each chord stream.
        :param keys: The keys of the map, used to detect pattern limits.
        :param groups: The grouping of the notes, generated from Pattern.grp
        :param andLower: Whether to include lower size chords or not
        :param includeJack: Whether to include jackstreams or not
        :return:
        """

        combo = PtnCombo.combinations(
            groups,
            size=2,
            flatten=True,
            makeSize2=True,
            chordFilter=PtnFilterChord.create(
                [[primary, secondary]], keys=keys,
                method=PtnFilterChord.Method.ANY_ORDER | PtnFilterChord.Method.AND_LOWER if andLower else 0,
                invertFilter=False).filter,
            comboFilter=PtnFilterCombo.create(
                [[0, 0]], keys=keys,
                method=PtnFilterCombo.Method.REPEAT,
                invertFilter=True).filter if not includeJack else None,
            typeFilter=PtnFilterType.create(
                [[HoldTail, object]],
                method=PtnFilterType.Method.ANY_ORDER,
                invertFilter=True).filter)

        return combo
