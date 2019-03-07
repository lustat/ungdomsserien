import sys
import PySide2
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QFileDialog,
                               QVBoxLayout, QWidget, QLineEdit, QHBoxLayout)
from PySide2.QtCore import Slot, Qt
from loader.read_results import extract_and_analyse
from PySide2.QtGui import QIcon
from loader.loader_utils import get_event_name
import os


class MyWidget(QWidget):
    def __init__(self, api_key):
        self.key = api_key
        QWidget.__init__(self)

        # 2018
        event_ids = [18218, 17412, 18308, 18106, 16981, 18995]
        night_ids = [18459, 18485]

        # 2019
        # event_ids = [20550, 21406, 21376, 21988, 21732, 21644]
        # night_ids = [21851, 21961]


        self.layout = QVBoxLayout()

        menubar = PySide2.QtWidgets.QMenuBar()
        filemenu = menubar.addMenu('Meny')

        exit_action = PySide2.QtWidgets.QAction('Avsluta', self)
        exit_action.triggered.connect(sys.exit)
        filemenu.addAction(exit_action)

        about_action = PySide2.QtWidgets.QAction('Om', self)
        about_action.triggered.connect(self.info_window)
        filemenu.addAction(about_action)

        self.layout.addWidget(menubar)

        self.setWindowIconText('Test')
        self.setWindowIcon(QIcon("run.png"))

        for k in range(6):
            Qbox = QHBoxLayout()
            w = QLineEdit(str(event_ids[k]), parent=self)
            w.setFixedWidth(120)
            w.setAlignment(Qt.AlignLeft)
            text = QLabel("Tävling " + str(k+1))
            Qbox.addWidget(w)
            Qbox.addWidget(text)
            self.layout.addLayout(Qbox)

        for k in range(2):
            Qbox = PySide2.QtWidgets.QHBoxLayout()
            text = PySide2.QtWidgets.QLabel("Natt-tävling " + str(k+1), parent=None)
            w = PySide2.QtWidgets.QLineEdit(str(night_ids[k]), parent=self)
            w.setFixedWidth(120)
            w.setAlignment(PySide2.QtCore.Qt.AlignLeft)
            Qbox.addWidget(w)
            Qbox.addWidget(text)
            self.layout.addLayout(Qbox)

        self.line = PySide2.QtWidgets.QFrame()
        self.layout.addWidget(self.line)


        self.button_getname = QPushButton("Hämta tävlingsnamn")
        self.layout.addWidget(self.button_getname)

        self.button_analyse = QPushButton("Extrahera och analysera tävlingsresultat")
        self.button_analyse.clicked.connect(self.magic)

        self.setLayout(self.layout)

        # Connecting the signal
        self.button_getname.clicked.connect(self.setnames)
        self.show()


    def info_window(self):
        msg_box = PySide2.QtWidgets.QMessageBox()
        msg_box.about(self, 'Information', 'SkofCounter Version 0.9\n'
                        'Poängberäknare för SKOF:s Ungdomsserie\n'
                        ' \n'
                       'Program icon by https://www.flaticon.com/authors/srip\n'
                       '"Flaticon" www.flaticon.com is licensed by http://creativecommons.org/licenses/by/3.0/ \n"'
                       'Creative Commons BY 3.0')

    @Slot()
    def magic(self):
        storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att lagra resultatfiler"))
        # Directory selector
        races, night_races = self.list_input_events()

        races = [race for race in races if not (race == 0)]
        night_races = [race for race in night_races if not (race == 0)]

        club_file, ind_file = extract_and_analyse(storage_path, races, night_races, self.key)
        print('Sparat: ' + club_file)
        print('Sparat: ' + ind_file)

    @Slot()
    def getnames(self):
        races, night_races = self.list_input_events()
        namelist1 = []
        for race in races:
            name, year = get_event_name(race, self.key)
            namelist1.append(name + ' (' + str(year) + ')')

        nightlist1 = []
        for night_race in night_races:
            name, year = get_event_name(night_race, self.key)
            nightlist1.append(name + ' (' + str(year) + ')')
        return namelist1, nightlist1

    def setnames(self):
        races, night_races = self.getnames()
        count = 0
        night_count = 0
        for id in self.children():
            if isinstance(id, PySide2.QtWidgets.QLabel):
                if count <= 5:
                    id.setText('Tävling: ' + str(count+1) +': ' + races[count])
                    count += 1
                else:
                    id.setText('Natt-tävling: ' + str(night_count + 1) + ': ' + night_races[night_count])
                    night_count += 1

        self.layout.addWidget(self.button_analyse)
        self.setLayout(self.layout)

    def quit_function(self):
        self.close()

    def list_input_events(self):
        events_str = [id.text() for id in self.children() if isinstance(id, PySide2.QtWidgets.QLineEdit)]
        events = []
        for e in events_str:
            if isinstance(e, str):
                if len(e) == 0:
                    events.append(0)
                else:
                    events.append(int(e))
            else:
                events.append(0)

        races = events[:6]
        night_races = events[6:]
        return races, night_races


if __name__ == "__main__":
    app = QApplication(sys.argv)
    key = input('Ange API nyckel: ')
    #key = os.environ["apikey"]
    widget = MyWidget(key)
    widget.setWindowTitle('Beräknaren: Skånes ungdomsserie')
    widget.resize(800, 300)
    widget.show()

    sys.exit(app.exec_())
