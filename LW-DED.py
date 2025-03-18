from flask import jsonify
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from datetime import datetime, timedelta
import requests
import threading
import sys
import time

global running 
base_url = 'http://keties.iptime.org:53000'
# base_url = 'http://localhost:5001'
# base_url = 'http://112.222.93.10:55001'

def connection_test():
    # 서버 B로 보낼 데이터
    data = {
        'connection_status': 'success',
    }

    # 서버 B의 엔드포인트 URL    
    url = base_url + '/connection_test'

    # POST 요청으로 데이터 전송
    response = requests.post(url, json=data)
    print(response.json())


def read_csv_in_chunks(file_path, chunk_size=100):
    global running
    running = True
    df = pd.read_csv(file_path)
    for start in range(0, len(df), chunk_size):
        if running is True:
            yield df[start:start + chunk_size].to_dict(orient='records')


def StartDataStreamDED():
    # 서버 B의 엔드포인트 URL
    url = base_url + '/StartDataStreamDED'
    csv_file_path = 'Data/Processed_Sample_data.csv'
    for chunk in read_csv_in_chunks(csv_file_path):
        # POST 요청으로 데이터 전송
        response = requests.post(url, json=chunk)
        if response.status_code != 200:
            print("status: error, message: Failed to send data")
            return
        time.sleep(1)
        print("success")
        

def SendInitBuildSignal():
    url = base_url + '/SetStartBuildSignal'
    utc_now = datetime.utcnow()
    # UTC 시간을 한국 시간으로 변환 (UTC+9)
    kst_time = utc_now + timedelta(hours=9)
    current_time = kst_time.strftime('%Y%m%d_%H%M')
    data = {
        'BP_DATETIME': current_time,
        'WORKER': '지성훈'
    }
    response = requests.post(url, json=data)
    rtn = response.json()
    print(rtn['message'])


def SendFinishBuildSignal():
    url = base_url + '/SetFinishBuildSignal'
    utc_now = datetime.utcnow()
    # UTC 시간을 한국 시간으로 변환 (UTC+9)
    kst_time = utc_now + timedelta(hours=9)
    current_time = kst_time.strftime('%Y%m%d_%H%M')
    data = { 'BP_FinishTime': current_time }
    response = requests.post(url, json=data)
    rtn = response.json()
    print(rtn['message'])

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
        SendInitBuildSignal()
        self.thread = threading.Thread(target=StartDataStreamDED)
        self.thread.start()        
        
    def stop_streaming(self):
        global running
        running = False
        SendFinishBuildSignal()
        
        print("Loop stopped.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())