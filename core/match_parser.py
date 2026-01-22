# core/match_parser.py
import requests
import xml.etree.ElementTree as XML
from pathlib import Path

from event import BBEvent
from player import Player
from team import Team


def parse_report(report: str, at: Team, ht: Team) -> list[BBEvent]:
    events = []

    # Read players (home)
    i = 0
    index = 0
    while i < 96:
        id = int(report[i:i + 8])
        i += 8
        if index < len(ht.players):
            ht.players[index].id = id
        index += 1

    # Read players (away)
    index = 0
    while i < 192:
        id = int(report[i:i + 8])
        i += 8
        if index < len(at.players):
            at.players[index].id = id
        index += 1

    # Read starters (home)
    pos = 0
    while i < 197:
        ht.set_starter(int(report[i], 16) - 1, pos)
        i += 1
        pos += 1

    # Read starters (away)
    pos = 0
    while i < 202:
        at.set_starter(int(report[i], 16) - 1, pos)
        i += 1
        pos += 1

    # Read events
    while i < len(report):
        s = report[i:i + 17]

        e = BBEvent(
            team=int(s[0]),
            type=int(s[1:4]),
            result=int(s[4], 16),
            variation=int(s[6], 16),
            player1=int(s[7], 16),
            player2=int(s[8], 16),
            gameclock=int(s[9:13]),
            realclock=int(s[13:17]),
            data=s[1:9],
        )

        sub_type = e.type // 100
        if int(s[5]) > 0:
            e.type = -100
            e.result = 0
            sub_type = 99

        events.append(e)

        if sub_type in (1, 2, 4):
            n = BBEvent(
                team=e.team,
                type=0,
                variation=0,
                result=e.result,
                player1=e.player1,
                player2=e.player2,
                gameclock=e.gameclock.clock,
                realclock=e.realclock + 2,
                data="000{}0000".format(e.result if e.result <= 9 else e.result - 9),
            )
            events.append(n)

        i += 17

    return events



def parse_xml(text: str):
    root = XML.fromstring(text)

    ht, at = Team(), Team()
    report = ""

    for child in root:
        if child.tag == "HomeTeam":
            for t in child:
                if t.tag == "ID":
                    ht.id = int(t.text)
                elif t.tag == "Name":
                    ht.name = t.text
        elif child.tag == "AwayTeam":
            for t in child:
                if t.tag == "ID":
                    at.id = int(t.text)
                elif t.tag == "Name":
                    at.name = t.text
        elif child.tag.startswith("HPlayer") and "Nick" not in child.tag:
            ht.players.append(Player(child.text))
        elif child.tag.startswith("APlayer") and "Nick" not in child.tag:
            at.players.append(Player(child.text))
        elif child.tag == "ReportString":
            report = child.text.strip()

    while len(ht.players) < 12:
        ht.players.append(Player("Lucky Fan"))
    while len(at.players) < 12:
        at.players.append(Player("Lucky Fan"))

    events = parse_report(report, at, ht)
    return events, ht, at


def get_xml_text(matchid: str, matches_dir: Path) -> str:
    path = matches_dir / "report.xml"

    if path.exists():
        return path.read_text(encoding="utf-8")

    response = requests.get(
        f"https://buzzerbeater.com/match/viewmatch.aspx?matchid={matchid}"
    )
    response.raise_for_status()

    path.write_text(response.text, encoding="utf-8")
    return response.text
