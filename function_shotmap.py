# ==================================================
# BBINSIDER – SHOT ZONE ANALYSIS & VISUALIZATION
# ==================================================
import json
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
from collections import defaultdict
from matplotlib.patches import Polygon


# ==================================================
# ANALYSIS ZONES (shotType -> logical zone)
# ==================================================
ANALYSIS_ZONES = {
    "DUNK": ["DUNK1", "DUNK2", "PUTBACK_DUNK"],
    "PAINT_SHOT": ["LAYUP", "DRIVING_LAYUP", "POST_UP_MOVE", "FADE_AWAY", "HOOK", "OFF_DRIBBLE_JUMP_SHOT","TIPIN","REBOUND_SHOT"],
    "TWO_POINTER_TOPKEY": ["TWO_POINTER_DEFAULT", "TWO_POINTER_TOPKEY"],
    "TWO_POINTER_ELBOW": ["TWO_POINTER_ELBOW"],
    "TWO_POINTER_WING": ["TWO_POINTER_WING"],
    "TWO_POINTER_BASELINE": ["TWO_POINTER_BASELINE"],
    "THREE_POINTER_LONG": ["THREE_POINTER_DEFAULT", "THREE_POINTER_LONG", "THREE_POINTER_HALFCOURT"],
    "THREE_POINTER_TOPKEY": ["THREE_POINTER_TOPKEY"],
    "THREE_POINTER_WING": ["THREE_POINTER_WING"],
    "THREE_POINTER_CORNER": ["THREE_POINTER_CORNER"]
}

# Mapeja al revés el diccionari ANALYSIS_ZONES: shotType -> analysis zone
SHOTTYPE_TO_ZONE = {
    st: zone
    for zone, shot_types in ANALYSIS_ZONES.items()
    for st in shot_types
}


# ==================================================
# COURT NORMALIZATION (away -> home side)
# ==================================================
COURT_WIDTH = 368
COURT_HEIGHT = 192
CENTER_X = COURT_WIDTH / 2
CENTER_Y = COURT_HEIGHT / 2

def normalize_shot(x, y):
    """Porta tots els tirs a la meitat esquerra del camp"""
    if x > CENTER_X:
        x = COURT_WIDTH - x
        y = COURT_HEIGHT - y
    return x, y


# ==================================================
# ZONE POLYGONS
# ==================================================
def mirrory(points, center_y=96):
    """Simetria respecte eix horitzontal"""
    return [(x, 2 * center_y - y) for x, y in points]


dunk = [(16,128),(30,128),(46,116),(52,96),(46,76),(30,64),(16,64)]
paint_shot = [(16,128),(16,146),(40,142),(56,130),(70,112),(70,80),(56,62),(40,50),(16,46),(16,64),(30,64),(46,76),(52,96),(46,116),(30,128)]
two_pointer_baseline = [(0,128),(16,128),(16,180),(0,180)]
two_pointer_wing = [(16,146),(40,142),(56,130),(92,154),(70,172),(52,180),(16,180)]
two_pointer_elbow = [(56,130),(92,154),(100,142),(104,132),(70,112)]
two_pointer_topkey = [(70,112),(104,132),(110,118),(116,96),(110,74),(104,60),(70,80)]
three_pointer_corner = [(0,180),(30,180),(30,192),(0,192)]
three_pointer_wing = [(30,180),(52,180),(70,172),(92,154),(100,142),(118,152),(78,192),(30,192)]
three_pointer_topkey = [(100,142),(118,152),(132,116),(112,112),(110,118)]
three_pointer_long = [(120, 96),(120, 114),(132, 116),(118, 152),(78, 192),(130, 192),(152, 120),(152, 72),(130, 0),(78, 0),(118, 40),(132, 76),(120, 78)]


