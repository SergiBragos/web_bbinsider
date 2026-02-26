#training.py

import math
from bbapi import BBApi
import password

MAIN_SKILLS = ["JS", "JR", "OD", "HA", "DR", "PA", "IS", "ID", "RB", "SB"]

# Coeficients base que s'entrenen quan selecciones un entrenament
COEFF = {
  "None": {},

  "JS for 12": {"JS":0.5, "JR":0.1, "HA":0.05, "DR":0.05},
  "JS for 34": {"JS":0.4, "JR":0.05, "IS":0.2},
  "JS for 23": {"JS":0.5, "JR":0.1, "HA":0.05, "DR":0.05},
  "JS for team": {"JS":0.22, "JR":0.044, "HA":0.022, "DR":0.022},

  "JR for 2": {"JR":0.4, "JS":0.2, "HA":0.05, "DR":0.05},
  "JR for 12": {"JR":0.3, "JS":0.15, "HA":0.0375, "DR":0.0375},
  "JR for 23": {"JR":0.3, "JS":0.15, "HA":0.0375, "DR":0.0375},
  "JR for team": {"JR":0.1, "JS":0.05, "HA":0.0125, "DR":0.0125},

  "OD for 1": {"OD":0.5, "HA":0.05, "DR":0.05, "ID":0.1},
  "OD for 12": {"OD":0.375, "HA":0.0375, "DR":0.0375, "ID":0.075},
  "OD for 123": {"OD":0.2, "HA":0.02, "DR":0.02, "ID":0.04},

  "HA for 1": {"HA":0.5, "OD":0.1, "DR":0.4},
  "HA for 12": {"HA":0.375, "OD":0.075, "DR":0.3},
  "HA for 123": {"HA":0.2, "OD":0.04, "DR": 0.16},

  "DR for 12": {"JS":0.4, "DR":0.5, "HA":0.4},
  "DR for 34": {"JS":0.2, "DR":0.5, "HA":0.4, "IS":0.2},
  "DR for team": {"JS":0.088, "DR":0.22, "HA":0.176, "IS":0.088},

  "PA for 1": {"HA": 0.16, "DR": 0.16, "PA":0.6},
  "PA for 12": {"HA": 0.12, "DR": 0.12, "PA":0.45},
  "PA for team": {"HA": 0.04, "DR": 0.04, "PA":0.15},

  "IS for 5": {"IS":0.5, "JS":0.1, "ID": 0.05},
  "IS for 45": {"IS":0.375, "JS":0.075, "ID": 0.038},
  "IS for 345": {"IS":0.2, "JS":0.04, "ID": 0.02},

  "ID for 5": {"ID":0.5, "IS":0.05, "SB": 0.1},
  "ID for 45": {"ID":0.375, "IS":0.0375, "SB": 0.075},
  "ID for 345": {"ID":0.2, "IS":0.02, "SB": 0.04},

  "RB for 45": {"RB":0.5, "ID":0.05, "IS": 0.05},
  "RB for team": {"RB":0.22, "ID":0.022, "IS": 0.02},

  "SB for 5": {"SB":0.5, "ID":0.2, "RB": 0.1},
  "SB for 45": {"SB":0.375, "ID":0.15, "RB": 0.075},
  "SB for 345": {"SB":0.2, "ID":0.08, "RB": 0.04},
}
#Habilitat que marca el coeficient de cross training per a cada tipus d'entrenament
PRIMARY_SKILL = {
    "None": "PA",
    "JS for 12": "JS",
    "JS for 34": "JS",
    "JS for 23": "JS",
    "JS for team": "JS",

    "JR for 2": "JR",
    "JR for 12": "JR",
    "JR for 23": "JR",
    "JR for team": "JR",

    "OD for 1": "OD",
    "OD for 12": "OD",
    "OD for 123": "OD",

    "HA for 1": "HA",
    "HA for 12": "HA",
    "HA for 123": "HA",

    "DR for 12": "DR",
    "DR for 34": "DR",
    "DR for team": "DR",

    "PA for 1": "PA",
    "PA for 12": "PA",
    "PA for team": "PA",

    "IS for 5": "IS",
    "IS for 45": "IS",
    "IS for 345": "IS",

    "ID for 5": "ID",
    "ID for 45": "ID",
    "ID for 345": "ID",

    "RB for 45": "RB",
    "RB for team": "RB",

    "SB for 5": "SB",
    "SB for 45": "SB",
    "SB for 345": "SB"
}
#ELASTIC_EFFECT["JS"] son totes les habilitats que afecten el valor actual de JS en un entrenament
ELASTIC_EFFECT = {
    "JS": [0,1,0,1,1,0,0,0,0,0],
    "JR": [1,0,0,1,1,0,0,0,0,0],
    "OD": [0,0,0,1,1,0,0,1,0,0],
    "HA": [0,0,1,0,1,0,0,0,0,0],
    "DR": [1,0,0,1,0,0,0,0,0,0],
    "PA": [0,0,0,1,1,0,0,0,0,0],
    "IS": [1,0,0,0,0,0,0,1,0,0],
    "ID": [0,0,0,0,0,0,1,0,0,1],
    "RB": [0,0,0,0,0,0,1,1,0,0],
    "SB": [0,0,0,0,0,0,0,1,1,0]
}
#Efecte directe de l'edat en l'entrenament
AGE_COEFF = {
    18:1.00, 19:0.95, 20:0.88, 21:0.78, 22:0.70,
    23:0.60, 24:0.51, 25:0.42, 26:0.35, 27:0.27,
    28:0.21, 29:0.16, 30:0.11, 31:0.07, 32:0.05,
    33:0.03, 34:0.02, 35:0.01,
}
#Efecte directe de l'altura
HEIGHT_COEFF = {
    175: {"JS":1,"JR":1.5,"OD":1.5,"HA":1.5,"DR":1,"PA":1,"IS":0.5,"ID":0.5,"RB":0.5,"SB":0.5},
    178: {"JS":1,"JR":1.45,"OD":1.45,"HA":1.45,"DR":1,"PA":1,"IS":0.55,"ID":0.55,"RB":0.55,"SB":0.55},
    180: {"JS":1,"JR":1.4,"OD":1.4,"HA":1.4,"DR":1,"PA":1,"IS":0.6,"ID":0.6,"RB":0.6,"SB":0.6},
    183: {"JS":1,"JR":1.35,"OD":1.35,"HA":1.35,"DR":1,"PA":1,"IS":0.65,"ID":0.65,"RB":0.65,"SB":0.65},
    185: {"JS":1,"JR":1.3,"OD":1.3,"HA":1.3,"DR":1,"PA":1,"IS":0.7,"ID":0.7,"RB":0.7,"SB":0.7},
    188: {"JS":1,"JR":1.25,"OD":1.25,"HA":1.25,"DR":1,"PA":1,"IS":0.75,"ID":0.75,"RB":0.75,"SB":0.75},
    190: {"JS":1,"JR":1.2,"OD":1.2,"HA":1.2,"DR":1,"PA":1,"IS":0.8,"ID":0.8,"RB":0.8,"SB":0.8},
    193: {"JS":1,"JR":1.15,"OD":1.15,"HA":1.15,"DR":1,"PA":1,"IS":0.85,"ID":0.85,"RB":0.85,"SB":0.85},
    196: {"JS":1,"JR":1.1,"OD":1.1,"HA":1.1,"DR":1,"PA":1,"IS":0.9,"ID":0.9,"RB":0.9,"SB":0.9},
    198: {"JS":1,"JR":1.05,"OD":1.05,"HA":1.05,"DR":1,"PA":1,"IS":0.95,"ID":0.95,"RB":0.95,"SB":0.95},
    201: {"JS":1,"JR":1,"OD":1,"HA":1,"DR":1,"PA":1,"IS":1,"ID":1,"RB":1,"SB":1},
    203: {"JS":1,"JR":0.95,"OD":0.95,"HA":0.95,"DR":1,"PA":1,"IS":1.05,"ID":1.05,"RB":1.05,"SB":1.05},
    206: {"JS":1,"JR":0.9,"OD":0.9,"HA":0.9,"DR":1,"PA":1,"IS":1.1,"ID":1.1,"RB":1.1,"SB":1.1},
    208: {"JS":1,"JR":0.85,"OD":0.85,"HA":0.85,"DR":1,"PA":1,"IS":1.15,"ID":1.15,"RB":1.15,"SB":1.15},
    211: {"JS":1,"JR":0.8,"OD":0.8,"HA":0.8,"DR":1,"PA":1,"IS":1.2,"ID":1.2,"RB":1.2,"SB":1.2},
    213: {"JS":1,"JR":0.75,"OD":0.75,"HA":0.75,"DR":1,"PA":1,"IS":1.25,"ID":1.25,"RB":1.25,"SB":1.25},
    216: {"JS":1,"JR":0.7,"OD":0.7,"HA":0.7,"DR":1,"PA":1,"IS":1.3,"ID":1.3,"RB":1.3,"SB":1.3},
    218: {"JS":1,"JR":0.65,"OD":0.65,"HA":0.65,"DR":1,"PA":1,"IS":1.35,"ID":1.35,"RB":1.35,"SB":1.35},
    221: {"JS":1,"JR":0.6,"OD":0.6,"HA":0.6,"DR":1,"PA":1,"IS":1.4,"ID":1.4,"RB":1.4,"SB":1.4},
    224: {"JS":1,"JR":0.55,"OD":0.55,"HA":0.55,"DR":1,"PA":1,"IS":1.45,"ID":1.45,"RB":1.45,"SB":1.45},
    226: {"JS":1,"JR":0.5,"OD":0.5,"HA":0.5,"DR":1,"PA":1,"IS":1.5,"ID":1.5,"RB":1.5,"SB":1.5},
    229: {"JS":1,"JR":0.45,"OD":0.45,"HA":0.45,"DR":1,"PA":1,"IS":1.55,"ID":1.55,"RB":1.55,"SB":1.55},
}
#Efecte directe de l'entrenador
COACH_COEFF = {
    7:1.06,
    6:1.03,
    5:1.00,
    4:0.97,
    3:0.94,
    2:0.91,
    1:0.88,
}


