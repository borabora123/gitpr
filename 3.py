import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
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
        if event.key() == Qt.Key_PageUp:
            self.map_zoom = min(15, self.map_zoom + 1)
            self.refresh_map()
        if event.key() == Qt.Key_PageDown:
            self.map_zoom = max(1, self.map_zoom - 1)
            self.refresh_map()
        if event.key() == Qt.Key_Up:
            self.map_ll[1] += 1 / self.map_zoom ** 1.6
            self.refresh_map()
        if event.key() == Qt.Key_Down:
            self.map_ll[1] -= 1 / self.map_zoom ** 1.6
            self.refresh_map()
        if event.key() == Qt.Key_Right:
            self.map_ll[0] += 1 / self.map_zoom ** 1.6
            self.refresh_map()
        if event.key() == Qt.Key_Left:
            self.map_ll[0] -= 1 / self.map_zoom ** 1.6
            self.refresh_map()
        event.accept()



app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
