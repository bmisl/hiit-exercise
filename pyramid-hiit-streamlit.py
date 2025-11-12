import streamlit as st
import time
import json
from pathlib import Path

# Use 'wide' layout for desktop, let CSS handle mobile
st.set_page_config(page_title="Pyramid HIIT Timer", page_icon="🔥", layout="wide")

# ---------------------------
# Config load/save (UNCHANGED)
# ---------------------------
def load_config():
    # Helper to load default config if file doesn't exist
    path = Path("hiit_config.json")
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    default = {
        "work_time": 40, "rest_between_exercises": 15, "rest_between_rounds": 45, "peak_rest": 75,
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
            "Stepup": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/stepup-1457044957.gif?resize=1400:*", 
            "Jumping Jacks": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/jumpingjack-1457045563.gif?resize=1400:*",
            "Squat Jumps": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/bodyweightsquatjump-1457041758.gif?resize=1400:*",
            "Y Superman": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/supermany-1472154643.gif",
            "Twisting Situp": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/situptwisting-1472152218.gif?resize=1400:*",
            "Russian Twists": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/russiantwistfeetraised-1472133891.gif?resize=1400:*",
            "Russian Twists2": "https://media4.giphy.com/media/cpKD9u3S25xYL8tcbr/giphy.gif",
            "V Ups": "https://media1.popsugar-assets.com/files/thumbor/wclUn2vpiB8j1l9Sry5XL35SyLs/fit-in/2048xorig/filters:format_auto-!!-:strip_icc-!!-/2017/06/05/906/n/1922729/4a427ce25102cba0_V-Ups.gif",
            "Hollow hold": "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/workouts/2016/03/lyinghollowbodyhold-1457044774.gif?crop=1xw:1xh;center,top&resize=480:*",
            "Hanging Leg Raises": "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/workouts/2017/05/hanginglegraise-1496161341.gif",
            "Plank": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/plank-1457045584.gif?resize=1400:*",
            "Plank Jacks": "https://media1.popsugar-assets.com/files/thumbor/E5X9t2h9kSYqGlWEe1zxtvusMOY/fit-in/2048xorig/filters:format_auto-!!-:strip_icc-!!-/2016/05/10/225/n/1922729/e95be01486710f18_8a0b7913bd7d4ec3_PlankJack/i/Plank-Jack.gif",
            "Bicycle Crunches": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/bicycle-1472058017.gif?resize=980:*",
            "Crunches": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/crunch-1457102356.gif?crop=1xw:0.75xh;center,top&resize=1200:*",
            "Bent Leg Raises": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/legraise-1472054568.gif?resize=640:*",
            "Leg Raises": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/legraisesinglelegalternating-1472061028.gif?crop=1xw:0.75xh;center,top&resize=1200:*",
            "Standing Leg Raises": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/standinglegraise-1457044676.gif?crop=1xw:1xh;center,top&resize=1200:*",
            "T Superman": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/08/supermant-1472154358.gif?resize=1400:*",
            "Lunge Split Squat With Kettlebell": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/dumbbellbulgariangobletsplitsquat-1457046602.gif",
            "Lunge Jumps": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/splitjump-1457044565.gif", 
            "Lunge": "https://media.tenor.com/-YiEMDDCOwoAAAAM/afundo.gif", 
            "Butt Kicks": "https://spotebi.com/wp-content/uploads/2015/01/butt-kicks-exercise-illustration-spotebi.gif",
            "Pike Push-ups": "https://hips.hearstapps.com/hmg-prod/images/workouts/2016/03/pikepushup-1456956895.gif?crop=1xw:1xh;center,top&resize=1200:*",
        },
    }
    try:
        save_config(default) 
    except:
        pass
    return default

def save_config(cfg):
    path = Path("hiit_config.json")
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)

# ---------------------------
# TIME CALCULATION HELPERS (UNCHANGED)
# ---------------------------
def calculate_total_time(cfg):
    """Calculates the total duration of the workout in seconds."""
    W = cfg["work_time"]
    RE = cfg["rest_between_exercises"]
    RR = cfg["rest_between_rounds"]
    RP = cfg["peak_rest"]
    
    # Pyramid structure: [1, 2, 3, 4, 5, 4, 3, 2, 1]
    total_work_intervals = 25
    total_rest_between_exercise_intervals = 16 
    total_rest_between_round_intervals = 7 
    total_peak_rest_intervals = 1 

    total_time = (total_work_intervals * W) + \
                 (total_rest_between_exercise_intervals * RE) + \
                 (total_rest_between_round_intervals * RR) + \
                 (total_peak_rest_intervals * RP)
    return total_time

def format_time(seconds):
    """Formats seconds into MM:SS format."""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

# ---------------------------
# Session state defaults (UNCHANGED)
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
if "total_time_seconds" not in st.session_state:
    st.session_state.total_time_seconds = 0
