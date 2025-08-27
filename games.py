import cv2
import mediapipe as mp
import random
import json
import os
import numpy as np
import streamlit as st

# --- Constants ---
PROGRESS_FILE = "progress.json"
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


# --- Load Progress ---
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"score": 0, "level": 1}
    return {"score": 0, "level": 1}


# --- Save Progress ---
def save_progress(score, level):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"score": score, "level": level}, f)


# --- Gesture Helpers ---
def detect_hand_center(hand_landmarks, width, height):
    cx = int(hand_landmarks.landmark[9].x * width)
    cy = int(hand_landmarks.landmark[9].y * height)
    return cx, cy


# --- Drawing Helpers ---
def draw_environment(frame, level):
    overlay = np.zeros_like(frame, np.uint8)
    rows, _, _ = frame.shape
    for i in range(rows):
        color = (int(50 + (i/rows)*100), int((i/rows)*150), int((i/rows)*200))
        overlay[i, :] = color
    frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
    return frame


def draw_hud(frame, score, level, misses):
    cv2.putText(frame, f"Score: {score}", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Level: {level}", (20, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 255), 2)
    cv2.putText(frame, f"Misses: {misses}/3", (20, 120), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)


# --- Main Game ---
def run_games():
    #st.title("🎮 Catch the Ball Game")

    if "playing" not in st.session_state:
        st.session_state.playing = False
        st.session_state.score = 0
        st.session_state.level = 1
        st.session_state.misses = 0

   # start_btn = st.button("▶️ Start Game")
    stop_btn = st.button("⏹️ Stop Game")

    if start_btn:
        st.session_state.playing = True
        st.session_state.score = 0
        st.session_state.level = load_progress().get("level", 1)
        st.session_state.misses = 0

    if stop_btn:
        st.session_state.playing = False
        save_progress(st.session_state.score, st.session_state.level)
        st.success(f"✅ Final Score: {st.session_state.score} | Level: {st.session_state.level}")

    frame_placeholder = st.empty()

    if st.session_state.playing:
        cap = cv2.VideoCapture(0)
        hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

        width, height = 640, 480
        cap.set(3, width)
        cap.set(4, height)

        ball_x, ball_y = random.randint(50, width - 50), 0
        ball_speed, ball_radius = 5 + st.session_state.level, 20

        while st.session_state.playing and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame = draw_environment(frame, st.session_state.level)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            hand_center = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    hand_center = detect_hand_center(hand_landmarks, width, height)

            # Ball mechanics
            ball_y += int(ball_speed)
            if ball_y > height:
                st.session_state.misses += 1
                ball_x, ball_y = random.randint(50, width - 50), 0
                if st.session_state.misses >= 3:
                    st.session_state.playing = False
                    break

            if hand_center:
                hx, hy = hand_center
                if abs(hx - ball_x) < 40 and abs(hy - ball_y) < 40:
                    st.session_state.score += 1
                    ball_x, ball_y = random.randint(50, width - 50), 0
                    if st.session_state.score > 0 and st.session_state.score % 5 == 0:
                        st.session_state.level += 1
                        ball_speed += 1

            cv2.circle(frame, (ball_x, ball_y), ball_radius, (0, 0, 255), -1)
            draw_hud(frame, st.session_state.score, st.session_state.level, st.session_state.misses)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        cap.release()
        hands.close()
        save_progress(st.session_state.score, st.session_state.level)


if __name__ == "__main__":
    run_games()
