from reamber.sm.SMMapSetObject import SMMapSetObject, SMMapObject
from reamber.osu.OsuMapObject import OsuMapObject
from reamber.osu.OsuHitObject import OsuHitObject
from reamber.osu.OsuHoldObject import OsuHoldObject
from reamber.osu.OsuBpmPoint import OsuBpmPoint
from reamber.base.BpmPoint import BpmPoint
from reamber.base.NoteObject import NoteObject
from typing import List


class SMToOsu:
    @staticmethod
    def convert(sm: SMMapSetObject) -> List[OsuMapObject]:
        """ Converts a Mapset to possibly multiple osu maps
        Note that a mapset contains maps, so a list would be expected.
        SMMap conversion is not possible due to lack of SMMapset Metadata
        :param sm: The MapSet
        :return: Osu Map
        """

        # I haven't tested with non 4 keys, so it might explode :(

        osuMapSet: List[OsuMapObject] = []
        for smMap in sm.maps:
            assert isinstance(smMap, SMMapObject)
            notes: List[NoteObject] = []

            # Note Conversion
            for note in smMap.notes.hits():
                notes.append(OsuHitObject(offset=note.offset, column=note.column))
            for note in smMap.notes.holds():
                notes.append(OsuHoldObject(offset=note.offset, column=note.column, length=note.length))

            bpms: List[BpmPoint] = []

            # Timing Point Conversion
            for bpm in smMap.bpms:
                bpms.append(OsuBpmPoint(offset=bpm.offset, bpm=bpm.bpm))

            # Extract Metadata
            osuMap = OsuMapObject(
                backgroundFileName=sm.background,
                title=sm.title,
                titleUnicode=sm.titleTranslit,
                artist=sm.artist,
                artistUnicode=sm.artistTranslit,
                audioFileName=sm.music,
                creator=sm.credit,
                version=f"{smMap.difficulty} {smMap.difficultyVal}",
                previewTime=int(sm.sampleStart),
                bpms=bpms,
                notes=notes
            )
            osuMapSet.append(osuMap)
        return osuMapSet
