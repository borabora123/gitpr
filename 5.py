import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QLineEdit
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class MainWindow(QMainWindow):
    g_map: QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('main_window.ui', self)
        self.press_delta = 0.00001
        self.map_zoom = 1
        self.map_ll = [39.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''
        self.geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва, Красная пл-дь, 1&format=json"
        self.setGeometry(300, 300, 1000, 700)

        self.adress = QLineEdit(self)
        self.adress.move(30, 600)
        self.adress.resize(200,40)

        self.btn_find = QPushButton(self)
        self.btn_find.setText('Искать')
        self.btn_find.move(700, 580)
        self.btn_find.resize(200, 110)
        self.btn_find.clicked.connect(self.find)

        self.btn_scheme = QPushButton(self)
        self.btn_scheme.setText('Схема')
        self.btn_scheme.move(650, 70)
        self.btn_scheme.resize(100, 70)
        self.btn_scheme.clicked.connect(self.click1)

        self.btn_sattel = QPushButton(self)
        self.btn_sattel.setText('Спутник')
        self.btn_sattel.move(650, 250)
        self.btn_sattel.resize(100, 70)
        self.btn_sattel.clicked.connect(self.click2)

        self.btn_hybr = QPushButton(self)
        self.btn_hybr.setText('Гибрид')
        self.btn_hybr.move(650, 430)
        self.btn_hybr.resize(100, 70)
        self.btn_hybr.clicked.connect(self.click3)

        self.refresh_map()

    def click1(self):
        self.map_l = 'map'
        self.btn_scheme.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_sattel.setStyleSheet('QPushButton {background-color: white}')
        self.btn_hybr.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

    def click2(self):
        self.map_l = 'skl'
        self.btn_sattel.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_scheme.setStyleSheet('QPushButton {background-color: white}')
        self.btn_hybr.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

    def click3(self):
        self.map_l = 'sat'
        self.btn_hybr.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_sattel.setStyleSheet('QPushButton {background-color: white}')
        self.btn_scheme.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

    def find(self):
        self.geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={self.adress.text()}&format=json"
        response = requests.get(self.geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            toponym_coodrinates = toponym["Point"]["pos"]
            print(type(toponym_coodrinates))
            self.map_ll = toponym_coodrinates.split()
            self.refresh_map()
        else:
            print("Ошибка выполнения запроса:")
            print(self.geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def refresh_map(self):
        map_params = {
            "ll": ','.join(map(str, self.map_ll)),
            "l": self.map_l,
            'z': self.map_zoom
        }
        session = requests.Session()
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get('https://static-maps.yandex.ru/1.x/',
                               params=map_params)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.map_zoom = min(15, self.map_zoom + 1)
            self.refresh_map()
        elif event.key() == Qt.Key_PageDown:
            self.map_zoom = max(1, self.map_zoom - 1)
            self.refresh_map()
        elif event.key() == Qt.Key_W:
            self.map_ll[1] += 1 / self.map_zoom ** 1.6
            self.refresh_map()
        elif event.key() == Qt.Key_S:
            self.map_ll[1] -= 1 / self.map_zoom ** 1.6
            self.refresh_map()
        elif event.key() == Qt.Key_D:
            self.map_ll[0] += 1 / self.map_zoom ** 1.6
            self.refresh_map()
        elif event.key() == Qt.Key_A:
            self.map_ll[0] -= 1 / self.map_zoom ** 1.6
            self.refresh_map()
        event.accept()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