if "elapsed_time_seconds" not in st.session_state:
    st.session_state.elapsed_time_seconds = 0
    
# ---------------------------
# Styles (UNCHANGED)
# ---------------------------
st.markdown("""
<style>
/* Sidebar Transparency (70%) */
[data-testid="stSidebar"] {
    background-color: rgba(240, 242, 246, 0.7); 
}

.top-timer {
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: #fff;
    border-bottom: 2px solid #ddd;
    padding: 2px 4px;
}

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
        font-size: 50px; 
        height: 150px; 
    }
    .exercise-name {
        font-size: 24px;
    }
    .exercise-gif { 
        max-height: 200px; 
    }
    .gif-blank {
        height: 200px; 
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
            

/* Remove Streamlit’s default top divider / padding */
section.main > div:first-child {
    border-top: none !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
}
[data-testid="stAppViewBlockContainer"] {
    border-top: none !important;
    box-shadow: none !important;
}

/* Small thumbnails in setup view */
img {
    border-radius: 6px;
}



</style>
""", unsafe_allow_html=True)

# ---------------------------
# Pyramid order helpers (UNCHANGED)
# ---------------------------
PYRAMID_LABELS = ["1", "1-2", "1-2-3", "1-2-3-4", "1-2-3-4-5", "5-4-3-2", "5-4-3", "5-4", "5"]
PYRAMID_INDICES = [
    [1], [1,2], [1,2,3], [1,2,3,4], [1,2,3,4,5], 
    [5,4,3,2], [5,4,3], [5,4], [5],
]

def round_exercises(round_num, full_list):
    idxs = PYRAMID_INDICES[round_num - 1]
    return [full_list[i-1] for i in idxs]

