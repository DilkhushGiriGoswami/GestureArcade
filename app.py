import streamlit as st
import json
import os
from time import sleep
# import game
# import cv2
# import mediapipe as mp
# import random
# import numpy as np

# --- IMPORTANT: Import your game function ---
# Make sure game.py is in the same directory
try:
    from games import run_games
except ImportError:
    # Provide a dummy function if game.py is not found, to avoid crashing
    def run_game():
        st.error("`game.py` not found. Please make sure it's in the same folder.")
        return 0, 1

st.set_page_config(page_title="Catch the Ball Game 🎮", layout="wide")

# --- Neon CSS Styling (your existing style code) ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Trebuchet MS', sans-serif;
    }

    h1 {
        color: #ffde59;
        text-align: center;
        font-size: 3.2em !important;
        text-shadow: 0 0 15px #ffde59, 0 0 30px #ffaa00;
        margin-bottom: 10px;
    }

    h3 {
        color: #eeeeee;
        text-align: center;
        margin-top: -10px;
    }

    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffde59, transparent);
        margin: 20px 0;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1f1c2c, #403d59);
        color: white;
        padding: 22px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0px 0px 15px rgba(255, 222, 89, 0.7);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 25px rgba(255, 222, 89, 1);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 16px;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 30px;
        border: none;
        cursor: pointer;
        transition: 0.3s;
        box-shadow: 0 0 12px rgba(255, 65, 108, 0.8);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff758c, #ff7eb3);
        transform: scale(1.1);
        box-shadow: 0 0 25px rgba(255, 120, 180, 1);
    }

    /* Info/Success/Warning Messages */
    .stAlert {
        border-radius: 12px;
        font-size: 16px;
        padding: 12px;
    }

    /* Center Buttons */
    div[data-testid="column"] > div {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

PROGRESS_FILE = "progress.json"

# --- Progress Functions ---
def load_progress():
    """Loads progress from the file, returning a default if not found."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"score": 0, "level": 1}
    return {"score": 0, "level": 1}

def save_progress(progress_data):
    """Saves the current progress data to the file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_data, f)

# --- Session State Initialization ---
if 'progress' not in st.session_state:
    st.session_state.progress = load_progress()

# --- UI Layout ---
st.title("🎮 Catch the Ball Game")
st.subheader("✋ Play with your hand gestures. Catch → Level Up → Enjoy 🚀")

col1, col2 = st.columns(2)
score_metric = col1.empty()
level_metric = col2.empty()

def update_metrics():
    """Updates the score and level display from session state."""
    score_metric.metric("⭐ High Score", st.session_state.progress["score"])
    level_metric.metric("🏆 Level", st.session_state.progress["level"])

update_metrics()

st.markdown("<hr>", unsafe_allow_html=True)

# --- Control Buttons ---
col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    if st.button("▶️ Play Game", use_container_width=True):
        st.info("Launching game... Close the game window when you're done.")
        
        final_score, final_level = games.run_games()
        
        if final_score > st.session_state.progress.get('score', 0):
            st.success(f"New High Score: {final_score}! Progress saved.")
            st.session_state.progress = {"score": final_score, "level": final_level}
            save_progress(st.session_state.progress)
        else:
            st.info(f"Game finished! Your score was {final_score}.")

        sleep(2)
        st.rerun()

with col2:
    if st.button("🔄 Refresh Progress", use_container_width=True):
        st.session_state.progress = load_progress()
        st.success("Progress has been refreshed from the saved file.")
        sleep(1.5)
        st.rerun()

with col3:
    if st.button("❌ Reset Progress", use_container_width=True):
        st.session_state.progress = {"score": 0, "level": 1}
        save_progress(st.session_state.progress)
        st.warning("Progress has been reset.")
        sleep(1.5)
        st.rerun()
