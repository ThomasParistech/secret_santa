# /usr/bin/python3
"""Players info."""
import dataclasses
import json
import random
from dataclasses import dataclass
from dataclasses import field
from typing import Iterator
from typing import List


@dataclass
class PlayerInfo:
    email: str
    first_name: str
    family_name: str = ""
    include: List[str] = field(default_factory=list)  # Offer gifts only to them. Empty list means offer to everybody
    exclude: List[str] = field(default_factory=list)  # Don't offer gifts to them

    @property
    def name(self) -> str:
        return self.first_name if self.family_name == "" else f"{self.family_name} {self.family_name}"


@dataclass
class ListOfPlayerInfo:
    players: List[PlayerInfo]

    def shuffle(self):
        random.shuffle(self.players)

    def __len__(self) -> int:
        return len(self.players)

    def __iter__(self) -> Iterator[PlayerInfo]:
        return self.players.__iter__()

    def __getitem__(self, key: int) -> PlayerInfo:
        return self.players[key]

    def check(self):
        all_names = set(player.name for player in self)
        assert len(all_names) == len(self), \
            "There are at least two players with the same name. Consider specifying family names."

        for player in self:
            assert '@' in player.email, f"Invalid mail adress: {player.email}"
            for other_name in player.include+player.exclude:
                assert other_name != player.name, \
                    f"Players can't include or exclude themselves: {player.name}."
                assert other_name in all_names, \
                    f"Unknown include/exclude name: {other_name}. Players' names are {all_names}"

    @staticmethod
    def load(path: str) -> 'ListOfPlayerInfo':
        with open(path, "r", encoding="utf-8") as _f:
            players = ListOfPlayerInfo([PlayerInfo(**info) for info in json.load(_f)["players"]])
            players.check()
            return players

    @staticmethod
    def dump_template(path: str, n_players: int):
        infos = ListOfPlayerInfo([PlayerInfo(email=f"_______EMAIL_{k}_______",
                                             first_name=f"_______FIRST_NAME_{k}_______",
                                             include=["", f"_______INCLUDE_NAME_{k}_______"],
                                             exclude=2*[f"_______EXCLUDE_NAME_{k}_______"])
                                 for k in range(n_players)])

        with open(path, "w", encoding="utf-8") as _f:
            json.dump(dataclasses.asdict(infos), _f, indent=4)
