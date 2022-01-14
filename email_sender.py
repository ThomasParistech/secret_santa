# /usr/bin/python3
"""Email sender."""
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from typing import List

from players_info import ListOfPlayerInfo

MAIL_TEMPLATE = """\
[Secret Santa] _______MAIL_OBJECT_______
Hi {src}!
______________
_______YOU_HAVE_TO_OFFER_A_GIFT_TO___ {dst}  ______________
______________
Merry Christmas
"""


@dataclass
class EmailSender:
    adress: str
    password: str
    mail_object: str
    mail_body: str

    def __init__(self, adress: str, password: str, mail_txt_file: str):
        """"
        AAAA
        """
        self.adress = adress
        self.password = password

        assert mail_txt_file.endswith(".txt"), f"Unvalid file format: {mail_txt_file}. Expect a .txt"
        with open(mail_txt_file, "r", encoding="utf-8") as _f:
            rows = _f.readlines()
            assert len(rows) > 1, "There must be at least two lines. The first one is the object, the rest is the body."
            self.mail_object = rows[0].strip()
            self.mail_body = "".join(rows[1:])
            assert "{src}" in self.mail_body and "{dst}" in self.mail_body, \
                "Invalid mail body. Must include {src} and {dst}."

    def send_mails(self, players: ListOfPlayerInfo, id_chain: List[int]):
        """"
        AAAA
        """
        assert len(players) == len(id_chain)

        for src_id, dst_id in zip(id_chain, id_chain[1:] + id_chain[0]):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(self.adress, self.password)
                text_type = 'plain'
                src = players[src_id]
                dst = players[dst_id]
                text = self.mail_body.format(src=src.name, dst=dst.name)
                msg = MIMEText(text, text_type, 'utf-8')
                msg['Subject'] = self.mail_object
                msg['From'] = self.adress
                msg['To'] = src.email
                server.send_message(msg)
                server.close()
                print(f'Email sent to {src.email}!')
            except:
                print(f'Failed to send email to {src.email}...')

    @staticmethod
    def dump_mail_template(path: str):
        assert path.endswith(".txt"), f"Unvalid file format: {path}. Expect a .txt"
        with open(path, "w", encoding="utf-8") as _f:
            _f.write(MAIL_TEMPLATE)
