from flask import Flask
import pandas as pd
import csv
from flask import request

app = Flask(__name__)

# 127.0.0.1:7711에서 접속 시 "Hello World!"를 반환하는 라우트
@app.route("/")
def hello():
	return "Hello World!"


# 127.0.0.1:7711/scoreget에서 접속 시 CSV 파일에서 점수를 읽어 정렬 후 JSON 형태로 반환
@app.route('/scoreget', methods=['GET'])
def scoreGet():
    # score.csv 파일을 읽어 데이터프레임으로 변환
    df = pd.read_csv("./score.csv", encoding="utf-8", header=0)
    # 점수를 기준으로 내림차순 정렬
    df = df.sort_values(by='score', ascending=False)
    print(df)
    # 데이터프레임을 JSON 형태로 변환하여 반환
    return df.to_json()


# 127.0.0.1:7711/scoresave에서 접속 시 폼에서 받은 점수와 이름을 CSV 파일에 저장
@app.route('/scoresave', methods=['POST'])
def score():
    # 요청(바디)에서 점수와 이름을 가져옴
    score = request.form.get('score')
    name = request.form.get('name')
    # CSV 파일에 기록
    f = open('./score.csv', 'a', newline='\n',encoding='utf-8')
    data = [name,score]
    writer = csv.writer(f)
    writer.writerow(data)
    f.close()
    # 성공 응답 반환
    return "1"


# Flask 앱을 호스트 0.0.0.0의 포트 7711에서 실행, 디버그 모드와 멀티 스레딩 활성화
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='7711', debug=True, threaded=True)