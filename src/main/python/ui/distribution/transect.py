from pathlib import Path
from typing import List


class Transect:
    def __init__(self, name: str, numPhotos: int):
        self.name = name
        self.numPhotos = numPhotos

    def toDict(self):
        return {"name": self.name, "numPhotos": self.numPhotos}

    @staticmethod
    def fromDict(rawDict: dict):
        return Transect(rawDict["name"], rawDict["numPhotos"])

    @staticmethod
    def createFromFlight(flightFolder: Path):
        """Returns List[Transect]"""
        transects: List[Transect] = []
        for transectDir in flightFolder.iterdir():
            if not (transectDir.is_file() or transectDir.name[0] == "."):
                photos = [fp for fp in transectDir.iterdir() if fp.is_file()]
                transects.append(Transect(transectDir.name, len(photos)))
        return transects

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __str__(self):
        return f'Transect("{self.name}", {self.numPhotos})'
