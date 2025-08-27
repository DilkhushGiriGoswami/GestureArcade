import cv2
import mediapipe as mp
import random
import json
import os
import numpy as np
import time
import streamlit as st

# --- Constants & Setup ---
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


# --- Gesture Helpers ---
def detect_fist(hand_landmarks):
    tips = [8, 12, 16, 20]
    folded = [hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y for tip in tips]
    return all(folded)


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
    alpha = 0.4
    frame = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
    color_shift = (level // 5) % 5
    tints = [(30, 30, 30), (0, 50, 100), (80, 0, 80), (0, 100, 50), (100, 60, 0)]
    tint_overlay = np.full_like(frame, tints[color_shift])
    frame = cv2.addWeighted(frame, 0.9, tint_overlay, 0.1, 0)
    return frame


def draw_hud(frame, score, level, misses):
    overlay = frame.copy()
    cv2.rectangle(overlay, (5, 5), (230, 145), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    cv2.putText(frame, f"Score: {score}", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Level: {level}", (20, 90), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 255), 2)
    cv2.putText(frame, f"Misses: {misses}/3", (20, 130), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)


def draw_game_over(frame, score):
    overlay = frame.copy()
    cv2.rectangle(overlay, (80, 150), (560, 380), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.putText(frame, "GAME OVER", (150, 220), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 6)
    cv2.putText(frame, f"Final Score: {score}", (180, 270), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)
    cv2.putText(frame, "Click Restart or Stop", (160, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)


# --- Main Game ---
def run_games():
    st.title("🎮 Catch the Ball Game")

    start_btn = st.button("Start Game")
    if not start_btn:
        return

    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    width, height = 640, 480
    cap.set(3, width)
    cap.set(4, height)

    progress = load_progress()
    score, level = 0, progress.get("level", 1)
    ball_x, ball_y = random.randint(50, width - 50), 0
    ball_speed, ball_radius, misses = 5 + level, 20, 0
    game_over = False

    frame_placeholder = st.empty()
    stop_btn = st.button("Stop Game")

    while cap.isOpened() and not stop_btn:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = draw_environment(frame, level)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        hand_center = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_center = detect_hand_center(hand_landmarks, width, height)

        if game_over:
            draw_game_over(frame, score)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            continue

        # Ball mechanics
        ball_y += int(ball_speed)
        if ball_y > height:
            misses += 1
            ball_x, ball_y = random.randint(50, width - 50), 0
            if misses >= 3:
                game_over = True

        if hand_center:
            hx, hy = hand_center
            if abs(hx - ball_x) < 40 and abs(hy - ball_y) < 40:
                score += 1
                ball_x, ball_y = random.randint(50, width - 50), 0
                if score > 0 and score % 5 == 0:
                    level += 1
                    ball_speed += 1

        cv2.circle(frame, (ball_x, ball_y), ball_radius, (0, 0, 255), -1)
        draw_hud(frame, score, level, misses)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()
    hands.close()
    st.success(f"Final Score: {score} | Level: {level}")
    return score, level
 

if __name__ == "__main__":
    run_game()
