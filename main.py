import cv2
import numpy as np
import mediapipe as mp
from collections import deque

bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]
ppoints = [deque(maxlen=1024)]  
opoints = [deque(maxlen=1024)]  
blue_index = green_index = red_index = yellow_index = pink_index = orange_index = 0

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (0, 255, 255), (255, 0, 255), (0, 165, 255)]  # Blue, Green, Red, Yellow, Pink, Orange
colorIndex = 0

# Make bigger paint canvas (to match 1280x720 camera size)
paintWindow = np.zeros((720, 1280, 3)) + 255

# Draw toolbar buttons across full width
buttons = [("CLEAR", (40, 1), (190, 65), (0, 0, 0)),      # Clear
           ("BLUE", (210, 1), (360, 65), (255, 0, 0)),    # Blue
           ("GREEN", (380, 1), (530, 65), (0, 255, 0)),   # Green
           ("RED", (550, 1), (700, 65), (0, 0, 255)),     # Red
           ("YELLOW", (720, 1), (870, 65), (0, 255, 255)),# Yellow
           ("PINK", (890, 1), (1040, 65), (255, 0, 255)), # Pink
           ("ORANGE", (1060, 1), (1210, 65), (0, 165, 255))]  # Orange

for text, start, end, color in buttons:
    paintWindow = cv2.rectangle(paintWindow, start, end, color, 2)
    cv2.putText(paintWindow, text, (start[0]+20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 0), 2, cv2.LINE_AA)

# Resizable windows
cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
cv2.namedWindow("Paint", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Tracking", 1280, 720)
cv2.resizeWindow("Paint", 1280, 720)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Set camera resolution to 1280x720
cap.set(3, 1280)
cap.set(4, 720)

ret = True
while ret:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Draw toolbar on camera frame
    for text, start, end, color in buttons:
        frame = cv2.rectangle(frame, start, end, color, 2)
        cv2.putText(frame, text, (start[0]+20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 0, 0), 2, cv2.LINE_AA)

    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * 1280)
                lmy = int(lm.y * 720)
                landmarks.append([lmx, lmy])

            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

        fore_finger = (landmarks[8][0], landmarks[8][1])
        center = fore_finger
        thumb = (landmarks[4][0], landmarks[4][1])
        cv2.circle(frame, center, 5, (0, 255, 0), -1)

        if thumb[1] - center[1] < 30:
            bpoints.append(deque(maxlen=512)); blue_index += 1
            gpoints.append(deque(maxlen=512)); green_index += 1
            rpoints.append(deque(maxlen=512)); red_index += 1
            ypoints.append(deque(maxlen=512)); yellow_index += 1
            ppoints.append(deque(maxlen=512)); pink_index += 1
            opoints.append(deque(maxlen=512)); orange_index += 1

        elif center[1] <= 65: 
            # Clear
            if 40 <= center[0] <= 190:
                bpoints, gpoints, rpoints, ypoints, ppoints, opoints = \
                    [deque(maxlen=512)], [deque(maxlen=512)], [deque(maxlen=512)], \
                    [deque(maxlen=512)], [deque(maxlen=512)], [deque(maxlen=512)]
                blue_index = green_index = red_index = yellow_index = pink_index = orange_index = 0
                paintWindow[67:, :, :] = 255
            # Colors
            elif 210 <= center[0] <= 360: colorIndex = 0  # Blue
            elif 380 <= center[0] <= 530: colorIndex = 1  # Green
            elif 550 <= center[0] <= 700: colorIndex = 2  # Red
            elif 720 <= center[0] <= 870: colorIndex = 3  # Yellow
            elif 890 <= center[0] <= 1040: colorIndex = 4  # Pink
            elif 1060 <= center[0] <= 1210: colorIndex = 5  # Orange

        else:
            if colorIndex == 0: bpoints[blue_index].appendleft(center)
            elif colorIndex == 1: gpoints[green_index].appendleft(center)
            elif colorIndex == 2: rpoints[red_index].appendleft(center)
            elif colorIndex == 3: ypoints[yellow_index].appendleft(center)
            elif colorIndex == 4: ppoints[pink_index].appendleft(center)
            elif colorIndex == 5: opoints[orange_index].appendleft(center)

    # Draw lines on both windows
    points = [bpoints, gpoints, rpoints, ypoints, ppoints, opoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None: continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 3)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 3)

    cv2.imshow("Tracking", frame)
    cv2.imshow("Paint", paintWindow)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
