import cv2
import numpy as np
import mediapipe as mp
import time
import math
import os
from datetime import datetime
from server import run_server

# ---------------------------------------------------------
# 1. State & Server Initialization
# ---------------------------------------------------------
server_state = {
    'colorIndex': 0,
    'brushSize': 5,
    'mode': 'Hover',
    'fps': 0,
    'commands': [],
    'frame_bytes': None
}

run_server(server_state, port=5000)
print("Server started at http://localhost:5000")

# ---------------------------------------------------------
# 2. Configuration & Variables
# ---------------------------------------------------------
# Colors matching the frontend (in BGR format for OpenCV)
# [Blue, Green, Red, Yellow, Pink, Orange, Purple, Cyan]
colors = [
    (246, 130, 59),   # Blue (#3b82f6) -> BGR
    (94, 197, 34),    # Green (#22c55e)
    (68, 68, 239),    # Red (#ef4444)
    (8, 179, 234),    # Yellow (#eab308)
    (153, 72, 236),   # Pink (#ec4899)
    (22, 115, 249),   # Orange (#f97316)
    (247, 85, 168),   # Purple (#a855f7)
    (212, 182, 6)     # Cyan (#06b6d4)
]

colorIndex = 0
brushSize = 5
mode = 'Hover'
selected_tool = 'Draw'

# History for Undo and Canvas Redraw
strokes = []
current_stroke = None
canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

# EMA Smoothing
smoothed_pos = None
alpha = 0.4  # Smoothing factor (0=rigid, 1=no smoothing)

def calculate_distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def redraw_canvas():
    global canvas
    canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
    for stroke in strokes:
        pts = stroke['points']
        col = stroke['color']
        sz = stroke['size']
        for i in range(1, len(pts)):
            cv2.line(canvas, pts[i-1], pts[i], col, sz)

backend_dir = os.path.dirname(__file__)
saved_dir = os.path.join(os.path.dirname(backend_dir), "saved")
if not os.path.exists(saved_dir):
    os.makedirs(saved_dir)

# ---------------------------------------------------------
# 3. MediaPipe & Camera Setup
# ---------------------------------------------------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

pTime = 0
last_mode = 'Hover'
stable_frames = 0
DEBOUNCE_FRAMES = 2

