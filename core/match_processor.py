# core/match_processor.py
from pathlib import Path
import json
from game import Game
import analyzeShots
import analyze_shot_pass_matrix
from core.match_parser import get_xml_text, parse_xml
from core.progress_store import MATCH_PROGRESS

class GameArgs:
    username = None
    password = None
    print_events = False
    print_stats = False
    save_charts = False
    verify = False


def ensure_match_processed(matchid: str, team: str):

    matches_dir = Path(f"matches/{matchid}")
    shots_path = matches_dir / "shot_events.json"

    if shots_path.exists():
        MATCH_PROGRESS[matchid] = 100
        return

    MATCH_PROGRESS[matchid] = 5

    matches_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Download XML
    MATCH_PROGRESS[matchid] = 15
    text = get_xml_text(matchid, matches_dir)

    # 2️⃣ Parse XML
    MATCH_PROGRESS[matchid] = 30
    events, ht, at = parse_xml(text)

    # 3️⃣ Game simulation
    MATCH_PROGRESS[matchid] = 55
    game = Game(matchid, events, ht, at, GameArgs(), [])
    game.play()

    # 4️⃣ Save game.json
    MATCH_PROGRESS[matchid] = 70
    game.save(matches_dir / "game.json")

    # 5️⃣ Analyze shots
    MATCH_PROGRESS[matchid] = 85
    shot_events = analyzeShots.analyze_shots(matchid)
    with shots_path.open("w", encoding="utf8") as f:
        json.dump(shot_events, f, ensure_ascii=False, indent=2)

    # 6️⃣ Final
    MATCH_PROGRESS[matchid] = 100
