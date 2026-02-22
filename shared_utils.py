import json
from pathlib import Path

STRETCHING_GIFS = [
    "exercises/stretch_child_pose.gif",
    "exercises/stretch_lunge_stretch.gif",
    "exercises/stretch_tricep_stretch.gif",
    "exercises/stretch_shoulder_stretch.gif",
    "exercises/stretch_quad_stretch.gif",
    "exercises/stretch_hip_stretch.gif",
    "exercises/stretch_hamstring_stretch.gif",
    "exercises/stretch_glute_stretch.gif"
]

def load_config():
    path = Path("hiit_config.json")
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg):
    path = Path("hiit_config.json")
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)

def format_time(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def calculate_total_time(cfg):
    W = cfg.get("work_time", 30)
    RE = cfg.get("rest_between_exercises", 45)
    RR = cfg.get("rest_between_rounds", 60)
    RP = cfg.get("peak_rest", 75)
    
    total_work_intervals = 25
    total_rest_between_exercise_intervals = 16 
    total_rest_between_round_intervals = 7 
    total_peak_rest_intervals = 1 

    total_time = (total_work_intervals * W) + \
                 (total_rest_between_exercise_intervals * RE) + \
                 (total_rest_between_round_intervals * RR) + \
                 (total_peak_rest_intervals * RP) + 10 # 10s initial countdown
    return total_time
