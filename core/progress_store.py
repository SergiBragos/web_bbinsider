# core/progress_store.py

# Estat global del progrés dels partits
MATCH_PROGRESS = {}


def init_match(matchid: str):
    MATCH_PROGRESS[matchid] = {
        "progress": 0,
        "status": "processing"
    }


def update_match(matchid: str, progress: int):
    MATCH_PROGRESS[matchid] = {
        "progress": progress,
        "status": "processing"
    }


def finish_match(matchid: str, status: str = "done"):
    MATCH_PROGRESS[matchid] = {
        "progress": 100,
        "status": status
    }


def get_match_progress(matchid: str):
    return MATCH_PROGRESS.get(matchid,{"progress": 0, "status": "processing"})


def is_match_done(matchid: str) -> bool:
    return get_match_progress(matchid)["progress"] >= 100


def get_global_progress(match_ids: list[str]):
    if not match_ids:
        return {"done": 0, "total": 0, "percent": 0}

    done = 0
    for m in match_ids:
        info = MATCH_PROGRESS.get(m)
        if info and info["progress"] >= 100:
            done += 1

    total = len(match_ids)

    return {
        "done": done,
        "total": total,
        "percent": int(done / total * 100)
    }
