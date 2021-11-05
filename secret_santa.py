import smtplib
from typing import List
import random
from email.mime.text import MIMEText


class Player:
    def __init__(self,
                 email: str,
                 first_name: str,
                 family_name: str = "",
                 suggestion: List[str] = [],
                 black_list: bool = False  # Don't offer gifts to them
                 ):
        self.first_name: str = first_name
        self.name: str = first_name if family_name == "" else first_name+" "+family_name

        self.email: str = email
        self.suggestion: List[str] = suggestion
        self.black_list: bool = black_list
        self.friends_indices: List[int] = []  # Ids of friends inside list

    def __repr__(self):
        return self.name

    def add_friends(self, possible_friends: List['Player']):
        possibles_names = [f.name for f in possible_friends]

        for n in self.suggestion:
            assert n in possibles_names, f"Invalid name \"{n}\" : {possibles_names}"

        for i, n in enumerate(possibles_names):
            if n != self.name:
                if self.black_list == (n not in self.suggestion):
                    self.friends_indices.append(i)


class SecretSanta:

    def __init__(self,
                 players: List[Player],
                 email_sender: str,
                 email_password: str,
                 email_subject: str,
                 email_body: str):
        self.players = players
        self.email_sender = email_sender
        self.email_password = email_password
        self.email_subject = email_subject
        self.email_body = email_body  # String format that accepts "from", "to", "email"

        self._solution = None
        assert len(set([f.name for f in self.players])) == len(
            self.players), "Two people have the same name."

        random.shuffle(self.players)
        for p in self.players:
            p.add_friends(self.players)

        print("--- Players ---")
        for p in self.players:
            print(f"{p.name}: " + ", ".join([self.players[idx].name for idx in p.friends_indices]))
        print("---------------")

    def _build_backtracking(self,
                            new_idx: int,
                            known_indices: List[int]) -> bool:
        known_indices.append(new_idx)
        new_player = self.players[new_idx]

        if len(known_indices) == len(self.players):
            if known_indices[0] in new_player.friends_indices:
                return True
        else:
            for i in new_player.friends_indices:
                if not i in known_indices:
                    if self._build_backtracking(i, known_indices):
                        return True

        known_indices.pop()
        return False

    def build(self) -> bool:
        self._solution = None
        links = []
        if not self._build_backtracking(0, links):
            print("Impossible to link players.")
            return False

        print("Solution: " + " -> ".join([self.players[idx].name for idx in links]))
        self._solution = links
        return True

    def send(self):
        assert self._solution is not None

        solution_extended = self._solution + [self._solution[0]]
        for i in range(len(self._solution)):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(self.email_sender, self.email_password)

                src = self.players[solution_extended[i]]
                dst = self.players[solution_extended[i+1]]

                to = src.email
                assert '@' in to

                text_type = 'plain'  # or 'html'
                text = self.email_body.format(src=src.first_name, dst=dst.name)
                msg = MIMEText(text, text_type, 'utf-8')
                msg['Subject'] = self.email_subject
                msg['From'] = self.email_sender
                msg['To'] = to
                server.send_message(msg)

                server.close()

                print(f'Email sent to {to}!')
            except:
                print('Something went wrong...')


if __name__ == "__main__":
    players = [
        Player(first_name="A", email="aaaa", suggestion=["D"]),
        Player(first_name="B", email="bbbb"),
        Player(first_name="C", email="cccc"),
        Player(first_name="D", email="dddd", suggestion=["A", "B"], black_list=True)
    ]

    email_sender = "XXXX@XXXX"
    email_password = "XXXX"
    email_subject = "[Secret Santa] XXXX"
    email_body = """\
Salut {src}!

Noël approche et {dst} sera content·e de savoir que tu lui prépares une petite attention.
Tu peux dépenser jusqu'à 15€, mais si tu préfères tu peux également utiliser de la récup et le faire toi-même ;)

Pense à amener ton cadeau lors de XXXX.

Joyeuses fêtes!
"""

    secret_santa = SecretSanta(players=players,
                               email_sender=email_sender,
                               email_password=email_password,
                               email_subject=email_subject,
                               email_body=email_body)
    secret_santa.build()
    # secret_santa.send()
