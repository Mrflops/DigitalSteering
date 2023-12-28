import math
import cv2
import mediapipe as mp
import ctypes

keys = {'w': 0x11, 'a': 0x1E, 's': 0x1F, 'd': 0x20}
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
font = cv2.FONT_HERSHEY_SIMPLEX

PUL = ctypes.POINTER(ctypes.c_ulong)

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
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Wait until the frame comes back")
                continue

            # Convert the image to RGB and process hands
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            imageHeight, imageWidth, _ = image.shape
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            co = []

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
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
                                co.append(list(pixelCoordinatesLandmark))
                            except:
                                continue

            if len(co) == 2:
                xm, ym = (co[0][0] + co[1][0]) / 2, (co[0][1] + co[1][1]) / 2
                radius = 150
                try:
                    m = (co[1][1] - co[0][1]) / (co[1][0] - co[0][0])
                except:
                    continue

                a = 1 + m ** 2
                b = -2 * xm - 2 * co[0][0] * (m ** 2) + 2 * m * co[0][1] - 2 * m * ym
                c = xm ** 2 + (m ** 2) * (co[0][0] ** 2) + co[0][1] ** 2 + ym ** 2 - 2 * co[0][1] * ym - 2 * co[0][1] * \
                    co[0][0] * m + 2 * m * ym * co[0][0] - 22500

                xa = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                xb = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                ya = m * (xa - co[0][0]) + co[0][1]
                yb = m * (xb - co[0][0]) + co[0][1]

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
                l = (int(math.sqrt((co[0][0] - co[1][0]) ** 2 * (co[0][1] - co[1][1]) ** 2)) - 150) // 2
                cv2.line(image, (int(xa), int(ya)), (int(xb), int(yb)), (195, 255, 62), 20)

                # Calculate angle in degrees
                angle_rad = math.atan2(co[1][1] - co[0][1], co[1][0] - co[0][0])
                angle_deg = math.degrees(angle_rad)

                # Steering logic based on the adjusted angle
                if -20 <= angle_deg <= 20:
                    print("Straight")
                    release_key('a')
                    release_key('d')
                    release_key('w')
                    release_key('s')
                    press_key('w')
                elif -45 <= angle_deg < -20:
                    print("Light right")
                    release_key('a')
                    release_key('d')
                    release_key('w')
                    release_key('s')
                    press_key('w')
                    press_key('d')  # Switch 'a' and 'd'
                elif -90 <= angle_deg < -45:
                    print("Hard right")
                    release_key('a')
                    release_key('d')
                    release_key('w')
                    release_key('s')
                    press_key('d')  # Keep 'd' as is
                    release_key('a')
                elif 20 <= angle_deg < 45:
                    print("Light left")
                    release_key('a')
                    release_key('d')
                    release_key('w')
                    release_key('s')
                    press_key('w')
                    press_key('a')  # Switch 'a' and 'd'
                elif 45 <= angle_deg <= 90:
                    print("Hard left")
                    release_key('a')
                    release_key('d')
                    release_key('w')
                    release_key('s')
                    press_key('a')  # Keep 'a' as is
                    release_key('d')
            else:
                # No hands detected, release all keys
                print("No hands detected")
                release_key('a')
                release_key('d')
                release_key('w')
                release_key('s')

            cv2.imshow('VIDEO HAND THING', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        # Release the video capture at the end
        cap.release()
        cv2.destroyAllWindows()
