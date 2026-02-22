import streamlit as st
import time
import random
from shared_utils import STRETCHING_GIFS, load_config, save_config, format_time

def init_strength_session():
    if "config" not in st.session_state:
        st.session_state.config = load_config()
    if "strength_started" not in st.session_state:
        st.session_state.strength_started = False
    if "strength_exercise_index" not in st.session_state:
        st.session_state.strength_exercise_index = 0
    if "strength_set_index" not in st.session_state:
        st.session_state.strength_set_index = 0

def show_strength_screen(sequence_key):
    init_strength_session()
    cfg = st.session_state.config
    exercises = cfg["exercise_sequences"].get(sequence_key, [])
    
    if not exercises:
        st.error(f"Sequence {sequence_key} not found!")
        return

    # Sidebar
    with st.sidebar:
        st.title("🏋️ Strength Training")
        st.markdown(f"### {sequence_key}")
        for i, ex in enumerate(exercises):
            prefix = "➡️ " if i == st.session_state.strength_exercise_index else "✅ " if i < st.session_state.strength_exercise_index else "⚪ "
            st.markdown(f"{prefix}{ex}")
        
        if st.button("Reset Workout"):
            st.session_state.strength_exercise_index = 0
            st.session_state.strength_set_index = 0
            st.session_state.strength_started = False
            st.rerun()

    # Main Area
    if st.session_state.strength_exercise_index >= len(exercises):
        st.balloons()
        st.success("🎉 Strength Session Complete!")
        if st.button("Back to Dashboard"):
            return "complete"
        return

    current_ex = exercises[st.session_state.strength_exercise_index]
    metadata = cfg.get("strength_metadata", {}).get(current_ex, {})
    img_url = cfg["exercise_images"].get(current_ex)

    st.header(f"{current_ex}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if img_url:
            st.image(img_url, use_container_width=True)
        else:
            st.info("No image available for this exercise.")
            
    with col2:
        st.markdown(f"**Sets:** {metadata.get('sets', 'N/A')}")
        st.markdown(f"**Reps:** {metadata.get('reps', 'N/A')}")
        st.markdown("**Cues:**")
        cues_list = metadata.get('cues', "").split(";")
        cues_markdown = "\n".join([f"- {cue.strip()}" for cue in cues_list if cue.strip()])
        st.markdown(cues_markdown)

        st.divider()
        
        # Set tracking
        target_sets_str = metadata.get('sets', "3").split("-")[-1] # take max sets
        try:
            target_sets = int(target_sets_str)
        except:
            target_sets = 3
            
        current_set = st.session_state.strength_set_index + 1
        st.markdown(f"### Set {current_set} of {target_sets}")
        
        if st.button("✅ SET COMPLETE", type="primary", use_container_width=True):
            st.session_state.strength_set_index += 1
            if st.session_state.strength_set_index >= target_sets:
                st.session_state.strength_exercise_index += 1
                st.session_state.strength_set_index = 0
                st.toast(f"Exercise {current_ex} complete!")
            st.rerun()

    return "active"
