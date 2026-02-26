# api.py

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import xml.etree.ElementTree as xml
from pathlib import Path
from function_shotmap import shotmap
from training import training_plan
from core.match_processor import ensure_match_processed
from bbapi import BBApi
from core.progress_store import (init_match, update_match, finish_match, get_global_progress)
from typing import Dict
import os

#Crear l'app i enviar-li les credencials de l'usuari
app = FastAPI()
BB_USER = os.environ["BB_USER"]
BB_PASSWORD = os.environ["BB_PASSWORD"]
bbapi = BBApi(BB_USER, BB_PASSWORD)
app.mount("/web", StaticFiles(directory="web"), name="web")


@app.get("/")
def index():
    return FileResponse(Path("web/index.html"))


# Permetre crides des del navegador
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"],)

# When the submit button is pressed, the HTML form is intercepted by JavaScript.
# The JavaScript code manually builds a URL (e.g. /shotmap?match_ids=...&team=...)
# and triggers a GET request to that endpoint.
#
# Because the request is sent to /shotmap, this FastAPI route is executed.
# If another button or action is needed (e.g. rebounds, assists),
# a different endpoint must be created (e.g. /rebounds) and called explicitly
# from JavaScript.
@app.get("/shotmap")
def get_shotmap(match_ids: str, team: str, show_individual_shots: bool = False, player: str | None = None):

    match_list = match_ids.split(",")

    for mid in match_list:
        ensure_match_processed(mid.strip(), team)

    output = Path("tmp")
    output.mkdir(exist_ok=True)

    zone_stats, assisted = shotmap(match_ids=match_list, team=team, player=player, output_path=output, show_individual_shots=show_individual_shots, show=False)

    return FileResponse(output/"shotmap.png", media_type="image/png")

@app.get("/assisted")
def get_assisted(match_ids: str,team: str,player: str | None = None):

    match_list = match_ids.split(",")

    for mid in match_list:
        ensure_match_processed(mid.strip(), team)

    zone_stats, assisted = shotmap(match_ids=match_list,team=team,player=player,show=False)

    return assisted


@app.get("/progress_batch")
def progress_batch(match_ids: str):
    ids = [m.strip() for m in match_ids.split(",") if m.strip()]
    return get_global_progress(ids)



@app.get("/api/schedule")
def api_schedule(teamid: str = Query(...), season: str = Query(...)):
    xml_text = bbapi.get_xml_schedule(teamid, season)
    root = xml.fromstring(xml_text)
    matches = []

    for m in root.findall("./schedule/match"):
        matches.append({
            "match_id": m.attrib["id"],
            "type": m.attrib.get("type", "unknown"),
            "date": m.attrib.get("start")
        })

    return matches


@app.get("/training")
def training(
    player_id: str = Query(...),
    coach_level: int = Query(...),
    current_week: int = Query(...),
    plan: str = Query(...)
):
    training_list = plan.split("|")

    result, age, name, surname, initial_skills = training_plan(
        playerid=player_id,
        start_week=current_week,
        training_plan=training_list,
        coach_level=coach_level
    )

    return {
        "player_id": player_id,
        "name": name,
        "surname": surname,
        "age_at_end": age,
        "coach_level": coach_level,
        "start_week": current_week,
        "weeks": len(training_list),
        "skills_by_week": result,
        "initial_skills": initial_skills
    }