# core/match_processor.py
from pathlib import Path
import json
from game import Game
import analyzeShots
import analyze_shot_pass_matrix
from core.match_parser import get_xml_text, parse_xml
from core.progress_store import MATCH_PROGRESS

GameArgs = {
        "username": None,
        "password": None,
        "print_events": False,
        "print_stats": False,
        "save_charts": False,
        "verify": False
        }


def ensure_match_processed(matchid: str, team: str):

    matches_dir = Path(f"matches/{matchid}")
    shots_path = matches_dir / "shot_events.json"

    if shots_path.exists():
        print(f"El partit {matchid} ja existeix, no cal descarregar-lo")
        MATCH_PROGRESS[matchid] = 100
        return

    MATCH_PROGRESS[matchid] = 5

    matches_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Download XML
    MATCH_PROGRESS[matchid] = 15
    #print(f"get_xml_text: Descarregant fitxer XML del partit {matchid}")
    text = get_xml_text(matchid, matches_dir)

    # 2️⃣ Parse XML
    MATCH_PROGRESS[matchid] = 30
    #print(f"parse_xml: Parsejant fitxer XML del partit {matchid} (aconsegueixo home team, away team i events)")
    events, ht, at = parse_xml(text)
    if not events:
        MATCH_PROGRESS[matchid] = 100
        #print(f"⚠️ Match skipped (no ReportString): {matchid}")
        return

    # 3️⃣ Game simulation
    MATCH_PROGRESS[matchid] = 55
    #print("fitxer match_processor. Variable GameArgs: ", GameArgs)
    game = Game(matchid, events, ht, at, GameArgs, [])
    game.play()

    # 4️⃣ Save game.json
    #print(f"Guardant partit {matchid}")
    MATCH_PROGRESS[matchid] = 70
    game.save(matches_dir / "game.json")

    # 5️⃣ Analyze shots
    #print("Obrint AnalyzeShots.py del partit {matchid}")
    MATCH_PROGRESS[matchid] = 85
    shot_events = analyzeShots.analyze_shots(matchid)
    with shots_path.open("w", encoding="utf8") as f:
        json.dump(shot_events, f, ensure_ascii=False, indent=2)

    # 6️⃣ Final
    MATCH_PROGRESS[matchid] = 100
