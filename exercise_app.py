import streamlit as st
import datetime
from shared_utils import load_config, save_config
import pyramid_hiit_streamlit as hiit
import strength_mode as strength

# Set page config for the entire app
st.set_page_config(page_title="Personal Exercise Regime", page_icon="💪", layout="wide")

PROGRAM_DAYS = {
    1: {"name": "Strength (Leg Day)", "type": "strength", "sequence": "Leg Day"},
    2: {"name": "HIIT / Aerobic", "type": "hiit", "sequence": "Classic HIIT"},
    3: {"name": "Rest", "type": "rest"},
    4: {"name": "Strength (Full Body)", "type": "strength", "sequence": "Full Body"},
    5: {"name": "HIIT / Aerobic", "type": "hiit", "sequence": "Classic HIIT"},
    6: {"name": "Rest", "type": "rest"},
    7: {"name": "Strength (Upper Body)", "type": "strength", "sequence": "Upper Body"},
    8: {"name": "HIIT / Aerobic", "type": "hiit", "sequence": "Classic HIIT"},
    9: {"name": "Rest", "type": "rest"},
}

def init_app_state():
    if "config" not in st.session_state:
        st.session_state.config = load_config()
    
    cfg = st.session_state.config
    if "current_program_day" not in cfg:
        cfg["current_program_day"] = 1
        save_config(cfg)
    
    if "active_workout" not in st.session_state:
        st.session_state.active_workout = False

def show_dashboard():
    st.title("🏋️ My Exercise Regime")
    cfg = st.session_state.config
    current_day = cfg.get("current_program_day", 1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Today's Schedule")
        day_info = PROGRAM_DAYS[current_day]
        st.info(f"### {day_info['name']}")
        
        if day_info['type'] == 'rest':
            st.write("Enjoy your rest day! Recharge for tomorrow.")
            if st.button("Complete Day & Advance"):
                advance_day()
        else:
            if st.button("🚀 START WORKOUT", type="primary"):
                st.session_state.active_workout = True
                st.rerun()

    with col2:
        # Day selection with radio buttons
        day_options = {d: f"Day {d}: {info['name']}" for d, info in PROGRAM_DAYS.items()}
        selected_day_label = st.radio(
            "Go to Day:",
            options=list(day_options.keys()),
            format_func=lambda x: day_options[x],
            index=current_day - 1,
            horizontal=False
        )
        
        if selected_day_label != current_day:
            cfg["current_program_day"] = selected_day_label
            save_config(cfg)
            st.rerun()

def advance_day():
    cfg = st.session_state.config
    current_day = cfg.get("current_program_day", 1)
    next_day = current_day + 1
    if next_day > 9:
        next_day = 1
        st.balloons()
        st.toast("Regime completed! Starting over.")
    cfg["current_program_day"] = next_day
    save_config(cfg)
    st.rerun()

def main():
    init_app_state()
    
    if st.session_state.active_workout:
        day_info = PROGRAM_DAYS[st.session_state.config["current_program_day"]]
        
        if day_info['type'] == 'strength':
            # Add Back to Dashboard button in sidebar for strength mode
            with st.sidebar:
                if st.button("⬅️ Back to Dashboard"):
                    st.session_state.active_workout = False
                    st.rerun()
            
            status = strength.show_strength_screen(day_info['sequence'])
            if status == "complete":
                st.session_state.active_workout = False
                advance_day()
        elif day_info['type'] == 'hiit':
            # Integrate HIIT logic
            st.session_state.selected_sequence = day_info['sequence']
            
            # Allow manual return if needed
            with st.sidebar:
                if st.button("⬅️ Back to Dashboard"):
                    st.session_state.active_workout = False
                    st.session_state.workout_started = False
                    st.rerun()
                    
            status = hiit.main()
            
            if status == "complete":
                if st.button("Finish & Return to Dash"):
                    st.session_state.active_workout = False
                    st.session_state.workout_started = False
                    advance_day()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
