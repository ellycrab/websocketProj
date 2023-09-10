import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# 웹캠 읽어오기 (컴퓨터에 따라서 인수가 0)
cap = cv2.VideoCapture(1)

# 손 좌표 초기화
hand_x = 0
hand_y = 0

# 게임의 화면 크기 설정
GAME_WIDTH  = 1920
GAME_HEIGHT = 1080

# mediapipe의 Hands 모델을 사용해 손 인식을 시작합니다.
with mp_hands.Hands() as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # 이미지를 RGB로 변환하고 좌우 반전합니다.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # 손을 검출합니다.
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 손이 닫혔는지 판별하는 플래그 초기화
        hand_closed = False

        # 손의 랜드마크를 찾으면
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 손의 x, y 좌표를 계산합니다.
                x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
                hand_x = int(x * GAME_WIDTH)
                hand_y = GAME_HEIGHT - int(y * GAME_HEIGHT)

                # 숙제: 손이 닫혔는지 확인합니다.


                # 손의 랜드마크와 연결을 그립니다.
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        # 이미지를 화면에 표시합니다.
        cv2.imshow('preview', image)

        # ESC 키를 누르면 종료합니다.
        if cv2.waitKey(5) & 0xFF == 27:
            break

# 비디오 캡처를 종료합니다.
cap.release()