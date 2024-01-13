import time
import math
import cv2
import mediapipe as mp
import ctypes

keys = {'w': 0x11, 'a': 0x1E, 's': 0x1F, 'd': 0x20}
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

font = cv2.FONT_HERSHEY_SIMPLEX
bkwrds = 0
PUL = ctypes.POINTER(ctypes.c_ulong)
swap_triggered = {'left': False, 'right': False}

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

def press_key(key):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, keys[key], 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(key):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, keys[key], 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Initialize the video capture outside the loop to avoid reopening it every iteration
cap = cv2.VideoCapture(0)  # Change based on your Camera
hands_detected = False
last_swap_time = time.time()

with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:
    try:
        swap_delay = 0.5  # Increase swap delay for smoother control
        sensitivity_factor = 1  # Adjust this factor for sensitivity control 0.1 to 2 --- Degree of angle / sensitivity_factor
        degrees_offset = 0 #Adjust this offset for angle offset negative or positive

        while cap.isOpened():
            current_time = time.time()
            elapsed_time_since_last_swap = current_time - last_swap_time

            success, image = cap.read()
            if not success:
                print("Error reading frame. Exiting...")
                break

            # Convert the image to RGB and process hands
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            imageHeight, imageWidth, _ = image.shape
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            co = []

            if results.multi_hand_landmarks:
                hands_detected = True
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    for point in mp_hands.HandLandmark:
                        if str(point) == "HandLandmark.WRIST":
                            normalizedLandmark = hand_landmarks.landmark[point]
                            pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(
                                normalizedLandmark.x,
                                normalizedLandmark.y,
                                imageWidth, imageHeight)
                            try:
                                co.append((i, list(pixelCoordinatesLandmark)))
                            except:
                                continue
            else:
                hands_detected = False

            if hands_detected:
                if len(co) == 2:
                    xm, ym = (co[0][1][0] + co[1][1][0]) / 2, (co[0][1][1] + co[1][1][1]) / 2
                    radius = 150

                    try:
                        if co[1][1][0] - co[0][1][0] != 0:
                            m = (co[1][1][1] - co[0][1][1]) / (co[1][1][0] - co[0][1][0])
                        else:
                            # Avoid division by zero
                            continue
                    except ZeroDivisionError:
                        # Avoid division by zero
                        continue

                    a = 1 + m ** 2
                    b = -2 * xm - 2 * co[0][1][0] * (m ** 2) + 2 * m * co[0][1][1] - 2 * m * ym
                    c = xm ** 2 + (m ** 2) * (co[0][1][0] ** 2) + co[0][1][1] ** 2 + ym ** 2 - 2 * co[0][1][1] * ym - 2 * co[0][1][1] * \
                        co[0][1][0] * m + 2 * m * ym * co[0][1][0] - 22500

                    xa = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                    xb = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                    ya = m * (xa - co[0][1][0]) + co[0][1][1]
                    yb = m * (xb - co[0][1][0]) + co[0][1][1]

                    if m != 0:
                        ap = 1 + ((-1 / m) ** 2)
                        bp = -2 * xm - 2 * xm * ((-1 / m) ** 2) + 2 * (-1 / m) * ym - 2 * (-1 / m) * ym
                        cp = xm ** 2 + ((-1 / m) ** 2) * (xm ** 2) + ym ** 2 + ym ** 2 - 2 * ym * ym - 2 * ym * xm * (
                                -1 / m) + 2 * (-1 / m) * ym * xm - 22500

                        try:
                            xap = (-bp + (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                            xbp = (-bp - (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                            yap = (-1 / m) * (xap - xm) + ym
                            ybp = (-1 / m) * (xbp - xm) + ym
                        except:
                            continue

                        cv2.circle(img=image, center=(int(xm), int(ym)), radius=radius, color=(195, 255, 62), thickness=15)
                        l = (int(math.sqrt((co[0][1][0] - co[1][1][0]) ** 2 * (co[0][1][1] - co[1][1][1]) ** 2)) - 150) // 2
                        cv2.line(image, (int(xa), int(ya)), (int(xb), int(yb)), (195, 255, 62), 20)

                        # Calculate angle in degrees
                        angle_rad = math.atan2(co[1][1][1] - co[0][1][1], co[1][1][0] - co[0][1][0])
                        angle_deg = math.degrees(angle_rad) + degrees_offset  # Add offset

                        # Steering logic based on the adjusted angle
                        angle_rad = math.atan2(co[0][1][1] - co[1][1][1], co[0][1][0] - co[1][1][0])
                        angle_deg = math.degrees(angle_rad) + degrees_offset  # Add offset

                        # Adjust sensitivity
                        adjusted_sensitivity = angle_deg * sensitivity_factor

                        if bkwrds == 0:
                            if -15 <= adjusted_sensitivity <= 15:
                                print("Straight")
                                press_key('w')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            if -30 <= adjusted_sensitivity <= -15:
                                print("WWWD")
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('d')
                                release_key('d')
                                release_key('a')
                                release_key('s')
                            if -45 <= adjusted_sensitivity <= -30:
                                print("WWD")
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('d')
                                release_key('d')
                                release_key('a')
                                release_key('s')
                            elif -60 <= adjusted_sensitivity < -45:
                                print("Middle right")
                                press_key('w')
                                press_key('d')
                                release_key('a')
                                release_key('s')
                            if -75 <= adjusted_sensitivity <= -60:
                                print("WDD")
                                press_key('w')
                                release_key('w')
                                press_key('d')
                                release_key('d')
                                press_key('d')
                                release_key('d')
                                release_key('a')
                                release_key('s')
                            elif -90 <= adjusted_sensitivity < -75: # RIGHT STOPS
                                print("D")
                                press_key('d')
                                release_key('w')
                                release_key('a')
                                release_key('s')
                            if 15 <= adjusted_sensitivity <= 30:
                                print("WWWA")
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            if 30 <= adjusted_sensitivity <= 45:
                                print("WWA")
                                press_key('w')
                                release_key('w')
                                press_key('w')
                                release_key('w')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            elif 45 <= adjusted_sensitivity < 60:
                                print("WA")
                                press_key('w')
                                press_key('a')
                                release_key('d')
                                release_key('s')
                            if 60 <= adjusted_sensitivity <= 75:
                                print("WAA")
                                press_key('w')
                                release_key('w')
                                press_key('a')
                                release_key('a')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            elif 75 <= adjusted_sensitivity < 90: # RIGHT STOPS
                                print("A")
                                press_key('a')
                                release_key('w')
                                release_key('d')
                                release_key('s')
                        elif bkwrds == 1:
                            if -15 <= adjusted_sensitivity <= 15:
                                print("S")
                                press_key('s')
                                release_key('a')
                                release_key('d')
                                release_key('w')
                            if -30 <= adjusted_sensitivity <= -15:
                                print("SSSA")
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            if -45 <= adjusted_sensitivity <= -30:
                                print("SSA")
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('w')
                            elif -60 <= adjusted_sensitivity < -45:
                                print("SA")
                                press_key('s')
                                press_key('a')
                                release_key('d')
                                release_key('w')
                            if -75 <= adjusted_sensitivity <= -60:
                                print("SAA")
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('w')
                            elif -90 <= adjusted_sensitivity < -75:  # RIGHT STOPS
                                print("A")
                                press_key('a')
                                release_key('w')
                                release_key('a')
                                release_key('s')
                            if 15 <= adjusted_sensitivity <= 30:
                                print("SSSA")
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('w')
                            if 30 <= adjusted_sensitivity <= 45:
                                print("SSA")
                                press_key('s')
                                release_key('s')
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('w')
                            elif 45 <= adjusted_sensitivity < 60:
                                print("SA")
                                press_key('s')
                                press_key('a')
                                release_key('d')
                                release_key('w')
                            if 60 <= adjusted_sensitivity <= 75:
                                print("SAA")
                                press_key('s')
                                release_key('s')
                                press_key('a')
                                release_key('a')
                                press_key('a')
                                release_key('a')
                                release_key('d')
                                release_key('s')
                            elif 75 <= adjusted_sensitivity < 90:  # RIGHT STOPS
                                print("A")
                                press_key('a')
                                release_key('w')
                                release_key('a')
                                release_key('s')

                        swap_triggered['left'] = True
                        swap_triggered['right'] = True

                        # Update the time of the last swap
                        last_swap_time = time.time()

                elif len(co) == 1:
                    hand_idx, _ = co[0]
                    if not swap_triggered['left'] and not swap_triggered['right']:
                        if elapsed_time_since_last_swap >= swap_delay:
                            print("Swapped direction!")
                            bkwrds = 1 if bkwrds == 0 else 0
                            release_key('a')
                            release_key('d')
                            release_key('w')
                            release_key('s')
                            swap_triggered['left'] = True if hand_idx == 0 else False
                            swap_triggered['right'] = True if hand_idx == 1 else False
            else:
                # No hands detected, release all keys
                release_key('a')
                release_key('d')
                release_key('w')
                release_key('s')
                swap_triggered['left'] = False
                swap_triggered['right'] = False

            cv2.imshow('Steering', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # Release the video capture at the end
        cap.release()
        cv2.destroyAllWindows()
        