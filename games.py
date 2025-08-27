import streamlit as st
import cv2
import mediapipe as mp
import random
import time
import json
import os

# -------------------------
# Progress File Handling
# -------------------------
PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"score": 0, "level": 1}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# -------------------------
# Catch Ball Game
# -------------------------
def run_games():
    st.title("🎮 Catch the Ball Game (Streamlit Edition)")

    if "score" not in st.session_state:
        st.session_state.score = 0
    if "level" not in st.session_state:
        st.session_state.level = 1
    if "ball_x" not in st.session_state:
        st.session_state.ball_x = random.randint(50, 550)
    if "ball_y" not in st.session_state:
        st.session_state.ball_y = 50

    picture = st.camera_input("📷 Enable your camera to play")

    if picture:
        # Convert image to OpenCV format
        file_bytes = np.asarray(bytearray(picture.getbuffer()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)

        h, w, _ = frame.shape

        # Ball parameters
        ball_radius = 20
        basket_y = h - 50
        basket_x = w // 2

        # Draw the ball
        cv2.circle(frame, (st.session_state.ball_x, st.session_state.ball_y),
                   ball_radius, (0, 0, 255), -1)

        # Draw basket
        cv2.rectangle(frame, (basket_x - 50, basket_y - 20),
                      (basket_x + 50, basket_y + 20), (0, 255, 0), 2)

        # Move ball down
        st.session_state.ball_y += 10

        # Reset ball if it goes down
        if st.session_state.ball_y > h:
            st.session_state.ball_x = random.randint(50, w - 50)
            st.session_state.ball_y = 50

        # Detect "catch" (center of ball in basket area)
        if (basket_x - 50 < st.session_state.ball_x < basket_x + 50 and
                basket_y - 20 < st.session_state.ball_y < basket_y + 20):
            st.session_state.score += 1
            st.session_state.ball_y = 50
            st.session_state.ball_x = random.randint(50, w - 50)

            # Increase level every 5 points
            if st.session_state.score % 5 == 0:
                st.session_state.level += 1

        # Show text
        cv2.putText(frame, f"Score: {st.session_state.score}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Level: {st.session_state.level}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        st.image(frame, channels="BGR")

    return st.session_state.score, st.session_state.level
# -------------------------
# Streamlit Main App
# -------------------------
def main():
    st.set_page_config(page_title="Catch the Ball 🎮", layout="wide")

    # Gradient background
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            font-family: 'Trebuchet MS', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎮 Gesture Arcade - Catch the Ball")
    st.write("👉 Use your hand to catch the falling ball. Press **Q** to quit the game window.")

    # Load progress
    if "progress" not in st.session_state:
        st.session_state.progress = load_progress()

    st.metric("High Score", st.session_state.progress["score"])
    st.metric("Highest Level", st.session_state.progress["level"])

    if st.button("▶️ Start Game", use_container_width=True):
        st.info("Launching game... Close the camera window when done.")
        final_score, final_level = run_games()

        # Save progress if improved
        if final_score > st.session_state.progress["score"]:
            st.session_state.progress["score"] = final_score
            st.success(f"🎉 New High Score: {final_score}!")
        if final_level > st.session_state.progress["level"]:
            st.session_state.progress["level"] = final_level
            st.success(f"🚀 New Highest Level: {final_level}!")

        save_progress(st.session_state.progress)

if __name__ == "__main__":
    main()
