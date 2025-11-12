# mobile_responsive_pyramid-hiit-streamlit.py
import streamlit as st
import time
import json
from pathlib import Path

# Use 'wide' layout for desktop, let CSS handle mobile
st.set_page_config(page_title="Pyramid HIIT Timer", page_icon="🔥", layout="wide")

# ---------------------------
# Config load/save (Unchanged)
# ---------------------------
def load_config():
    path = Path("hiit_config.json")
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    default = {
        "work_time": 40,
        "rest_between_exercises": 15,
        "rest_between_rounds": 45,
        "peak_rest": 75,
        "exercise_sequences": {
            "Classic HIIT": ["Burpees", "Mountain Climbers", "Jump Squats", "High Knees", "Push-ups"],
            "Core Focus": ["Plank Jacks", "Russian Twists", "Bicycle Crunches", "Mountain Climbers", "Leg Raises"],
            "Cardio Blast": ["Jumping Jacks", "High Knees", "Butt Kicks", "Jump Squats", "Burpees"],
            "Strength & Power": ["Push-ups", "Squat Jumps", "Burpees", "Lunge Jumps", "Pike Push-ups"],
        },
        "exercise_images": {
            "Burpees": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/burpee-1457045324.gif?resize=1400:*",
            "Mountain Climbers": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/mountainclimber-1472061303.gif?resize=1400:*",
            "Jump Squats": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/bodyweightsquatjump-1457041758.gif?resize=1400:*",
            "High Knees": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/highkneerun-1457044203.gif?resize=1400:*",
            "Push-ups": "https://hips.hearstapps.com/hmg-prod/images/pushup-1462808858.gif?resize=1400:*",
            "Plank Jacks": "https://media.giphy.com/media/l378AEZceMNl1JTfW/giphy.gif",
            "Russian Twists": "https://media.giphy.com/media/1qfDuQzxKWaq4cjBVJ/giphy.gif",
            "Bicycle Crunches": "https://media.giphy.com/media/26FPpSuhgHvYo9Kyk/giphy.gif",
            "Leg Raises": "https://media.giphy.com/media/3o7TKqnN349PBUtGFO/giphy.gif",
            "Jumping Jacks": "https://media.giphy.com/media/3oEduWFBrKjvf9DFiE/giphy.gif",
            "Butt Kicks": "https://media.giphy.com/media/l0HlHcuzAjhMQ2m0U/giphy.gif",
            "Squat Jumps": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/bodyweightsquatjump-1457041758.gif?resize=1400:*",
            "Lunge Jumps": "https://tenor.com/view/afundo-gif-12659523759178076149.gif",
            "Pike Push-ups": "https://media.giphy.com/media/3o7TKqnN349PBUtGFO/giphy.gif",
        },
    }
    save_config(default)
    return default

def save_config(cfg):
    path = Path("hiit_config.json")
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)

# ---------------------------
# Session state defaults (Unchanged)
# ---------------------------
if "config" not in st.session_state:
    st.session_state.config = load_config()
if "workout_started" not in st.session_state:
    st.session_state.workout_started = False
if "round" not in st.session_state:
    st.session_state.round = 1
if "exercise_index" not in st.session_state:
    st.session_state.exercise_index = 0
if "selected_sequence" not in st.session_state:
    st.session_state.selected_sequence = "Classic HIIT"

