from flask import Flask
from flask import request
import json
import pandas as pd
import csv
from socketio import Server, WSGIApp
from threading import Thread

import cv2
import mediapipe as mp

app = Flask(__name__)


def mp_process(show):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(1)

    hand_x = 0
    hand_y = 0

    with mp_hands.Hands() as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            hand_closed = False

            if results.multi_hand_landmarks:

                for hand_landmarks in results.multi_hand_landmarks:
                    x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
                    hand_x = int(x * 1920)
                    hand_y = 1080 - int(y * 1080)

                    x1, y1 = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y
                    if y1 > y:
                        hand_closed = True
                        ##print("hand closed")

                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            d = {
                'x': hand_x,
                'y': hand_y,
                'c': hand_closed
            }

            if show:
                cv2.imshow('preview', image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break
            else:
                sio.emit("hand", json.dumps(d))

    cap.release()


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/scoreget', methods=['GET'])
def scoreget():
    # score.csv 파일을 읽어 데이터프레임으로 변환
    df = pd.read_csv("./score.csv", encoding="utf-8", header=0)
    # 점수를 기준으로 내림차순 정렬
    df = df.sort_values(by='score', ascending=False)
    print(df)
    # 데이터프레임을 JSON 형태로 변환하여 반환
    return df.to_json()


@app.route('/scoresave', methods=['POST'])
def score():
    # 요청(바디)에서 점수와 이름을 가져옴
    score = request.form.get('score')
    name = request.form.get('name')
    # CSV 파일에 기록
    f = open('score.csv', 'a', newline='\n', encoding='utf-8')
    data = [name, score]
    writer = csv.writer(f)
    writer.writerow(data)
    f.close()
    # 성공 응답 반환
    return "1"


sio = Server(async_mode="threading")
app.wsgi_app = WSGIApp(sio, app.wsgi_app)


@sio.event
def connect(sid, environ, auth):
    print('connect ', sid)
    sio.emit('test', {'data': 'Connected'})


import multiprocessing


if __name__ == "__main__":
    t1 = Thread(target=mp_process, args=[False])
    t1.daemon = True
    t1.start()
    display_process = multiprocessing.Process(target=mp_process, args=[True])
    display_process.start()
    app.run(host='0.0.0.0', port='7711', debug=True, threaded=True)
