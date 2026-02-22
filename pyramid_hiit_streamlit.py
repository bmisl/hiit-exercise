import streamlit as st
import time
import json
import random
from pathlib import Path
from shared_utils import STRETCHING_GIFS, load_config, save_config, calculate_total_time, format_time

# ---------------------------
# Session state defaults
# ---------------------------
def init_hiit_session():
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
/* Sidebar Transparency (40%) */
[data-testid="stSidebar"] {
    background-color: rgba(240, 242, 246, 0.4); 
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
        cfg["work_time"] = st.number_input("Work (s)", 15, 120, cfg["work_time"], step=5)
        cfg["rest_between_exercises"] = st.number_input("Rest Between Exercises (s)", 5, 60, cfg["rest_between_exercises"], step=5)
        cfg["rest_between_rounds"] = st.number_input("Rest Between Rounds (s)", 10, 120, cfg["rest_between_rounds"], step=5)
        cfg["peak_rest"] = st.number_input("Peak Rest (s)", 30, 180, cfg["peak_rest"], step=5)

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

    # --- Define all placeholders early so they always exist ---
    progress_ph = st.empty()        # for total workout time at completion
    progress_text = st.empty()      # for live elapsed time text
    progress_bar = st.empty()       # for live progress bar
    labels_ph = st.empty()          # for WORK / REST labels

    # Layout columns for main area
    gif_col, timer_col = st.columns([2, 1])
    with gif_col:
        gif_ph_name = st.empty()
        gif_ph = st.empty()
    with timer_col:
        timer_ph = st.empty()

    # --- Determine current exercise and list for this round ---
    curr_list = round_exercises(st.session_state.round, exercises)
    st.session_state.exercise_index = min(
        st.session_state.exercise_index, len(curr_list) - 1
    )
    current_exercise = curr_list[st.session_state.exercise_index]

    # --- Sidebar: show all exercises and pyramid ---
    with st.sidebar:
        st.markdown("### 🏋️ Exercises")
        for i, ex in enumerate(exercises, 1):
            prefix = "➡️ " if ex == current_exercise else ""
            st.markdown(f"{prefix}{i}. **{ex}**")
        st.markdown("---")
        st.markdown("### 🧱 Pyramid Progress")
        show_pyramid_progress()

    # --- Timer values ---
    total_time_str = format_time(st.session_state.total_time_seconds)
    elapsed_time_sec = st.session_state.elapsed_time_seconds
    current_round = st.session_state.round

    # -------------------------
    # INITIAL PREPARATION (10s)
    # -------------------------
    if st.session_state.elapsed_time_seconds == 0:
        labels_ph.markdown(
            "<div class='phase-labels'><span class='label-active'>🚀 PREPARE</span></div>",
            unsafe_allow_html=True,
        )
        gif_ph_name.markdown(f"<div class='exercise-name'>GET READY!</div>", unsafe_allow_html=True)
        img_url = cfg["exercise_images"].get(current_exercise)
        if img_url:
            gif_ph.markdown(f"<img src='{img_url}' class='exercise-gif'/>", unsafe_allow_html=True)
        
        for t in range(10, 0, -1):
            elapsed = 10 - t
            progress_text.markdown(f"### ⏱ {format_time(elapsed)} / {total_time_str}")
            progress_val = min(1.0, elapsed / st.session_state.total_time_seconds)
            progress_bar.progress(progress_val)
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.session_state.elapsed_time_seconds = 10

    # -------------------------
    # WORK PHASE
    # -------------------------
    labels_ph.markdown(
        "<div class='phase-labels'><span class='label-active'>⚡ WORK</span> | "
        "<span class='label-faded'>REST 😮‍💨</span></div>",
        unsafe_allow_html=True,
    )
    gif_ph_name.markdown(f"<div class='exercise-name'>💪 {current_exercise}</div>", unsafe_allow_html=True)

    img_url = cfg["exercise_images"].get(current_exercise)
    if img_url:
        gif_ph.markdown(f"<img src='{img_url}' class='exercise-gif'/>", unsafe_allow_html=True)
    else:
        gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)

    work_time = cfg["work_time"]
    for t in range(work_time, 0, -1):
        current_elapsed = st.session_state.elapsed_time_seconds + (work_time - t)
        progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
        progress_value = min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds))
        progress_bar.progress(progress_value)
        timer_ph.markdown(f"<div class='big-timer work-phase'>{t}</div>", unsafe_allow_html=True)
        time.sleep(1)

    st.session_state.elapsed_time_seconds += work_time
    st.session_state.exercise_index += 1

    # -------------------------
    # REST PHASE
    # -------------------------
    labels_ph.markdown(
        "<div class='phase-labels'><span class='label-faded'>⚡ WORK</span> | "
        "<span class='label-active'>REST 😮‍💨</span></div>",
        unsafe_allow_html=True,
    )
    gif_ph.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)

    # Rest between exercises
    if st.session_state.exercise_index < len(curr_list):
        next_exercise = curr_list[st.session_state.exercise_index]
        gif_ph_name.markdown(f"<div class='exercise-name'>NEXT: {next_exercise}</div>", unsafe_allow_html=True)
        rest_duration = cfg["rest_between_exercises"]

        for t in range(rest_duration, 0, -1):
            # Show/Change stretching GIF every 15 seconds
            if t == rest_duration or t % 15 == 0:
                gif_ph.markdown(f"<img src='{random.choice(STRETCHING_GIFS)}' class='exercise-gif'/>", unsafe_allow_html=True)

            current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
            progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
            progress_value = min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds))
            progress_bar.progress(progress_value)
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)

        st.session_state.elapsed_time_seconds += rest_duration
        st.rerun()

    # Finished the round
    st.session_state.exercise_index = 0

    # Peak rest after round 5
    if current_round == 5:
        gif_ph_name.markdown(
            f"<div class='exercise-name'>PEAK REST ⛰️: Round {current_round} of 9</div>",
            unsafe_allow_html=True,
        )
        rest_duration = cfg["peak_rest"]

    # Workout complete after round 9
    elif current_round == 9:
        st.balloons()
        st.success("🎉 WORKOUT COMPLETE! Amazing job!")

        total_time_str = format_time(st.session_state.total_time_seconds)
        progress_ph.markdown(f"### Total Workout Time: **{total_time_str}**")
        st.progress(1.0)

        if st.button("Back to Setup"):
            st.session_state.workout_started = False
            st.session_state.elapsed_time_seconds = 0
            st.session_state.phase = "setup"
            st.rerun()
        return "complete"

    # Regular rest between rounds
    else:
        gif_ph_name.markdown(
            f"<div class='exercise-name'>REST BETWEEN ROUNDS: Round {current_round} of 9</div>",
            unsafe_allow_html=True,
        )
        rest_duration = cfg["rest_between_rounds"]

    # Run the appropriate rest timer (peak or regular)
    for t in range(rest_duration, 0, -1):
        # Show/Change stretching GIF every 15 seconds
        if t == rest_duration or t % 15 == 0:
            gif_ph.markdown(f"<img src='{random.choice(STRETCHING_GIFS)}' class='exercise-gif'/>", unsafe_allow_html=True)

        current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
        progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
        progress_value = min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds))
        progress_bar.progress(progress_value)
        timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
        time.sleep(1)

    st.session_state.elapsed_time_seconds += rest_duration
    st.session_state.round += 1
    st.rerun()
    return "active"


# ---------------------------
# Entrypoint (FIXED)
# ---------------------------
def main():
    init_hiit_session()
    # FIX: Ensure setup screen does not render if workout has started, 
    # preventing the ghosting effect (Issue B).
    if st.session_state.workout_started:
        return show_workout_screen()

    # If the workout hasn't started, show the setup screen.
    show_setup_screen()
    return "active"

if __name__ == "__main__":
    st.set_page_config(page_title="Pyramid HIIT Timer", page_icon="🔥", layout="wide")
    main()