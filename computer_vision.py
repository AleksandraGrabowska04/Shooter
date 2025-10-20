import cv2
import mediapipe as mp

# Podstawowe śledzenie dłoni

mp_hands = mp.solutions.hands   # główny moduł do wykrywania dłoni
mp_draw = mp.solutions.drawing_utils    # narzędzia do rysowania szkieletu dłoni

# Inicjalizacja kamery (0 => domyślna kamera laptop/USB)
cap = cv2.VideoCapture(0) # cap => capture_device / camera

"""
max_num_hands: ile dłoni chcemy śledzić

min_detection_confidence: pewność przy pierwszym wykryciu
z jakim model AI (w MediaPipe) musi uznać, że na obrazie widać dłoń, zanim rozpocznie jej śledzenie.
Wartość w zakresie 0.0 - 1.0 (czyli od 0% do 100%).
Domyślnie 0.6

min_tracking_confidence: pewność przy dalszym śledzeniu (gdy dłoń się rusza)
"""

with mp_hands.Hands(
    max_num_hands=1,         # jedna dłoń
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6) as hands:

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # lustrzane odbicie (naturalniejsze z perspektywy gracza)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # konwersja do RGB (bo OpenCV używa BGR jako wewnętrzny format)
        result = hands.process(rgb) 

        """
        Jeśli wykryto przynajmniej jedną dłoń:
        result.multi_hand_landmarks zawiera listę obiektów z 21 punktami (landmarks) każdej dłoni.
        """

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                # Rysowanie szkieletu dłoni
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC do wyjścia
            break

cap.release()
cv2.destroyAllWindows()