# ---------------------------
# UI screens
# ---------------------------
def show_setup_screen():
    st.title("🔥 Pyramid HIIT Timer")
    st.markdown("### Configure Your Workout")

    c1, c2 = st.columns([2,1])
    with c1:
        keys = list(st.session_state.config["exercise_sequences"].keys())
        sel = st.selectbox("Choose a sequence:", keys, index=keys.index(st.session_state.selected_sequence))
        st.session_state.selected_sequence = sel
        exercises = st.session_state.config["exercise_sequences"][sel]
        images = st.session_state.config["exercise_images"]

        # Visual layout for thumbnails
        st.markdown("### Exercises Preview")
        cols = st.columns(len(exercises))

        for i, ex in enumerate(exercises):
            img_url = images.get(ex)
            with cols[i]:
                if img_url:
                    st.markdown(
                        f"""
                        <div style="text-align:center">
                            <img src="{img_url}" style="width:100%; border-radius:8px; max-height:100px; object-fit:cover;"/>
                            <div style="font-size:12px; margin-top:4px;">{ex}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"<div style='text-align:center; font-size:12px;'>{ex}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.info("Pyramid: 1 → 1-2 → 1-2-3 → 1-2-3-4 → 1-2-3-4-5 → 5-4-3-2 → 5-4-3 → 5-4 → 5")

    with c2:
        cfg = st.session_state.config
        cfg["work_time"] = st.number_input("Work (s)", 10, 120, cfg["work_time"])
        cfg["rest_between_exercises"] = st.number_input("Rest Between Exercises (s)", 5, 60, cfg["rest_between_exercises"])
        cfg["rest_between_rounds"] = st.number_input("Rest Between Rounds (s)", 10, 120, cfg["rest_between_rounds"])
        cfg["peak_rest"] = st.number_input("Peak Rest (s)", 30, 180, cfg["peak_rest"])

    st.markdown("---")
    
    if st.button("🚀 START WORKOUT", type="primary"):
        st.session_state.workout_started = True
        st.session_state.round = 1
        st.session_state.exercise_index = 0
        st.session_state.elapsed_time_seconds = 0
        
        # Calculate and store total time
        st.session_state.total_time_seconds = calculate_total_time(cfg) 
        
        save_config(st.session_state.config)
        # RERUN is called, but the function still finishes, 
        # which can cause rendering issues. We rely on the main function 
        # logic below to block further setup rendering.
        st.rerun() 
        st.stop
        return 

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
    
    # Determine current exercise list for this round
    curr_list = round_exercises(st.session_state.round, exercises)
    st.session_state.exercise_index = min(st.session_state.exercise_index, len(curr_list) - 1)
    current_exercise = curr_list[st.session_state.exercise_index]
    
    # Get Time Variables
    total_time_str = format_time(st.session_state.total_time_seconds)
    elapsed_time_sec = st.session_state.elapsed_time_seconds
    
    # --- Sidebar: show all exercises and highlight by NAME
    with st.sidebar:
        st.markdown("### 🏋️ Exercises")
        for i, ex in enumerate(exercises, 1):
            prefix = "➡️ " if ex == current_exercise else ""
            st.markdown(f"{prefix}{i}. **{ex}**")
        st.markdown("---")
        st.markdown("### 🧱 Pyramid Progress")
        show_pyramid_progress()

    # --- Sticky top timer ---
    st.markdown("<div class='top-timer'>", unsafe_allow_html=True)
    progress_text = st.empty()
    progress_bar = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

    # Phase labels (WORK / REST)
    labels_ph = st.empty()

    # Layout: GIF/Exercise Name (2/3) | Timer (1/3)
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
    
    gif_ph_name.markdown(f"<div class='exercise-name'>💪 {current_exercise}</div>", unsafe_allow_html=True)
    if current_exercise in cfg["exercise_images"]:
        gif_ph.markdown(
            f"<img src='{cfg['exercise_images'][current_exercise]}' class='exercise-gif'/>",
            unsafe_allow_html=True
        )
    else:
        gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)
            
    work_time_duration = cfg["work_time"]
    for t in range(work_time_duration, 0, -1):
        # Update elapsed time display based on current countdown value
        current_elapsed = elapsed_time_sec + (work_time_duration - t) 
        # Display Time Progress
        progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
        progress_bar.progress(current_elapsed / st.session_state.total_time_seconds)
        timer_ph.markdown(f"<div class='big-timer work-phase'>{t}</div>", unsafe_allow_html=True)
        time.sleep(1)

    # Increment elapsed time by the phase duration
    st.session_state.elapsed_time_seconds += work_time_duration

    # Move to next exercise in this round
    st.session_state.exercise_index += 1

    # -------------------------
    # REST PHASE
    # -------------------------
    labels_ph.markdown(
        "<div class='phase-labels'><span class='label-faded'>⚡ WORK</span> | <span class='label-active'>REST 😮‍💨</span></div>",
        unsafe_allow_html=True
    )
    
    gif_ph_name.markdown("<div class='exercise-name'></div>", unsafe_allow_html=True)
    gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)

    current_round = st.session_state.round

    if st.session_state.exercise_index < len(curr_list):
        # Rest between exercises
        next_exercise = curr_list[st.session_state.exercise_index]
        gif_ph_name.markdown(f"<div class='exercise-name'>NEXT: {next_exercise}</div>", unsafe_allow_html=True)
        rest_duration = cfg["rest_between_exercises"]
        for t in range(rest_duration, 0, -1):
            current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
            progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
            progress_bar.progress(current_elapsed / st.session_state.total_time_seconds)
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.session_state.elapsed_time_seconds += rest_duration
        st.rerun()
    else:
        # Finished the round — decide what rest to do
        st.session_state.exercise_index = 0
        
        # Peak rest after round 5 (Pyramid Peak)
        if current_round == 5:
            # Show round count here
            gif_ph_name.markdown(f"<div class='exercise-name'>PEAK REST ⛰️: Round {current_round} of 9</div>", unsafe_allow_html=True)
            rest_duration = cfg["peak_rest"]
            for t in range(rest_duration, 0, -1):
                current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
                progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
                progress_bar.progress(current_elapsed / st.session_state.total_time_seconds)
                timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
                time.sleep(1)
            
            st.session_state.elapsed_time_seconds += rest_duration
            st.session_state.round += 1
            st.rerun()

        # Workout complete after round 9
        elif current_round == 9:
            st.balloons()
            st.success("🎉 WORKOUT COMPLETE! Amazing job!")
            # Final time update
            progress_ph.markdown(f"### Total Workout Time: **{total_time_str}**") 
            progress_ph.progress(1.0)
            if st.button("Back to Setup"):
                st.session_state.workout_started = False
                st.session_state.elapsed_time_seconds = 0
                st.rerun()
            return 
        
        # Regular rest between rounds
        else:
            # Show round count here
            gif_ph_name.markdown(f"<div class='exercise-name'>REST BETWEEN ROUNDS: Round {current_round} of 9</div>", unsafe_allow_html=True)
            rest_duration = cfg["rest_between_rounds"]
            for t in range(rest_duration, 0, -1):
                current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
                progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
                progress_bar.progress(current_elapsed / st.session_state.total_time_seconds)
                timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
                time.sleep(1)
            
            st.session_state.elapsed_time_seconds += rest_duration
            st.session_state.round += 1
            st.rerun()

# ---------------------------
# Entrypoint (FIXED)
# ---------------------------
def main():
    # FIX: Ensure setup screen does not render if workout has started, 
    # preventing the ghosting effect (Issue B).
    if st.session_state.workout_started:
        show_workout_screen()
        return

    # If the workout hasn't started, show the setup screen.
    show_setup_screen()

if __name__ == "__main__":
    main()