# Funció de carregar dades de tirs útils (no faltes ni cap altre esdeveniment)
def generate_shotmap_data(match_ids, team=("home", "away"), player=None, analysis_zone=None):
    shots = []

    # Si l'equip és "home,away" ho transforma en "home","away" per tl que la funció ho entengui.
    #Ara passa això:
    #"home" → ("home",)
    #"away" → ("away",)
    #"home,away" → ("home", "away")
    if isinstance(team, str):
        team = tuple(t.strip() for t in team.split(","))
        print("TEAM NORMALIZED FROM STR:", team)
    elif isinstance(team, list) and len(team) == 1 and "," in team[0]:
        team = tuple(t.strip() for t in team[0].split(","))
        print("TEAM NORMALIZED FROM LIST:", team)
    #El mateix si passes varis match_id. Els normalitza com a tupla d'IDs individuals.
    if isinstance(match_ids, str):
        match_ids = tuple(m.strip() for m in match_ids.split(","))
        print("ID NORMALIZED FROM STR:", match_ids)
    elif isinstance(match_ids, list) and len(match_ids) == 1 and "," in match_ids[0]:
        match_ids = tuple(m.strip() for m in match_ids[0].split(","))
        print("ID NORMALIZED FROM LIST:", match_ids)
    for match_id in match_ids:
        path = Path("matches") / match_id / "shot_events.json"
        with open(path, "r", encoding="utf-8") as f:
            shots.extend(json.load(f))

    zone_stats = defaultdict(lambda: {"attempts": 0, "made": 0})
    filtered = []

    for s in shots:
        if team and s["team"] not in team:
            continue
        if s["result"] == "missed_foul":
            continue
        if player and s["shooter"] != player:
            continue

        zone = SHOTTYPE_TO_ZONE.get(s.get("shotType"))
        if not zone or (analysis_zone and zone != analysis_zone):
            continue

        zone_stats[zone]["attempts"] += 1
        if s["result"] in ("scored", "scored_foul"):
            zone_stats[zone]["made"] += 1

        s["x"], s["y"] = normalize_shot(s["x"], s["y"])
        filtered.append(s)

    print("TOTAL SHOTS LOADED:", len(filtered)) #DEBUG: Mirar si quan l'equip és "home,away" passa tirs
    return zone_stats, filtered


# Funció de dibuix dels tirs
def draw_shotmap(zone_stats, shots, show=True, show_individual_shots=False, output_path=None):
    court = Image.open("halfcourt.png")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(court)
    ax.axis("off")
    ZONES = {
    "DUNK": [Polygon(dunk)],
    "PAINT_SHOT": [Polygon(paint_shot)],
    "TWO_POINTER_BASELINE": [Polygon(two_pointer_baseline), Polygon(mirrory(two_pointer_baseline))],
    "TWO_POINTER_WING": [Polygon(two_pointer_wing), Polygon(mirrory(two_pointer_wing))],
    "TWO_POINTER_ELBOW": [Polygon(two_pointer_elbow), Polygon(mirrory(two_pointer_elbow))],
    "TWO_POINTER_TOPKEY": [Polygon(two_pointer_topkey)],
    "THREE_POINTER_TOPKEY": [Polygon(three_pointer_topkey), Polygon(mirrory(three_pointer_topkey))],
    "THREE_POINTER_WING": [Polygon(three_pointer_wing), Polygon(mirrory(three_pointer_wing))],
    "THREE_POINTER_CORNER": [Polygon(three_pointer_corner), Polygon(mirrory(three_pointer_corner))],
    "THREE_POINTER_LONG": [Polygon(three_pointer_long)]
}


    for zone_name, shapes in ZONES.items():
        stats = zone_stats.get(zone_name, {"attempts": 0, "made": 0})
        attempts, made = stats["attempts"], stats["made"]
        pct = made / attempts if attempts else 0

        for shape in shapes:

            pts = shape.get_xy()
            cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
            if zone_name == "PAINT_SHOT":
                cx, cy = 60, 96
            elif zone_name == "THREE_POINTER_WING":
                cx, cy = 84,18
            elif zone_name == "THREE_POINTER_LONG":
                cx, cy = 140,96
            elif zone_name == "THREE_POINTER_TOPKEY":
                cx, cy = 116,60

            shape.set_edgecolor("black")
            if attempts > 0:
                shape.set_alpha(0.8)
                shape.set_facecolor((1 - pct, pct, 0))
                ax.text(cx, cy, f"{made}/{attempts}\n({pct:.1%})",
                fontsize=8, ha="center", va="center")
            else:
                shape.set_alpha(0.1)
                shape.set_facecolor((0, 0, 1))
                ax.text(cx, cy, f"{made}/{attempts}",
                fontsize=7, ha="center", va="center")
            ax.add_patch(shape)

    if show_individual_shots:
        for s in shots:
            color = "green" if s["result"] == "scored" else "red"
            ax.scatter(s["x"], s["y"], s=20, c=color, alpha=0.7, edgecolors="black")

    if output_path:
        plt.savefig(output_path, dpi=200, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)


#Crida a les dues funcions anteriors per generar dades i dibuixar les zones de tir. És la funció que executa pas per pas tota la resta de l'arxiu!
def shotmap(match_ids,team,player=None,analysis_zone=None,show_individual_shots=False,show=True,output_path=None):

    zone_stats, shots = generate_shotmap_data(match_ids, team, player, analysis_zone)

    draw_shotmap(zone_stats,shots,show=show,show_individual_shots=show_individual_shots,output_path=output_path)

    return zone_stats



######
#DEBUG
######

if __name__ == "__main__":
    zone_stats = shotmap(
        match_ids="137869361,137869372",
        team="home,away",
        player="Constantí Sucarrats",
        show_individual_shots=True,
        show=True
    )

    print("ZONE STATS:")
    for zone, stats in zone_stats.items():
        print(zone, stats)