# ---------------------------
# Styles (ADJUSTED FOR RESPONSIVENESS)
# ---------------------------
st.markdown("""
<style>
/* Default styles for larger screens (compact layout) */
.big-timer {
    font-size: 80px;
    font-weight: bold;
    text-align: center;
    padding: 20px; 
    border-radius: 15px;
    margin: 10px 0;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.exercise-name {
    font-size: 36px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
}
.exercise-gif { 
    max-width: 100%;
    max-height: 350px; 
    object-fit: contain; 
    margin: auto;
    display: block;
}
.gif-blank    { height: 350px; }

/* Mobile-Specific Styles: Shrink everything for screens <= 600px */
@media (max-width: 600px) {
    .big-timer {
        font-size: 50px; /* Smaller font on mobile */
        height: 150px;  /* Smaller box height on mobile */
    }
    .exercise-name {
        font-size: 24px; /* Smaller exercise name */
    }
    .exercise-gif { 
        max-height: 200px; /* Smaller GIF height */
    }
    .gif-blank {
        height: 200px; /* Match placeholder height */
    }
}

/* Color and general styles (Unchanged) */
.work-phase {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
}
.rest-phase {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
}
.phase-labels {
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    margin: 5px 0 15px 0;
}
.label-active { opacity: 1;   transition: opacity 0.4s ease; }
.label-faded  { opacity: 0.2; transition: opacity 0.4s ease; }

.pyramid-progress {
    text-align: center;
    font-size: 11px;
    margin-top: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.round-item { display: inline-block; margin: 0 5px; padding: 4px 6px; border-radius: 4px; }
.round-completed { color: #9ca3af; opacity: 0.5; }
.round-current   { background-color: #10b981; color: white; font-weight: bold; }
.round-upcoming  { color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Pyramid order helpers (Unchanged)
# ---------------------------
PYRAMID_LABELS = ["1", "1-2", "1-2-3", "1-2-3-4", "1-2-3-4-5", "5-4-3-2", "5-4-3", "5-4", "5"]
PYRAMID_INDICES = [
    [1],
    [1,2],
    [1,2,3],
    [1,2,3,4],
    [1,2,3,4,5],
    [5,4,3,2],
    [5,4,3],
    [5,4],
    [5],
]

def round_exercises(round_num, full_list):
    idxs = PYRAMID_INDICES[round_num - 1]
    return [full_list[i-1] for i in idxs]

# ---------------------------
# UI screens (Button fix applied)
# ---------------------------
def show_setup_screen():
    st.title("🔥 Pyramid HIIT Timer")
    st.markdown("### Configure Your Workout")

    c1, c2 = st.columns([2,1])
    with c1:
        keys = list(st.session_state.config["exercise_sequences"].keys())
        sel = st.selectbox("Choose a sequence:", keys, index=keys.index(st.session_state.selected_sequence) if st.session_state.selected_sequence in keys else 0)
        st.session_state.selected_sequence = sel
        exercises = st.session_state.config["exercise_sequences"][sel]
        st.markdown("**Exercises:**")
        for i, ex in enumerate(exercises, 1):
            st.write(f"{i}. {ex}")
        st.markdown("---")
        st.info("Pyramid: 1 → 1-2 → 1-2-3 → 1-2-3-4 → 1-2-3-4-5 → 5-4-3-2 → 5-4-3 → 5-4 → 5")

    with c2:
        cfg = st.session_state.config
        cfg["work_time"] = st.number_input("Work (s)", 10, 120, cfg["work_time"])
        cfg["rest_between_exercises"] = st.number_input("Rest Between Exercises (s)", 5, 60, cfg["rest_between_exercises"])
        cfg["rest_between_rounds"] = st.number_input("Rest Between Rounds (s)", 10, 120, cfg["rest_between_rounds"])
        cfg["peak_rest"] = st.number_input("Peak Rest (s)", 30, 180, cfg["peak_rest"])

    st.markdown("---")
    
    # Button fix: Ensures the button is not drawn in the subsequent cycle
    if st.button("🚀 START WORKOUT", type="primary"):
        st.session_state.workout_started = True
        st.session_state.round = 1
        st.session_state.exercise_index = 0
        save_config(st.session_state.config)
        st.rerun()
        return # Important: Exits the function immediately after rerun is called.

def show_pyramid_progress():
    current = st.session_state.round - 1 
    html = "<div class='pyramid-progress'>"
    for i, label in enumerate(PYRAMID_LABELS):
        cls = "round-current" if i == current else "round-completed" if i < current else "round-upcoming"
        html += f"<span class='round-item {cls}'>{label}</span>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def show_workout_screen():
    cfg = st.session_state.config
    exercises = cfg["exercise_sequences"][st.session_state.selected_sequence]
    total_rounds = 9

    # Determine current exercise list for this round
    curr_list = round_exercises(st.session_state.round, exercises)
    st.session_state.exercise_index = min(st.session_state.exercise_index, len(curr_list) - 1)
    current_exercise = curr_list[st.session_state.exercise_index]

    # --- Sidebar: show all exercises and highlight by NAME (Unchanged)
    with st.sidebar:
        st.markdown("### 🏋️ Exercises")
        for i, ex in enumerate(exercises, 1):
            prefix = "➡️ " if ex == current_exercise else ""
            st.markdown(f"{prefix}{i}. **{ex}**")
        st.markdown("---")
        st.markdown("### 🧱 Pyramid Progress")
        show_pyramid_progress()

    # Header + progress (Unchanged)
    st.markdown(f"### Round {st.session_state.round} of {total_rounds}")
    st.progress((st.session_state.round - 1) / total_rounds)

    # Placeholders for dynamic content
    labels_ph = st.empty()

    # Layout: GIF/Exercise Name (2/3) | Timer (1/3) (Layout is responsive due to CSS)
    gif_col, timer_col = st.columns([2, 1])
    
    # Placeholders inside columns
    with gif_col:
        gif_ph_name = st.empty()
        gif_ph = st.empty()
            
    with timer_col:
        timer_ph = st.empty()


    # -------------------------
    # WORK PHASE
    # -------------------------
    labels_ph.markdown(
        "<div class='phase-labels'><span class='label-active'>⚡ WORK</span> | <span class='label-faded'>REST 😮‍💨</span></div>",
        unsafe_allow_html=True
    )
    
    # Show Exercise Name and GIF only during work
    gif_ph_name.markdown(f"<div class='exercise-name'>💪 {current_exercise}</div>", unsafe_allow_html=True)
    if current_exercise in cfg["exercise_images"]:
        gif_ph.markdown(
            f"<img src='{cfg['exercise_images'][current_exercise]}' class='exercise-gif'/>",
            unsafe_allow_html=True
        )
    else:
        gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)
            

    for t in range(cfg["work_time"], 0, -1):
        timer_ph.markdown(f"<div class='big-timer work-phase'>{t}</div>", unsafe_allow_html=True)
        time.sleep(1)

    # Move to next exercise in this round
    st.session_state.exercise_index += 1

    # -------------------------
    # REST PHASE (between exercises or between rounds/peak)
    # -------------------------
    # Update labels
    labels_ph.markdown(
        "<div class='phase-labels'><span class='label-faded'>⚡ WORK</span> | <span class='label-active'>REST 😮‍💨</span></div>",
        unsafe_allow_html=True
    )
    
    # Clear GIF column content for rest
    gif_ph_name.markdown("<div class='exercise-name'></div>", unsafe_allow_html=True)
    gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)


    if st.session_state.exercise_index < len(curr_list):
        # Rest between exercises
        next_exercise = curr_list[st.session_state.exercise_index]
        gif_ph_name.markdown(f"<div class='exercise-name'>NEXT: {next_exercise}</div>", unsafe_allow_html=True)
        for t in range(cfg["rest_between_exercises"], 0, -1):
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.rerun()
    else:
        # Finished the round — decide what rest to do
        st.session_state.exercise_index = 0

        # Peak rest after round 5 (Pyramid Peak)
        if st.session_state.round == 5:
            gif_ph_name.markdown("<div class='exercise-name'>PEAK REST ⛰️</div>", unsafe_allow_html=True)
            for t in range(cfg["peak_rest"], 0, -1):
                timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
                time.sleep(1)
            # Advance to next round
            st.session_state.round += 1
            st.rerun()

        # Workout complete after round 9
        elif st.session_state.round == 9:
            st.balloons()
            st.success("🎉 WORKOUT COMPLETE! Amazing job!")
            if st.button("Back to Setup"):
                st.session_state.workout_started = False
                st.rerun()
            return # Exit function for final screen
        
        # Regular rest between rounds
        else:
            gif_ph_name.markdown(f"<div class='exercise-name'>REST BETWEEN ROUNDS</div>", unsafe_allow_html=True)
            for t in range(cfg["rest_between_rounds"], 0, -1):
                timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
                time.sleep(1)
            # Advance to next round
            st.session_state.round += 1
            st.rerun()

# ---------------------------
# Entrypoint (Unchanged)
# ---------------------------
def main():
    if not st.session_state.workout_started:
        show_setup_screen()
    else:
        show_workout_screen()

if __name__ == "__main__":
    main()