#FUNCIONS AUXILIARS
def elastic_effect(target_skill: str, current_skills: dict) -> float:
    weights = ELASTIC_EFFECT[target_skill]
    values = [current_skills[s] for s in MAIN_SKILLS]

    weighted_avg = mmult(values, weights) / sum(weights)
    exponent = current_skills[target_skill] - weighted_avg

    return 0.91 ** exponent


def cross_training(skill: str, current_skills: dict) -> float:
  max_skill = math.floor(max(current_skills.values()))

  if current_skills[skill] >= max_skill:
    exponent = (current_skills[skill] - average_skills(current_skills))
    return 0.925**exponent
  else:
    return 1


def train_skill(skills: dict, training_type: str, age: int, height: int, coach_level: int) -> dict:
    new_skills = skills.copy()

    for skill, base_coeff in COEFF[training_type].items():
      
      #Calcular cross training 
      ct = cross_training(skill, skills)
      #print(f"ct {skill} = {ct}")
      
      #Calcular elastic effect
      ee = elastic_effect(skill, skills)
      #print(f"ee {skill} = {ee}")

      #Calcular la quantitat d'entrenament
      delta = (base_coeff * HEIGHT_COEFF[height][PRIMARY_SKILL[training_type]] * AGE_COEFF[age] * COACH_COEFF[coach_level] * ee * ct)
      #print("height ", HEIGHT_COEFF[height][PRIMARY_SKILL[training_type]], "\nage ", AGE_COEFF[age],"\ncoach ", COACH_COEFF[coach_level])
      #print(f"delta {skill} = {delta}\n")
      
      new_skills[skill] += delta

    return new_skills


