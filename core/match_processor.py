# core/match_processor.py
from pathlib import Path
import json
from game import Game
import analyzeShots
import analyze_shot_pass_matrix
from core.match_parser import get_xml_text, parse_xml
from core.progress_store import (init_match, update_match, finish_match, MATCH_PROGRESS)

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

    if matchid not in MATCH_PROGRESS:
        init_match(matchid)

    if shots_path.exists():
        #print(f"El partit {matchid} ja existeix, no cal descarregar-lo")
        update_match(matchid, 100)
        return finish_match(matchid, "done")

    update_match(matchid, 5)

    matches_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Download XML
    update_match(matchid, 15)
    #print(f"get_xml_text: Descarregant fitxer XML del partit {matchid}")
    text = get_xml_text(matchid, matches_dir)

    # 2️⃣ Parse XML
    update_match(matchid, 30)
    #print(f"parse_xml: Parsejant fitxer XML del partit {matchid} (aconsegueixo home team, away team i events)")
    events, ht, at = parse_xml(text)
    if not events:
        update_match(matchid, 100)
        #print(f"⚠️ Match skipped (no ReportString): {matchid}")
        return

    # 3️⃣ Game simulation
    update_match(matchid, 55)
    #print("fitxer match_processor. Variable GameArgs: ", GameArgs)
    game = Game(matchid, events, ht, at, GameArgs, [])
    game.play()

    # 4️⃣ Save game.json
    update_match(matchid, 70)

    tmp_path = matches_dir / "game.json.tmp"
    final_path = matches_dir / "game.json"

    game.save(tmp_path)
    tmp_path.replace(final_path)

    # 5️⃣ Analyze shots
    #print("Obrint AnalyzeShots.py del partit {matchid}")
    update_match(matchid, 85)
    shot_events = analyzeShots.analyze_shots(matchid)
    with shots_path.open("w", encoding="utf8") as f:
        json.dump(shot_events, f, ensure_ascii=False, indent=2)

    # 6️⃣ Final
    finish_match(matchid, "done")
