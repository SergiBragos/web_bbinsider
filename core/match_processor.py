# core/match_processor.py
from pathlib import Path
import json
from game import Game
import analyzeShots
import analyze_shot_pass_matrix
from core.match_parser import get_xml_text, parse_xml

class GameArgs:
    username = None
    password = None
    print_events = True
    print_stats = False
    save_charts = False
    verify = False


def ensure_match_processed(matchid: str, team: str):
    matches_dir = Path(f"matches/{matchid}")
    shots_path = matches_dir / "shot_events.json"

    if shots_path.exists():
        return

    matches_dir.mkdir(parents=True, exist_ok=True)

    text = get_xml_text(matchid, matches_dir)
    events, ht, at = parse_xml(text)

    game = Game(matchid, events, ht, at, GameArgs(), [])
    game.play()

    game_json_path = matches_dir / "game.json"
    game.save(game_json_path)

    shot_events = analyzeShots.analyze_shots(matchid)
    with shots_path.open("w", encoding="utf8") as f:
        json.dump(shot_events, f, ensure_ascii=False, indent=2)

    analyze_shot_pass_matrix.ps_matrix(matchid, team, matches_dir)
