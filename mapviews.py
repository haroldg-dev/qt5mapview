# test data
# -12.070972, -77.034917
# -12.071115, -77.035363
# -12.070247, -77.033177 
# -12.069478, -77.034116
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QLabel, QWidget, QLineEdit, QTextBrowser, QPushButton, QVBoxLayout, QGraphicsPathItem
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine

import csv
import io
import folium # pip install folium
import sys

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.chosen_points = []
        self.initUI()

    def initUI(self):
        """Se define los elementos de la interfaz grafica"""

        # 1 element
        self.le = QLineEdit()
        self.le.returnPressed.connect(self.append_text)
        
        # 2 element 
        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.setOpenExternalLinks(True)

        # 3 element
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.pressed.connect(self.clear_text)

        # 4 element
        self.save_data = QPushButton('Guardar Data')
        self.save_data.pressed.connect(self.save_all_data)

        # 5 element
        self.delete_marker = QPushButton('Eliminar Marcadores')
        self.delete_marker.pressed.connect(self.delete_marker_map)

        # 6 element
        coordinate = (-12.070831, -77.033788)
        self.m = folium.Map(
        	tiles='Stamen Terrain',
        	zoom_start=17,
        	location=coordinate
        )

        data = io.BytesIO()
        self.m.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())

        # box
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.le, 0)
        self.vbox.addWidget(self.tb, 1)
        self.vbox.addWidget(self.clear_btn, 2)
        self.vbox.addWidget(self.save_data, 3)
        self.vbox.addWidget(self.delete_marker, 4)
        self.vbox.addWidget(self.webView, 5)

        self.setLayout(self.vbox)
        self.setWindowTitle('Detector de Anomalias')
        self.setGeometry(600, 700, 600, 700)
        self.center_app()
        self.show()
    
    def center_app(self):
        """Inicializa la app en el centro de la pantalla"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def append_text(self):
        """Agrega los datos en el visualizador de coordenadas"""
        text = self.le.text()
        self.tb.append(text)
        
        # add marker
        self.update_map(text)

        #delete info
        self.le.clear()

    def clear_text(self):
        """Limpia el visualizador de coordenadas"""
        self.tb.clear()

    def update_map(self,coordinate):
        """Actualiza el mapa con los puntos del gps"""
        coordinate = coordinate.split(',')
        first = float(coordinate[0])
        second = float(coordinate[1])
        coordinate = [first,second]
        self.chosen_points.append(coordinate)

        self.vbox.removeWidget(self.webView)

        coordinate = (-12.070831, -77.033788)
        self.m = folium.Map(
        	tiles='Stamen Terrain',
        	zoom_start=17,
        	location=coordinate
        )

        for coordinate in self.chosen_points:
            self.m.add_child(folium.Marker(location = coordinate, icon = folium.Icon(color='red')))

        data = io.BytesIO()
        self.m.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())
        self.vbox.addWidget(self.webView, 5)

        # self.vbox.update()
        # self.update()
    def delete_marker_map(self):
        """Elimina todos los marcadores del mapa"""
        self.vbox.removeWidget(self.webView)
        coordinate = (-12.070831, -77.033788)
        self.m = folium.Map(
        	tiles='Stamen Terrain',
        	zoom_start=17,
        	location=coordinate
        )
        data = io.BytesIO()
        self.m.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())
        self.vbox.addWidget(self.webView, 5)
    
    def save_all_data(self):
        """Guarda todos los valores del visualizador de data
        en un archivos csv"""
        data_header = ['first','second']
        data_body = []

        text = self.tb.toPlainText()
        text_list = text.split('\n')

        for line in text_list:
            line_data = {
                'first': line.split(',')[0],
                'second': line.split(',')[1],
            }
            data_body.append(line_data)

        with open('gps.csv', 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data_header)
            writer.writeheader()
            writer.writerows(data_body)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())