# ---------------------------------------------------------
# 4. Main Loop
# ---------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.resize(frame, (1280, 720))
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process Frontend API Commands
    while len(server_state['commands']) > 0:
        cmd = server_state['commands'].pop(0)
        action = cmd.get('action')
        
        if action == 'set_color':
            colorIndex = int(cmd.get('index', 0))
            selected_tool = 'Draw'
        elif action == 'set_brush_size':
            brushSize = int(cmd.get('size', 5))
        elif action == 'clear':
            strokes.clear()
            current_stroke = None
            redraw_canvas()
        elif action == 'undo':
            if len(strokes) > 0:
                strokes.pop()
                current_stroke = None
                redraw_canvas()
        elif action == 'eraser':
            selected_tool = 'Eraser'
        elif action == 'save':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create a clean white background for saving
            save_img = np.zeros((720, 1280, 3), dtype=np.uint8) + 255
            for stroke in strokes:
                if stroke['color'] != (0,0,0): # Ignore eraser strokes on white bg
                    pts = stroke['points']
                    for i in range(1, len(pts)):
                        cv2.line(save_img, pts[i-1], pts[i], stroke['color'], stroke['size'])
            save_path = os.path.join(saved_dir, f"painting_{timestamp}.png")
            cv2.imwrite(save_path, save_img)
            print(f"Saved: {save_path}")

    # Process Hand Tracking
    result = hands.process(framergb)
    detected_mode = 'Hover'
    
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
            
            lmList = []
            h, w, c = frame.shape
            for id, lm in enumerate(handLms.landmark):
                lmList.append([int(lm.x * w), int(lm.y * h)])
                
            if len(lmList) > 0:
                # Finger States (0=down, 1=up)
                fingers = []
                # Thumb
                if lmList[4][0] < lmList[3][0]: fingers.append(1)
                else: fingers.append(0)
                # Index, Middle, Ring, Pinky
                for id in [8, 12, 16, 20]:
                    if lmList[id][1] < lmList[id - 2][1]: fingers.append(1)
                    else: fingers.append(0)
                        
                index_pos = (lmList[8][0], lmList[8][1])
                
                # EMA Smoothing
                if smoothed_pos is None:
                    smoothed_pos = list(index_pos)
                else:
                    smoothed_pos[0] = int(alpha * index_pos[0] + (1 - alpha) * smoothed_pos[0])
                    smoothed_pos[1] = int(alpha * index_pos[1] + (1 - alpha) * smoothed_pos[1])
                
                cx, cy = int(smoothed_pos[0]), int(smoothed_pos[1])
                
                indicator_color = (0,0,0) if selected_tool == 'Eraser' else colors[colorIndex]
                cv2.circle(frame, (cx, cy), brushSize, indicator_color, 2)
                
                # Gesture Recognition (Modifier Fingers)
                # 1. Clear: Open Hand ✋ (Very lenient: at least 3 fingers up including pinky)
                if sum(fingers[1:]) >= 3 and fingers[4] == 1:
                    mode = 'Clear'
                # 2. Erase: Index + Pinky UP 🤘 (Rock On)
                elif fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 1:
                    mode = 'Eraser'
                # 3. Hover: Index + Middle UP ✌️
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                    mode = 'Hover'
                # 4. Draw: ONLY Index UP 👆
                elif fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 0:
                    mode = selected_tool
                else:
                    mode = 'Hover'
                    
                cv2.putText(frame, f"MODE: {mode}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, indicator_color, 3)
                
                # Action Execution
                if mode in ['Draw', 'Eraser']:
                    col = (0,0,0) if mode == 'Eraser' else colors[colorIndex]
                    sz = brushSize * 4 if mode == 'Eraser' else brushSize
                    
                    if current_stroke is None or current_stroke['color'] != col or current_stroke['size'] != sz:
                        current_stroke = {'color': col, 'size': sz, 'points': [(cx, cy)]}
                        strokes.append(current_stroke)
                    else:
                        last_pt = current_stroke['points'][-1]
                        if calculate_distance(last_pt, (cx, cy)) > 2:
                            current_stroke['points'].append((cx, cy))
                            cv2.line(canvas, last_pt, (cx, cy), col, sz)
                
                elif mode == 'Clear':
                    strokes.clear()
                    redraw_canvas()
                    current_stroke = None
                    
                else: # Hover
                    current_stroke = None
    else:
        smoothed_pos = None
        current_stroke = None
        
    # Combine Frame and Canvas
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    
    bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    blended = cv2.add(bg, fg)
    
    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime
    
    # Update State for Web Frontend
    server_state['fps'] = int(fps)
    server_state['mode'] = mode
    server_state['colorIndex'] = colorIndex
    server_state['brushSize'] = brushSize
    
    # Stream to Frontend
    ret_encode, jpeg = cv2.imencode('.jpg', blended, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if ret_encode:
        server_state['frame_bytes'] = jpeg.tobytes()

    # Local Display Overlay
    cv2.putText(blended, f"FPS: {int(fps)} | Mode: {mode}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("AI Virtual Canvas", blended)
        
    # Keyboard Shortcuts
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        strokes.clear()
        current_stroke = None
        canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
    elif key == ord('e'):
        selected_tool = 'Eraser'
    elif ord('1') <= key <= ord('8'):
        colorIndex = key - ord('1')
        selected_tool = 'Draw'
    elif key == ord('s'):
        server_state['commands'].append({'action': 'save'})
    elif key == 26: # Ctrl+Z
        server_state['commands'].append({'action': 'undo'})

cap.release()
cv2.destroyAllWindows()
