import json
from pathlib import Path
import pandas as pd
import numpy as np

def ps_matrix(matchid: int, team: str, matches_dir: Path):
    input_file = matches_dir/"shot_events.json"
    if not input_file.exists():
        raise FileNotFoundError(input_file)

    with input_file.open(encoding="utf8") as f:
        shots = json.load(f)

    players = sorted({
        s["shooter"]
        for s in shots
        if s["team"] == team and s["shooter"] is not None
    })[:12]

    if not players:
        raise ValueError("No s'han trobat jugadors")

    points = pd.DataFrame(0, index=players, columns=players)
    attempts = pd.DataFrame(0, index=players, columns=players)

    def is_field_goal_attempt(shot):
        return shot["result"] != "missed_foul"

    def shot_points(shot):
        if shot["result"] not in ("scored", "scored_foul"):
            return 0
        if shot["shotType"] and shot["shotType"].startswith("THREE"):
            return 3
        return 2

    for shot in shots:
        if shot["team"] != team:
            continue

        shooter = shot.get("shooter")
        if shooter not in players:
            continue

        if not is_field_goal_attempt(shot):
            continue

        pts = shot_points(shot)

        if shot["assisted"]:
            passer = shot.get("passer")
            if passer in players:
                attempts.loc[passer, shooter] += 1
                points.loc[passer, shooter] += pts
        else:
            attempts.loc[shooter, shooter] += 1
            points.loc[shooter, shooter] += pts

    efficiency = points.divide(attempts).replace([np.inf, np.nan], 0).round(2)

    return points, efficiency
