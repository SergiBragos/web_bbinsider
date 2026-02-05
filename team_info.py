# team_info.py
import requests
import xml.etree.ElementTree as XML
from pathlib import Path

from event import BBEvent
from player import Player
from team import Team
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re


def get_team_schedule(teamid: str) -> str:
    team_dir = Path("teams") / teamid
    team_dir.mkdir(parents=True, exist_ok=True)
    xml_path = team_dir / "schedule.xml"


    #if xml_path.exists():
        #return xml_path.read_text(encoding="utf-8")

    response = requests.get(
        f"https://www.buzzerbeater.com/team/{teamid}/schedule.aspx"
    )
    response.raise_for_status()

    xml_path.write_text(response.text, encoding="utf-8")

    return response.text



def parse_schedule(teamid: str) -> list[dict]:
    xml_text = get_team_schedule(teamid)
    root = ET.fromstring(xml_text)

    matches = []

    for match in root.findall(".//match"):
        match_id = match.attrib["id"]
        start = match.attrib["start"]
        match_type = match.attrib["type"]

        away = match.find("awayTeam")
        home = match.find("homeTeam")

        away_id = away.attrib["id"]
        home_id = home.attrib["id"]

        away_name = away.findtext("teamName")
        home_name = home.findtext("teamName")

        is_home = home_id == teamid

        competition_map = {
            "league.rs": "League",
            "league.po": "League Playoffs",
            "cup": "Cup",
            "friendly": "Friendly",
            "scrimmage": "Scrimmage",
            "bbm": "BBM",
            "b3": "B3"
        }

        competition = competition_map.get(match_type, match_type)

        matches.append({
            "match_id": match_id,
            "date": start,
            "home_team": home_name,
            "away_team": away_name,
            "is_home": is_home,
            "competition": competition,
            "raw_type": match_type
        })

    return matches



def extract_match_id_from_row(tr):
    link = tr.find("a", href=re.compile(r"/match/\d+/"))
    if not link:
        return None

    href = link["href"]  # /match/137869424/tactics.aspx
    match_id = re.search(r"/match/(\d+)/", href).group(1)
    return match_id


######
#DEBUG
######

if __name__ == "__main__":
    games = parse_schedule(teamid="138045")
    for g in games:
        print(g)