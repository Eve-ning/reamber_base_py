""" Holds multiple PtnGroups """
from __future__ import annotations
from dataclasses import dataclass
from reamber.algorithms.pattern.PtnNote import PtnNote
from typing import List
from reamber.base.lists.notes.NoteList import NoteList
from reamber.base.lists.NotePkg import NotePkg
from reamber.algorithms.pattern.PtnGroup import PtnGroup
import numpy as np
from copy import deepcopy


class PtnPkg:
    def __init__(self, lis_:NotePkg):
        self.dt = np.dtype([('column', np.int8), ('offset', np.float_), ('confidence', np.float_)])
        if lis_ is None:
            self.data = np.empty(0, dtype=self.dt)
            return

        self.data = np.empty(lis_.objCount(), dtype=self.dt)
        # noinspection PyTypeChecker
        lisCopy = [obj for i in lis_.deepcopy().data().values() for obj in i]
        lisCopy.sort(key=lambda x: x.offset)
        self.data['column'] = [i.column for i in lisCopy]
        self.data['offset'] = [i.offset for i in lisCopy]
        self.data['confidence'] = 1.0

    def customInit(self, columns, offsets):
        assert len(columns) == len(offsets), "Length of columns must be the same as offsets"

        pass

    def __len__(self):
        return len(self.data)

    def copy(self):
        return self.data.copy()

    def empty(self, length: int):
        return np.empty(length, dtype=self.dt)

    def group(self, vwindow: float = 50.0, hwindow:None or int = None, avoidJack=True,
              excludeMarked=True) -> List[np.ndarray]:
        """ Groups the package horizontally and vertically, returns a list of groups

        Warning: Having too high of a hwindow can cause overlapping groups.

        Example::

            | 6 7 X 8
            | 3 X 4 5
            | X 1 2 X
            =========

        If our window is too large, the algorithm will group it as [1,2,3,5][4,6,7,8].

        The overlapping [3,4,5] in 2 groups may cause issues in calculation.

        Let's say we want to group with the parameters
        ``vwindow = 0, hwindow = None``::

            [4s]  _5__           _5__           _5__           _5__           _X__
            [3s]  ___4  GROUP 1  ___4  GROUP 2  ___4  GROUP 3  ___X  GROUP 4  ___X
            [2s]  _2_3  ------>  _2_3  ------>  _X_X  ------>  _X_X  ------>  _X_X
            [1s]  ____  [1]      ____  [2,3]    ____  [4]      ____  [5]      ____
            [0s]  1___           X___           X___           X___           X___

            Output: [1][2,3][4][5]

        ``vwindow = 1000, hwindow = None``::

            [4s]  _5__           _5__           _5__           _X__
            [3s]  ___4  GROUP 1  ___4  GROUP 2  ___X  GROUP 3  ___X
            [2s]  _2_3  ------>  _2_3  ------>  _X_X  ------>  _X_X
            [1s]  ____  [1]      ____  [2,3,4]  ____  [5]      ____
            [0s]  1___           X___           X___           X___

            Output: [1][2,3,4][5]

        2, 3 and 4 are grouped together because 4 is within the vwindow of 2;

        ``2.offset + vwindow <= 4.offset``

        ``vwindow = 1000, hwindow = 1``::

            [4s]  _5__           _5__          _5__           _5__           _X__
            [3s]  ___4  GROUP 1  ___4  GROUP 2 ___4  GROUP 3  ___X  GROUP 4  ___X
            [2s]  _2_3  ------>  _2_3  ------> _X_3  ------>  _X_X  ------>  _X_X
            [1s]  ____  [1]      ____  [2]     ____  [3,4]    ____  [5]      ____
            [0s]  1___           X___          X___           X___           X___

            Output: [1][2][3,4][5]

        2 and 3 aren't grouped together because they are > 1 column apart. (Hence the hwindow argument)

        :param vwindow: The Vertical Window to check (Offsets)
        :param hwindow: The Horizontal Window to check (Columns). If none, all columns will be grouped.
        :param avoidJack: If True, a group will never have duplicate columns.
        :param excludeMarked: If True, any note that is already grouped will never be grouped again. If False, notes\
            that aren't grouped will be used as reference points and may include marked objects.
        """
        assert vwindow >= 0, "VWindow cannot be negative"
        assert hwindow is None or hwindow >= 0, "HWindow cannot be negative, use None to group all columns available."

        groupedArr = np.zeros(len(self), dtype=np.bool_)

        grps = []

        for i, note in enumerate(self.data):
            if groupedArr[i] is np.True_: continue  # Skip all grouped

            data = self.data
            mask = np.ones(len(data), np.bool_)

            if vwindow >= 0:
                # e.g. searchsorted([0,1,2,6,7,9], 3) -> 2
                # From this we can find the indexes where the groups are.
                left = np.searchsorted(data['offset'], note['offset'], side='left')
                right = np.searchsorted(data['offset'], note['offset'] + vwindow, side='right')
                vmask = np.zeros(len(data), np.bool_)
                indexes = list(range(left, right))

                if avoidJack:
                    # The r-hand checks if in the left-right range, if the column mismatches.
                    # We only want mismatched columns if we avoid jack
                    # e.g. [0, 1, 2]
                    cols = data['column'][indexes]

                    unqCols = np.unique(cols)
                    # This finds the first occurrences of each unique column, we add left because it's relative
                    indexes = np.intersect1d(np.array([np.where(cols == col)[0][0] for col in unqCols]) + left,
                                             indexes)
                else:
                    vmask[left:right] = True
                #
                # if True:
                #     indexes = np.intersect1d(np.array(np.where(data['offset'][left:right] != note['offset'])) + left,
                #                              indexes)
                #     indexes = np.append(left, indexes)
                vmask[indexes] = True
                mask = np.bitwise_and(mask, vmask)

            # Filter hwindow
            if hwindow is not None:
                hmask = np.zeros(len(data), np.bool_)
                hmask[abs(note['column'] - data['column']) <= hwindow] = 1
                mask = np.bitwise_and(mask, hmask)

            if excludeMarked:
                mask = np.bitwise_and(~groupedArr, mask)

            # Depending on if we want to repeat h selections, we mark differently.
            groupedArr = np.bitwise_or(groupedArr, mask)

            conf = list(1 - (self.data[mask]['offset'] - note['offset']) / vwindow)
            data = self.data[mask].copy()
            data['confidence'] = conf
            grps.append(data)

        return grps



    @staticmethod
    def combinations(groups, size=2, flatten=True):
        """ Gets all possible combinations of each subsequent pair

        :param groups:
        :param size:
        :param flatten: Whether to flatten into a singular np.ndarray
        :return:
        """

        chunks = []
        groupLen = len(groups)
        for left, right in zip(range(0, groupLen - size), range(size, groupLen)):
            chunk = groups[left:right]
            chunks.append(chunk)

        dt = np.dtype([*[(f'column{i}', np.int8) for i in range(size)],
                       *[(f'offset{i}', np.float_) for i in range(size)],
                       *[(f'difference{i}', np.float_) for i in range(size - 1)]])
        comboList: List = []

        for chunk in chunks:
            combos = np.array(np.meshgrid(*chunk)).T.reshape(-1, size)

            npCombo = np.empty(len(combos), dtype=dt)

            for i, combo in enumerate(combos):
                diffs = np.diff(combo['offset'])
                for j, col, offset in zip(range(size), combo['column'], combo['offset']):
                    npCombo[i][f'column{j}'] = col
                    npCombo[i][f'offset{j}'] = offset
                    if j != size - 1:
                        npCombo[i][f'difference{j}'] = diffs[j]

            comboList.append(npCombo)

        return np.asarray([i for j in comboList for i in j]) if flatten else comboList

