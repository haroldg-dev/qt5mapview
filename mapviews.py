# test data
# -12.070972, -77.034917
# -12.071115, -77.035363
# -12.070247, -77.033177
# -12.069478, -77.034116
# -12.075757833333334, -77.00004533333333
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QComboBox, QTextBrowser, QPushButton, QVBoxLayout, QLabel, QStatusBar, QMessageBox, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView  # pip install PyQtWebEngine
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QTextStream
import csv
import io
import folium  # pip install folium
import sys


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.port = QSerialPort()
        self.chosen_points = []
        self.initUI()

    def initUI(self):
        """Se define los elementos de la interfaz grafica"""
        self.data = []
        self.straux = ""
        # 1 element
        self.portNames = QComboBox(self)
        self.portNames.addItems([port.portName()
                                for port in QSerialPortInfo().availablePorts()])

        self.portOpenButton = QPushButton('CONECTAR')
        self.portOpenButton.setCheckable(True)
        self.portOpenButton.clicked.connect(self.portOpen)
        self.port.readyRead.connect(self.readFromPort)

        # 2 element
        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.setOpenExternalLinks(True)

        # 3 element
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.pressed.connect(self.clear_text)

        # 4 element
        self.save_data = QPushButton("Guardar Data")
        self.save_data.pressed.connect(self.save_all_data)

        # 5 element
        self.delete_marker = QPushButton("Eliminar Marcadores")
        self.delete_marker.pressed.connect(self.delete_marker_map)

        # 6 element
        coordinate = (-12.070831, -77.033788)
        self.m = folium.Map(tiles="Stamen Terrain",
                            zoom_start=17, location=coordinate)

        data = io.BytesIO()
        self.m.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())

        # box
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.portNames, 0)
        self.vbox.addWidget(self.portOpenButton, 1)
        self.vbox.addWidget(self.tb, 2)
        self.vbox.addWidget(self.clear_btn, 3)
        self.vbox.addWidget(self.save_data, 4)
        self.vbox.addWidget(self.delete_marker, 5)
        self.vbox.addWidget(self.webView, 6)

        self.setLayout(self.vbox)
        self.setWindowTitle("Detector de Anomalias")
        self.setGeometry(600, 700, 600, 700)
        self.center_app()
        self.show()

    def portOpen(self, flag):
        if flag:
            self.port.setBaudRate(9600)
            self.port.setPortName("COM3")
            self.port.setDataBits(8)
            self.port.setParity(0)
            r = self.port.open(QIODevice.ReadWrite)
            if not r:
                self.portOpenButton.setChecked(False)
                print('Port Error')
            else:
                print('Port opened')
        else:
            self.port.close()
            self.statusText.setText('Port closed')
            self.toolBar.serialControlEnable(True)

    def readFromPort(self):
        char = self.port.readAll()
        x = str(char, 'utf-8')
        if x != "%" and x != ",":
            self.straux = self.straux + x
        elif x == ",":
            self.data.append(self.straux)
            self.straux = ""
        elif x == "%":
            self.data.append(self.straux)
            self.straux = ""
            print(self.data)
            self.append_text()

    def center_app(self):
        """Inicializa la app en el centro de la pantalla"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def append_text(self):
        """Agrega los datos en el visualizador de coordenadas"""
        text = self.data[0]+","+self.data[1]
        self.tb.append(text)

        # add marker
        self.update_map(text)

        # delete info
        self.data = []

    def clear_text(self):
        """Limpia el visualizador de coordenadas"""
        self.tb.clear()

    def update_map(self, coordinate):
        """Actualiza el mapa con los puntos del gps"""
        coordinate = coordinate.split(",")
        self.first = float(coordinate[0])
        self.second = float(coordinate[1])
        coordinate = [self.first, self.second]
        self.chosen_points.append(coordinate)
        punto_promedio_x = 0
        punto_promedio_y = 0
        numero_puntos = len(self.chosen_points)

        # promedio de puntos leidos
        for point in self.chosen_points:
            punto_promedio_x += point[0]
            punto_promedio_y += point[1]

        punto_promedio_x = round(punto_promedio_x / numero_puntos, 6)
        punto_promedio_y = round(punto_promedio_y / numero_puntos, 6)

        self.vbox.removeWidget(self.webView)

        coordinate = (punto_promedio_x, punto_promedio_y)
        self.m = folium.Map(tiles="Stamen Terrain",
                            zoom_start=17, location=coordinate)

        for coordinate in self.chosen_points:
            self.m.add_child(folium.Marker(
                location=coordinate, icon=folium.Icon(color="red")))

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
        coordinate = (self.first, self.second)
        self.m = folium.Map(tiles="Stamen Terrain",
                            zoom_start=17, location=coordinate)
        data = io.BytesIO()
        self.m.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())
        self.vbox.addWidget(self.webView, 5)

    def save_all_data(self):
        """Guarda todos los valores del visualizador de data
        en un archivos csv"""
        data_header = ["first", "second"]
        data_body = []

        text = self.tb.toPlainText()
        text_list = text.split("\n")

        try:
            path =  QFileDialog.getExistingDirectory(
                self,
                caption='Seleccionar un Directorio'
            )
            for line in text_list:
                line_data = {
                    "first": line.split(",")[0],
                    "second": line.split(",")[1],
                }
                data_body.append(line_data)
            with open(f"{path}/gps.csv", "w", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data_header)
                writer.writeheader()
                writer.writerows(data_body)
        except IndexError:
            QMessageBox.about(self, "Error", "No se encontro ningun dato")
            
if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
