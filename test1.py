# import cv2
# import mediapipe as mp
# import pyautogui
# import math

# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
# mp_draw = mp.solutions.drawing_utils

# screen_w, screen_h = pyautogui.size()
# cam_w, cam_h = 640, 480
# cap = cv2.VideoCapture(0)
# cap.set(3, cam_w)
# cap.set(4, cam_h)

# pyautogui.FAILSAFE = False

# def fingers_distance(p1, p2):
#     return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

# clicking = False  # عشان الكليك ميتكررش

# while True:
#     ret, frame = cap.read()
#     frame = cv2.flip(frame, 1)
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     result = hands.process(rgb)

#     if result.multi_hand_landmarks:
#         for hand_landmarks in result.multi_hand_landmarks:
#             lm = hand_landmarks.landmark

#             # بطن الإيد (النقطة 9) للتحريك
#             palm_x = int(lm[9].x * screen_w)
#             palm_y = int(lm[9].y * screen_h)
#             pyautogui.moveTo(palm_x, palm_y, duration=0.05)

#             # السبابة (8) والإبهام (4) للكليك
#             index_x = int(lm[8].x * cam_w)
#             index_y = int(lm[8].y * cam_h)
#             thumb_x  = int(lm[4].x * cam_w)
#             thumb_y  = int(lm[4].y * cam_h)

#             dist = fingers_distance((index_x, index_y), (thumb_x, thumb_y))

#             if dist < 30 and not clicking:
#                 pyautogui.click()
#                 clicking = True
#             elif dist >= 30:
#                 clicking = False

#             mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#     cv2.imshow("Hand Control", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

# إعدادات ميديا بايب
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# إعدادات الشاشة والكاميرا
screen_w, screen_h = pyautogui.size()
cam_w, cam_h = 640, 480
cap = cv2.VideoCapture(1)

# متغيرات السلاسة والحالة
plocX, plocY = 0, 0
smoothening = 5
dragging = False 

print("--- البرنامج بدأ.. دوس 'q' في أي وقت عشان تقفل ---")

while True:
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # نقطة السبابة (8) ونقطة الإبهام (4)
            idx_x = hand_landmarks.landmark[8].x * cam_w
            idx_y = hand_landmarks.landmark[8].y * cam_h
            tmb_x = hand_landmarks.landmark[4].x * cam_w
            tmb_y = hand_landmarks.landmark[4].y * cam_h
            
            # 1. تحويل الإحداثيات للشاشة مع Margin
            x_mapped = np.interp(idx_x, (100, cam_w - 100), (0, screen_w))
            y_mapped = np.interp(idx_y, (100, cam_h - 100), (0, screen_h))
            
            # 2. تطبيق السلاسة (Smoothening)
            curr_x = plocX + (x_mapped - plocX) / smoothening
            curr_y = plocY + (y_mapped - plocY) / smoothening
            
            # تحريك الماوس
            pyautogui.moveTo(curr_x, curr_y)
            plocX, plocY = curr_x, curr_y
            
            # 3. حساب المسافة بين السبابة والإبهام للكليك والسحب
            distance = math.hypot(idx_x - tmb_x, idx_y - tmb_y)
            
            # منطق الـ Click والـ Drag مع الـ Terminal Logs
            if distance < 35: 
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
                    print("[ACTION] Mouse Down (Start Drag/Click) ✅")
                else:
                    # اختيارية: ممكن تشيل دي لو مش عايز زحمة في الترمينال
                    print(f"[STATUS] Dragging at ({int(curr_x)}, {int(curr_y)})...", end="\r")
            else: 
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False
                    print("\n[ACTION] Mouse Up (Drop/Release) ✋")
            
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n--- تم إيقاف البرنامج ---")
        break

cap.release()
cv2.destroyAllWindows()