import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class MainWindow(QMainWindow):
    g_map: QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('main_window_1-3.ui', self)
        self.press_delta = 0.00001

        self.map_zoom = 5
        self.map_ll = [30, 50]
        self.map_l = 'map'
        self.map_key = ''

        self.refresh_map()

        self.btn_scheme = QPushButton(self)
        self.btn_scheme.setText('Схема')
        self.btn_scheme.move(650, 70)
        self.btn_scheme.resize(100, 70)
        self.btn_scheme.clicked.connect(self.click1)
        self.btn_scheme.releaseKeyboard()

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

    def click1(self):
        self.map_l = 'skl'
        self.btn_scheme.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_sattel.setStyleSheet('QPushButton {background-color: white}')
        self.btn_hybr.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

    def click2(self):
        self.map_l = 'sat'
        self.btn_sattel.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_scheme.setStyleSheet('QPushButton {background-color: white}')
        self.btn_hybr.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

    def click3(self):
        self.map_l = 'map'
        self.btn_hybr.setStyleSheet('QPushButton {background-color: #A3C1DA}')
        self.btn_sattel.setStyleSheet('QPushButton {background-color: white}')
        self.btn_scheme.setStyleSheet('QPushButton {background-color: white}')
        self.refresh_map()

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
        long = [40 / (2 ** i) for i in range(15)]
        deep = [30 / (2 ** i) for i in range(15)]
        if event.key() == Qt.Key_PageUp:
            self.map_zoom = min(15, self.map_zoom + 1)
            self.refresh_map()
        elif event.key() == Qt.Key_PageDown:
            self.map_zoom = max(1, self.map_zoom - 1)
            self.refresh_map()
        elif event.key() == Qt.Key_W:
            self.map_ll[1] += deep[self.map_zoom - 1]
            if self.map_ll[1] > 85:
                self.map_ll[1] -= 170
            self.refresh_map()
        elif event.key() == Qt.Key_S:
            self.map_ll[1] -= deep[self.map_zoom - 1]
            if self.map_ll[1] < -85:
                self.map_ll[1] += 170
            self.refresh_map()
        elif event.key() == Qt.Key_D:
            self.map_ll[0] += long[self.map_zoom - 1]
            if self.map_ll[0] > 180:
                self.map_ll[0] -= 360
            self.refresh_map()
        elif event.key() == Qt.Key_A:
            self.map_ll[0] -= long[self.map_zoom - 1]
            if self.map_ll[0] < -180:
                self.map_ll[0] += 360
            self.refresh_map()
        event.accept()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