def average_skills(skills: dict):
  res = 0
  for skill in skills:
    if skill not in ["FT", "ST"]:
      res += skills[skill]
  return res/10


def mmult(list1: list, list2: list):
  res = 0
  for l1, l2 in zip(list1, list2):
    res += l1*l2
  return res


# FUNCIONS PRINCIPALS
def training_plan(api, playerid: str, start_week: int, training_plan: list, coach_level: int=4, bonus: dict={"JS": 0, "JR": 0, "OD": 0, "HA": 0, "DR": 0, "PA": 0, "IS": 0, "ID": 0, "RB": 0, "SB":0, "FT":0, "ST":0}):
  try:
    player = api.player_all_data(playerid)
  except Exception as e:
    return {"error": str(e)}
  
  age = player["age"]
  height = player["height"]
  week = start_week

  #Diccionari on es guardaran les habilitats després de cada entrenament
  weekly_skills = {}
  simulated = 0
  weekly_skills[simulated] = {}
  for skill, value in player["skills"].items():
    weekly_skills[simulated][skill] = value + bonus.get(skill, 0)
  #Crear la primera línia del diccionari amb les habilitats extretes de BB + les habilitats inicials que seleccioni l'usuari.
  for key in player["skills"].keys():
    weekly_skills[simulated][key] = player["skills"][key] + bonus[key]

  #Dades inicials del jugador
  print(
    f"\nName: {player['first_name']} {player['last_name']} "
    f"|| salary: {player['salary']} $ "
    f"|| pot: {player['potential']} "
    f"|| age: {player['age']} years "
    f"|| height: {player['height']} cm\n\n"
    f"Habilitats inicials: {weekly_skills[0]}\n")

  while simulated < len(training_plan):
    simulated += 1
    if week == 14:
      week = 1
      age += 1
    elif week < 14:
      week +=1
    weekly_skills[simulated] = train_skill(weekly_skills[simulated-1], training_plan[simulated-1], age, player['height'], coach_level)
    #print(f"Setmana {week}, edat {age}: ", weekly_skills[simulated], "\n")

  return weekly_skills[simulated], age, player['first_name'], player['last_name'], weekly_skills[0]


# DEBUG
if __name__ == "__main__":

  bonus = {'JS': 0.22, 'JR': 0.5, 'OD': 0.35, 'HA': 0.57, 'DR': 0.12, 'PA': 0.5, 'IS': 0.18, 'ID': 0.38, 'RB': 0.0, 'SB': 0.5, 'FT': 0.0, 'ST': 0.0}

  print(training_plan(playerid="54646103",
                      start_week=5,
                      horizon=23,
                      coach_level=4,
                      bonus=bonus))