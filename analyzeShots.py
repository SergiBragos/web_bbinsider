import json
from pathlib import Path

  # =====================================================
  # 1. MAPES DE TRADUCCIÓ I PLAYER MAP
  # =====================================================
TEAM_KEY = {
      0: "home",
      1: "away"
  }

RESULT_KEY = {
      '0': "missed",
      '1': "scored",
      '2': "goaltend",
      '3': "blocked",
      '4': "missed_foul",
      '5': "scored_foul"
  }

SHOT_KEY = {
      # ===== THREE POINTERS =====
      '100': "THREE_POINTER_DEFAULT",
      '101': "THREE_POINTER_TOPKEY",
      '102': "THREE_POINTER_WING",
      '103': "THREE_POINTER_CORNER",
      '104': "THREE_POINTER_LONG",
      '105': "THREE_POINTER_HALFCOURT",

      # ===== MID DISTANCE =====
      '200': "TWO_POINTER_DEFAULT",
      '201': "TWO_POINTER_ELBOW",
      '202': "TWO_POINTER_WING",
      '203': "TWO_POINTER_BASELINE",
      '204': "TWO_POINTER_TOPKEY",

      # ===== FINISHES / PAINT =====
      '401': "DUNK1",
      '402': "LAYUP",
      '403': "POST_UP_MOVE",
      '404': "FADE_AWAY",
      '405': "HOOK",
      '406': "OFF_DRIBBLE_JUMP_SHOT",
      '411': "DRIVING_LAYUP",

      # ===== TIPIN =====
      '407': "PUTBACK_DUNK",
      '408': "TIPIN",
      '409': "REBOUND_SHOT",
      '410': "DUNK2"
  }

playerMap = {
      "home": {},
      "away": {}
  }

  # Home team
  
def analyze_shots(game_id):
  
  input_file = Path(f"./matches/{game_id}/game.json")
  with input_file.open(encoding="utf8") as f:
    data = json.load(f)

  for index, player in enumerate(data["teamHome"]["players"]):
    number = index + 1
    playerMap["home"][number] = player["name"]

  # Away team
  for index, player in enumerate(data["teamAway"]["players"]):
    number = index + 1
    playerMap["away"][number] = player["name"]

  shotEvents = []

  # =====================================================
  # 4. PROCESSAR ESDEVENIMENTS DEL PARTIT
  # =====================================================
  for event in data["events"]:

    # Només tirs
    if event.get("event_type") != "shot":
      continue

    # Validacions bàsiques
    if event.get("attacking_team") is None or event.get("attacker") is None:
      continue

    # Traduir equips
    team = TEAM_KEY.get(event["attacking_team"])
    def_team = TEAM_KEY.get(event.get("defending_team"))

    if team is None:
      continue

    # Jugadors
    shooter = playerMap[team].get(event["attacker"])
    passer = playerMap[team].get(event.get("assistant"))
    defender = playerMap.get(def_team, {}).get(event.get("defender"))

    # Altres dades
    shot_type = SHOT_KEY.get(event.get("shot_type"))
    result = RESULT_KEY.get(event.get("shot_result"))
    posx = event.get("shot_pos_x")
    posy = event.get("shot_pos_y")

    shot_event = {
      "team": team,
      "shooter": shooter,
      "passer": passer if event.get("assistant") else None,
      "defender": defender if event.get("defender") else None,
      "shotType": shot_type,
      "result": result,
      "assisted": bool(event.get("assistant")),
      "x": posx,
      "y": posy
    }

    shotEvents.append(shot_event)

  # =====================================================
  # 5. GUARDAR RESULTAT
  # =====================================================
  return shotEvents

