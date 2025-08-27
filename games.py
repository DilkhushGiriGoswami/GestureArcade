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
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("❌ Camera not accessible. Please check permissions.")
        return 0, 1  # Default values

    score, level = 0, 1
    ball_x, ball_y = random.randint(50, 590), 0
    ball_speed = 5
    last_time = time.time()

    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            h, w, _ = frame.shape
            hand_x, hand_y = None, None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_x = int(hand_landmarks.landmark[8].x * w)
                    hand_y = int(hand_landmarks.landmark[8].y * h)
                    cv2.circle(frame, (hand_x, hand_y), 10, (255, 0, 0), -1)

            # Ball movement
            ball_y += ball_speed
            if ball_y > h:
                ball_y = 0
                ball_x = random.randint(50, w - 50)

            # Collision detection
            if hand_x and abs(hand_x - ball_x) < 50 and abs(hand_y - ball_y) < 50:
                score += 10
                ball_y = 0
                ball_x = random.randint(50, w - 50)

                if score % 50 == 0:
                    level += 1
                    ball_speed += 2

            # HUD
            cv2.putText(frame, f"Score: {score}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, f"Level: {level}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

            cv2.circle(frame, (ball_x, ball_y), 20, (0, 0, 255), -1)

            cv2.imshow("Catch the Ball 🎮 (Press Q to Quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    return score, level

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
