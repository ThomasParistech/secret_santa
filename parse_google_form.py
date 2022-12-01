# /usr/bin/python3
"""Parse Secret Santa Google form."""
import fire
from typing import List
import pandas as pd

from players_info import PlayerInfo, ListOfPlayerInfo


def parse_form(form_csv: str) -> List[List[PlayerInfo]]:
    df = pd.read_csv(form_csv, delimiter=",")
    df = df.drop(["Timestamp"], axis=1)
    df = df.rename(columns={"Username": "email",
                            "First Name": "first_name",
                            "Last Name": "family_name",
                            "Team": "team"})
    df = df.drop_duplicates("email")

    print(f"{df.shape[0]} have answered the Google Form")
    print(df.head())
    return [[PlayerInfo(**row) for row in data.drop(["team"], axis=1).to_dict('records')]
            for _, data in df.groupby(["team"])]


def main(form_csv: str, output_players_info_json: str):
    groups_of_players = parse_form(form_csv)

    # Apply exclusion rules
    for players in groups_of_players:
        team_names = [player.name for player in players]
        for player in players:
            player.exclude = [name for name in team_names
                              if name != player.name]

    list_players = ListOfPlayerInfo([player
                                    for players in groups_of_players
                                    for player in players])

    list_players.write(output_players_info_json)


if __name__ == "__main__":
    fire.Fire(main)
