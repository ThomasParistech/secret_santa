# /usr/bin/python3
"""Secret Santa."""
from typing import List
from typing import Optional

import fire
import networkx as nx
from pyvis.network import Network

from email_sender import EmailSender
from players_info import ListOfPlayerInfo


def _show_solution(players: ListOfPlayerInfo, possible_ids: List[List[int]], id_chain: List[int]):
    complete_chain = id_chain+[id_chain[0]]
    graph = nx.DiGraph()
    graph.add_nodes_from([player.name for player in players])

    for idx, list_ids in enumerate(possible_ids):
        k = complete_chain.index(idx)
        for other_idx in list_ids:
            if complete_chain[k+1] == other_idx:
                graph.add_edge(players[idx].name, players[other_idx].name, color="red")
            else:
                pass
                graph.add_edge(players[idx].name, players[other_idx].name)

    net = Network(directed=True)
    net.from_nx(graph)
    net.show("example.html")


def _init_possible_recipients(players: ListOfPlayerInfo) -> List[List[int]]:
    # Apply inclusion and exclusion lists to get all possible recipients for each player
    all_names = [player.name for player in players]
    possible_ids: List[List[int]] = [[idx for idx, other_name in enumerate(all_names)
                                      if other_name != player.name and
                                      (len(player.include) == 0 or other_name in player.include) and
                                      player not in player.exclude]
                                     for player in players]

    # Find players with a single recipient and remove useless possible recipients
    known_players = [idx for idx, list_ids in enumerate(possible_ids)
                     if len(list_ids) == 1]
    while len(known_players) != 0:
        known_idx = known_players.pop()
        recipient_idx = possible_ids[known_idx][0]
        for idx, list_ids in enumerate(possible_ids):
            if idx != known_idx and recipient_idx in list_ids:
                list_ids.remove(recipient_idx)
                if len(list_ids) == 1:
                    known_players.append(idx)

    # Print all possible recipients
    print("--- Players ---")
    for src_idx, list_ids in enumerate(possible_ids):
        print("{src}: {dst}".format(src=players[src_idx].name,
                                    dst=", ".join([players[dst_idx].name for dst_idx in list_ids])))
    print("---------------")

    return possible_ids


def _backtrack(possible_ids: List[List[int]],
               new_idx: int,
               current_id_chain: List[int]) -> bool:
    current_id_chain.append(new_idx)

    if len(current_id_chain) == len(possible_ids):
        if current_id_chain[0] in possible_ids[new_idx]:
            return True
    else:
        for idx in possible_ids[new_idx]:
            if not idx in current_id_chain:
                if _backtrack(possible_ids, idx, current_id_chain):
                    return True

    current_id_chain.pop()
    return False


def solve(players: ListOfPlayerInfo) -> Optional[List[int]]:
    """
    AAAA
    """
    players.shuffle()
    possible_ids = _init_possible_recipients(players)

    if any(len(list_ids) == 0 for list_ids in possible_ids):
        return None

    id_chain = []
    if not _backtrack(possible_ids, 0, id_chain):
        return None

    print("Solution: {}".format(" -> ".join([players[idx].name for idx in id_chain])))

    _show_solution(players, possible_ids, id_chain)
    return id_chain


def main(players: str,
         adress: str = "",
         pwd: str = "",
         txt: str = ""):
    """
    AAAAA
    """
    try:
        assert txt.endswith(".txt")
        email_sender = EmailSender(adress, pwd, txt)
        print("Email sender has been successfully instantiated.")
    except Exception as err:
        email_sender = None
        if adress == "" and pwd == "" and txt == "":
            print("Skip email automation.")
        else:
            print("Failed to instantiate the email sender.")

    assert players.endswith(".json")
    players_info = ListOfPlayerInfo.load(players)
    id_chain = solve(players_info)
    if id_chain is None:
        print("Impossible to link players.")
        exit(1)

    if email_sender is not None:
        email_sender.send_mails(players_info, id_chain)


if __name__ == "__main__":
    fire.Fire(main)
