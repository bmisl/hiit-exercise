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
# Styles
# ---------------------------
def inject_hiit_css():
    st.markdown("""
    <style>
    /* Sidebar Transparency (40%) */
    [data-testid="stSidebar"] {
        background-color: rgba(220, 220, 220, 0.95); 
        color: black !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: black !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: black !important;
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
    /* Standardize image height in workout screen */
    [data-testid="stColumn"]:nth-of-type(1) img {
        max-height: 400px !important;
        width: auto !important;
        object-fit: contain !important;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    .gif-blank { height: 400px; }

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

    /* Color and general styles */
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
        margin-top: 5px;
        padding: 8px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
    }
    .round-item { 
        padding: 4px 6px; 
        border-radius: 4px;
        min-width: 25px;
        text-align: center;
    }
    .round-completed { 
        background-color: #e5e7eb;
        color: #9ca3af;
    }
    .round-current   { 
        background-color: #10b981; 
        color: white; 
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    .round-upcoming  { 
        background-color: #f3f4f6;
        color: #6b7280; 
    }
                
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

    /* Invisible button overlay for skipping */
    .skip-btn-container {
        position: relative;
        width: 100%;
    }
    .skip-btn-container button {
        position: absolute !important;
        top: 0;
        left: 0;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 1000 !important;
        border: none !important;
        cursor: pointer;
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
    inject_hiit_css()
    st.title("🔥 Pyramid HIIT Timer")
    st.markdown("### Configure Your Workout")

    c1, c2 = st.columns([2,1])
    with c1:
        all_sequences = st.session_state.config["exercise_sequences"]
        categories = st.session_state.config.get("sequence_categories", {})
        
        # Filter for HIIT sequences
        hiit_sequences = [k for k, v in categories.items() if v == "hiit"]
        if not hiit_sequences:
            # Fallback if no categories or none match
            hiit_sequences = list(all_sequences.keys())
            
        sel = st.selectbox("Choose a sequence:", hiit_sequences, index=0 if st.session_state.selected_sequence not in hiit_sequences else hiit_sequences.index(st.session_state.selected_sequence))
        st.session_state.selected_sequence = sel
        exercises = all_sequences[sel]
        images = st.session_state.config["exercise_images"]

        # Visual layout for thumbnails
        st.markdown("### Exercises Preview")
        cols = st.columns(len(exercises))

        for i, ex in enumerate(exercises):
            img_url = images.get(ex)
            with cols[i]:
                if img_url:
                    st.image(img_url, use_container_width=True)
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
    inject_hiit_css()
    cfg = st.session_state.config
    exercises = cfg["exercise_sequences"][st.session_state.selected_sequence]

    if "workout_phase" not in st.session_state:
        st.session_state.workout_phase = "prepare"

    # --- Define all placeholders ---
    progress_ph = st.empty()
    progress_text = st.empty()
    progress_bar = st.empty()
    labels_ph = st.empty()

    gif_col, timer_col = st.columns([2, 1])
    with gif_col:
        gif_ph_name = st.empty()
        gif_ph = st.empty()
    with timer_col:
        timer_ph = st.empty()

    # Determine current exercise
    curr_list = round_exercises(st.session_state.round, exercises)
    st.session_state.exercise_index = min(st.session_state.exercise_index, len(curr_list) - 1)
    current_exercise = curr_list[st.session_state.exercise_index]

    # Sidebar — styled to match strength mode
    with st.sidebar:
        st.title("🔥 HIIT Workout")
        st.markdown(f"### {st.session_state.selected_sequence}")
        for i, ex in enumerate(exercises):
            if ex == current_exercise:
                prefix = "➡️ "
            else:
                prefix = "⚪ "
            st.markdown(f"{prefix}{ex}")
        st.markdown("---")
        st.markdown("### 🧱 Pyramid Progress")
        show_pyramid_progress()

    # Timer values
    total_time_str = format_time(st.session_state.total_time_seconds)
    
    # Helper for rendering interactive image — invisible tap overlay (like strength mode)
    def render_skip_image(img_url, label=None):
        if label:
            gif_ph_name.markdown(f"<div class='exercise-name'>{label}</div>", unsafe_allow_html=True)
        
        with gif_ph.container():
            st.markdown("""
                <style>
                /* Invisible tap overlay for HIIT image */
                [data-testid="stColumn"]:nth-of-type(1) button {
                    position: absolute !important;
                    height: 400px !important;
                    width: 100% !important;
                    opacity: 0 !important;
                    z-index: 1000 !important;
                    border: none !important;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                }
                </style>
            """, unsafe_allow_html=True)
            if st.button("Skip", key=f"skip_{st.session_state.elapsed_time_seconds}", use_container_width=True):
                st.session_state.skip_triggered = True
                st.rerun()
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.markdown("<div class='gif-blank'></div>", unsafe_allow_html=True)

    # Check for skip from previous run
    if st.session_state.get("skip_triggered"):
        st.session_state.skip_triggered = False
        if st.session_state.workout_phase == "prepare":
            st.session_state.workout_phase = "work"
            st.session_state.elapsed_time_seconds = 10
        elif st.session_state.workout_phase == "work":
            st.session_state.elapsed_time_seconds += cfg["work_time"]
            st.session_state.exercise_index += 1
            if st.session_state.exercise_index < len(curr_list):
                st.session_state.workout_phase = "rest_exercise"
            else:
                st.session_state.workout_phase = "rest_round"
        elif st.session_state.workout_phase == "rest_exercise":
            st.session_state.elapsed_time_seconds += cfg["rest_between_exercises"]
            st.session_state.workout_phase = "work"
        elif st.session_state.workout_phase == "rest_round":
            st.session_state.elapsed_time_seconds += (cfg["peak_rest"] if st.session_state.round == 5 else cfg["rest_between_rounds"])
            st.session_state.round += 1
            st.session_state.exercise_index = 0
            if st.session_state.round > 9:
                st.session_state.workout_phase = "complete"
            else:
                st.session_state.workout_phase = "work"
        st.rerun()

    # -------------------------
    # PHASE EXECUTION
    # -------------------------
    if st.session_state.workout_phase == "prepare":
        labels_ph.markdown("<div class='phase-labels'><span class='label-active'>🚀 PREPARE</span></div>", unsafe_allow_html=True)
        img_url = cfg["exercise_images"].get(current_exercise)
        render_skip_image(img_url, "GET READY!")
        
        for t in range(10, 0, -1):
            elapsed = 10 - t
            progress_text.markdown(f"### ⏱ {format_time(elapsed)} / {total_time_str}")
            progress_bar.progress(min(1.0, elapsed / st.session_state.total_time_seconds))
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.session_state.workout_phase = "work"
        st.session_state.elapsed_time_seconds = 10
        st.rerun()

    elif st.session_state.workout_phase == "work":
        labels_ph.markdown("<div class='phase-labels'><span class='label-active'>⚡ WORK</span> | <span class='label-faded'>REST 😮‍💨</span></div>", unsafe_allow_html=True)
        img_url = cfg["exercise_images"].get(current_exercise)
        render_skip_image(img_url, f"💪 {current_exercise}")
        
        work_time = cfg["work_time"]
        for t in range(work_time, 0, -1):
            current_elapsed = st.session_state.elapsed_time_seconds + (work_time - t)
            progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
            progress_bar.progress(min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds)))
            timer_ph.markdown(f"<div class='big-timer work-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.session_state.elapsed_time_seconds += work_time
        st.session_state.exercise_index += 1
        if st.session_state.exercise_index < len(curr_list):
            st.session_state.workout_phase = "rest_exercise"
        else:
            st.session_state.workout_phase = "rest_round"
        st.rerun()

    elif st.session_state.workout_phase == "rest_exercise":
        labels_ph.markdown("<div class='phase-labels'><span class='label-faded'>⚡ WORK</span> | <span class='label-active'>REST 😮‍💨</span></div>", unsafe_allow_html=True)
        next_exercise = curr_list[st.session_state.exercise_index]
        rest_duration = cfg["rest_between_exercises"]
        
        for t in range(rest_duration, 0, -1):
            if t == rest_duration or t % 15 == 0:
                render_skip_image(random.choice(STRETCHING_GIFS), f"NEXT: {next_exercise}")
            
            current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
            progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
            progress_bar.progress(min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds)))
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)
            
        st.session_state.elapsed_time_seconds += rest_duration
        st.session_state.workout_phase = "work"
        st.rerun()

    elif st.session_state.workout_phase == "rest_round":
        if st.session_state.round == 9:
            st.session_state.workout_phase = "complete"
            st.rerun()

        labels_ph.markdown("<div class='phase-labels'><span class='label-faded'>⚡ WORK</span> | <span class='label-active'>REST 😮‍💨</span></div>", unsafe_allow_html=True)
        
        if st.session_state.round == 5:
            rest_duration = cfg["peak_rest"]
            label = f"PEAK REST ⛰️: Round {st.session_state.round} of 9"
        else:
            rest_duration = cfg["rest_between_rounds"]
            label = f"REST BETWEEN ROUNDS: Round {st.session_state.round} of 9"

        for t in range(rest_duration, 0, -1):
            if t == rest_duration or t % 15 == 0:
                render_skip_image(random.choice(STRETCHING_GIFS), label)
            
            current_elapsed = st.session_state.elapsed_time_seconds + (rest_duration - t)
            progress_text.markdown(f"### ⏱ {format_time(current_elapsed)} / {total_time_str}")
            progress_bar.progress(min(1.0, max(0.0, current_elapsed / st.session_state.total_time_seconds)))
            timer_ph.markdown(f"<div class='big-timer rest-phase'>{t}</div>", unsafe_allow_html=True)
            time.sleep(1)

        st.session_state.elapsed_time_seconds += rest_duration
        st.session_state.round += 1
        st.session_state.exercise_index = 0
        st.session_state.workout_phase = "work"
        st.rerun()

    elif st.session_state.workout_phase == "complete":
        st.balloons()
        st.success("🎉 WORKOUT COMPLETE! Amazing job!")
        total_time_str = format_time(st.session_state.total_time_seconds)
        progress_ph.markdown(f"### Total Workout Time: **{total_time_str}**")
        st.progress(1.0)
        if st.button("Back to Setup"):
            st.session_state.workout_started = False
            st.session_state.elapsed_time_seconds = 0
            st.session_state.workout_phase = "prepare"
            st.rerun()
        return "complete"

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