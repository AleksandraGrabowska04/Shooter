import cv2
import mediapipe as mp

# Podstawowe śledzenie dłoni

mp_hands = mp.solutions.hands   # główny moduł do wykrywania dłoni
mp_draw = mp.solutions.drawing_utils    # narzędzia do rysowania szkieletu dłoni

# Inicjalizacja kamery (0 => domyślna kamera laptop/USB)
cap = cv2.VideoCapture(0) # cap => capture_device / camera


# Zwracanie współrzędnych punktów na dłoni (Nazwy według dokumentacji MediaPipe)
LANDMARK_NAMES = [
    "WRIST",
    "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
]


def get_hand_landmarks(frame, hands, tracked_points=None, draw=False):
    """
    Zwraca współrzędne (x, y, z) wybranych punktów dłoni (jednej lub dwóch).
    
    OpenCV przekazuje klatki w tempie np. (u mnie) 30 FPS.
    Funkcja jest wywoływana dla każdej klatki i wypisuje współrzędne śledzonych punktów nawet jeśli dłoń się nie rusza.
    !!!!(Potem można zmienić ewentualnie tak, żeby wypisywać tylko przy zmianie pozycji dłoni, ale nie wiem, czy będzie potrzebne)

    Args:
        frame: klatka z kamery (np. z OpenCV)
        hands: obiekt klasy mp_hands.Hands (inicjalizowany tylko raz)
        tracked_points: lista nazw punktów do śledzenia (np. ["INDEX_FINGER_TIP", "WRIST"])
                        jeśli None → zwraca wszystkie 21 punktów
        draw: czy rysować punkty i połączenia na klatce
    
    Returns:
        hands_data: lista słowników, np.:
        [
          {"WRIST": (x, y, z), "INDEX_FINGER_TIP": (x, y, z)},
          {"WRIST": (x, y, z), "INDEX_FINGER_TIP": (x, y, z)}
        ]
    """
    hands_data = []

    # Konwersja koloru (bo OpenCV używa BGR, a MediaPipe wymaga RGB)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        h, w, _ = frame.shape
        for handLms in result.multi_hand_landmarks:
            hand_dict = {}

            # Które punkty śledzimy
            indices = range(21) if tracked_points is None else [
                LANDMARK_NAMES.index(p) for p in tracked_points if p in LANDMARK_NAMES
            ]

            for i in indices:
                lm = handLms.landmark[i]
                hand_dict[LANDMARK_NAMES[i]] = (int(lm.x * w), int(lm.y * h), lm.z)

            hands_data.append(hand_dict)

            if draw:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    # Wypisanie współrzędnych śledzonych punktów
    if hands_data:
        print("\n--- Śledzone dłonie ---")
        for idx, hand in enumerate(hands_data):
            print(f"Dłoń {idx + 1}:")
            for name, coords in hand.items():
                print(f"  {name}: x={coords[0]}  y={coords[1]}  z={coords[2]:.3f}")
    else:
        print("Brak wykrytych dłoni")

    return hands_data


"""
max_num_hands: ile dłoni chcemy śledzić

min_detection_confidence: pewność przy pierwszym wykryciu
z jakim model AI (w MediaPipe) musi uznać, że na obrazie widać dłoń, zanim rozpocznie jej śledzenie.
Wartość w zakresie 0.0 - 1.0 (czyli od 0% do 100%).
Domyślnie 0.6

min_tracking_confidence: pewność przy dalszym śledzeniu (gdy dłoń się rusza)
"""

with mp_hands.Hands(
    max_num_hands=2,         
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

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

        # Wywołanie funkcji do śledzenia punktów i wypisywania ich współrzędnych
        _ = get_hand_landmarks(frame, hands, tracked_points=["WRIST", "INDEX_FINGER_TIP"], draw=False)

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC do wyjścia
            break

cap.release()
cv2.destroyAllWindows()
