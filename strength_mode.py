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

    raw_ex = exercises[st.session_state.strength_exercise_index]
    
    # Handle list-based choice logic
    if isinstance(raw_ex, list):
        options = raw_ex
        choice_key = f"choice_{st.session_state.strength_exercise_index}"
        if choice_key not in st.session_state or st.session_state[choice_key] not in options:
            st.session_state[choice_key] = options[0]
            
        st.subheader("Select Variation")
        current_ex = st.selectbox(
            "Choose your movement:",
            options,
            index=options.index(st.session_state[choice_key]),
            key=f"select_{st.session_state.strength_exercise_index}"
        )
        st.session_state[choice_key] = current_ex
    else:
        current_ex = raw_ex

    # Update Sidebar with selection info if applicable
    with st.sidebar:
        if isinstance(raw_ex, list):
            st.info(f"Selected: {current_ex}")

    metadata = cfg.get("strength_metadata", {}).get(current_ex, {})
    img_url = cfg["exercise_images"].get(current_ex)

    # Helper for advancing set logic
    target_sets_str = metadata.get('sets', "3").split("-")[-1] 
    try:
        target_sets = int(target_sets_str)
    except:
        target_sets = 3

    def advance_set():
        st.session_state.strength_set_index += 1
        if st.session_state.strength_set_index >= target_sets:
            st.session_state.strength_exercise_index += 1
            st.session_state.strength_set_index = 0
            st.toast(f"Exercise {current_ex} complete!")
        st.rerun()

    st.header(f"{current_ex}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if img_url:
            # Enforce image height and button overlay via direct CSS
            st.markdown(
                """
                <style>
                /* Target the image in the first main-area column */
                [data-testid="stColumn"]:nth-of-type(1) img {
                    max-height: 400px !important;
                    width: auto !important;
                    object-fit: contain !important;
                    margin-left: auto;
                    margin-right: auto;
                    display: block;
                }
                /* Target the button in the same column and make it an invisible overlay */
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
                """, unsafe_allow_html=True
            )
            
            # The button renders first in the DOM, becoming an overlay for what follows
            if st.button("Complete Set", key="clickable_img_overlay", use_container_width=True):
                advance_set()
                
            st.image(img_url, use_container_width=True)
            st.caption("Tip: You can tap the image to complete a set!")
        else:
            st.info("No image available for this exercise.")
            
    with col2:
        st.markdown(f"**Sets:** {metadata.get('sets', 'N/A')}")
        st.markdown(f"**Reps:** {metadata.get('reps', 'N/A')}")

        st.divider()

        # Set tracking
        current_set = st.session_state.strength_set_index + 1
        st.markdown(f"### Set {current_set} of {target_sets}")
        
        # No visible button here either

        st.divider()

        st.markdown("**Cues:**")
        cues_list = metadata.get('cues', "").split(";")
        cues_markdown = "\n".join([f"- {cue.strip()}" for cue in cues_list if cue.strip()])
        st.markdown(cues_markdown)

    return "active"
