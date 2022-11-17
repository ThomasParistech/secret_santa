# /usr/bin/python3
"""Parse Secret Santa Google form."""
import numpy as np
import math
import os
import fire
from typing import List
from typing import Dict
import pandas as pd

from players_info import PlayerInfo, ListOfPlayerInfo


def parse_form(form_csv: str) -> Dict[str, List[PlayerInfo]]:
    df = pd.read_csv(form_csv, delimiter=",")
    df = df.drop(["Horodateur"], axis=1)
    df = df.rename(columns={"Nom d'utilisateur": "email",
                            "Prénom": "first_name",
                            "Nom": "family_name",
                            "Equipe": "team"})
    df = df.drop_duplicates("email")

    n_people = df.shape[0]
    print(f"{n_people} have answered the Google Form")
    print(df.head())

    return {team: [PlayerInfo(**row)
                   for row in data.drop(["team"], axis=1).to_dict('records')]
            for team, data in df.groupby(["team"])}


def generate_players_json_with_exclusions(dikt: Dict[str, List[PlayerInfo]],
                                          output_players_info_json: str):
    for players in dikt.values():
        team_names = [player.name for player in players]
        for player in players:
            player.exclude = [name for name in team_names
                              if name != player.name]

    list_players = ListOfPlayerInfo([player
                                    for players in dikt.values()
                                    for player in players])

    list_players.write(output_players_info_json)


def print_homogeneous_teams(dikt: Dict[str, List[PlayerInfo]], team_size: int):
    names = list(dikt.keys())
    counts = [len(team) for team in dikt.values()]
    n_people = sum(counts)
    n_teams = math.ceil(n_people/team_size)
    print(f"There are {n_people} people and {n_teams} teams of size {team_size}")
    print(f"Names of teams: {', '.join(names)}")
    all_teams: List[List[List[str]]] = [[] for _ in range(team_size)]
    all_teams[0] = [[] for _ in range(n_teams)]

    final_groups = []

    # Start with largest groups
    for idx in np.argsort(counts)[::-1]:
        name = names[idx]
        count = counts[idx]

        remaining = count
        while remaining > 0:
            # Add
            for teams in all_teams:
                for team in teams[:remaining]:
                    team.append(name)
                remaining -= len(teams)
                if remaining <= 0:
                    break

            # Update
            tmp_all_teams = [[] for _ in range(team_size)]
            for teams in all_teams:
                for team in teams:
                    if len(team) == team_size:
                        final_groups.append(team)
                    else:
                        tmp_all_teams[len(team)].append(team)
            all_teams = tmp_all_teams

    incomplete_groups = [team for teams in all_teams
                         for team in teams
                         if len(team) != 0]
    ####

    names_per_team = {name: [player.name for player in players]
                      for name, players in dikt.items()}

    print()
    for k, group in enumerate(final_groups+incomplete_groups):
        print(f"{k+1}) " + ", ".join(group))

    for k, group in enumerate(final_groups+incomplete_groups):
        print(f"{k+1}) " + ", ".join([names_per_team[team].pop() for team in group]))


def main(form_csv: str = 'Secret Santa C&V 2022.csv',
         output_players_info_json: str = "cv_2022_players.json",
         team_size: int = 5):
    assert os.path.isfile(form_csv)
    assert form_csv.endswith(".csv")
    assert output_players_info_json.endswith(".json")

    dikt = parse_form(form_csv)

    generate_players_json_with_exclusions(dikt, output_players_info_json)

    print_homogeneous_teams(dikt, team_size)


if __name__ == "__main__":
    fire.Fire(main)
