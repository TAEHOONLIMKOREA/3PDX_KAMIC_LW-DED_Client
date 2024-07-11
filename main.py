from flask import jsonify
from modules import InfluxHepler
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import requests
import threading
import sys
import time


flask_app = Flask(__name__)

global running 

def connection_test():
    # 서버 B로 보낼 데이터
    data = {
        'key1': 'value1',
        'key2': 'value2'
    }

    # 서버 B의 엔드포인트 URL
    url = 'http://localhost:5001/receive_data'

    # POST 요청으로 데이터 전송
    response = requests.post(url, json=data)
    print("Send data")

    return jsonify({
        'status': 'success',
        'response_from_server_b': response.json()
    })


def read_csv_in_chunks(file_path, chunk_size=100):
    df = pd.read_csv(file_path)
    for start in range(0, len(df), chunk_size):
        yield df[start:start + chunk_size].to_dict(orient='records')


def send_DED_data():
    # 서버 B의 엔드포인트 URL
    url = 'http://localhost:5000/InputDataDED'
    csv_file_path = 'Data/Processed_Sample_data.csv'
    for chunk in read_csv_in_chunks(csv_file_path):
        # POST 요청으로 데이터 전송
        response = requests.post(url, json=chunk)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Failed to send data"}), 500
        time.sleep(1)
        print("success")


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        self.send_data_button = QPushButton('API TEST', self)
        self.send_data_button.clicked.connect(self.send_test_data)
        vbox.addWidget(self.send_data_button)
        
        self.start_button = QPushButton('Start Streaming', self)
        self.start_button.clicked.connect(self.start_streaming)
        vbox.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Streaming', self)
        self.stop_button.clicked.connect(self.stop_streaming)
        vbox.addWidget(self.stop_button)

        self.setLayout(vbox)
        self.setWindowTitle('Start/Stop Loop Example')
        self.setGeometry(300, 300, 300, 200)

    def send_test_data(self):
        connection_test()

    def start_streaming(self):
        self.thread = threading.Thread(target=send_DED_data)
        self.thread.start()
        
        
    def stop_streaming(self):
        
        
        
        
        print("Loop stopped.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())