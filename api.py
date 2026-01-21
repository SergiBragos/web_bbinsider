from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from function_shotmap import shotmap
from core.match_processor import ensure_match_processed

app = FastAPI()

app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
def index():
    return FileResponse(Path("web/index.html"))


# Permetre crides des del navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/shotmap")
def get_shotmap(match_ids: str, team: str, player: str | None = None):

    match_list = match_ids.split(",")

    for mid in match_list:
        ensure_match_processed(mid.strip(), team)

    output = "tmp/shotmap.png"

    shotmap(
        match_ids=match_list,
        team=(team,),
        player=player,
        output_path=output,
        show=False
    )

    return FileResponse(output, media_type="image/png")
