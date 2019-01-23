import sys
import PySide2
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QFileDialog,
                               QVBoxLayout, QWidget, QLineEdit, QHBoxLayout)
from PySide2.QtCore import Slot, Qt
from loader.read_results import extract_and_analyse
from PySide2.QtGui import QIcon
from loader.loader_utils import get_event_name


class MyWidget(QWidget):
    def __init__(self, api_key):
        self.key = api_key
        QWidget.__init__(self)

        event_ids = [18218, 17412, 18308, 18106, 16981, 18995]
        night_ids = [18459, 18485]

        self.layout = QVBoxLayout()
        self.setWindowIconText('Test')
        self.setWindowIcon(QIcon("run.png"))

        for k in range(6):
            Qbox = QHBoxLayout()
            text = QLabel("Tävling " + str(k+1))
            name = QLabel(" ")

            w = QLineEdit(str(event_ids[k]), parent=self)
            w.setFixedWidth(120)
            w.setAlignment(Qt.AlignLeft)
            Qbox.addWidget(text)
            Qbox.addWidget(w)
            Qbox.addWidget(name)
            self.layout.addLayout(Qbox)

        for k in range(2):
            Qbox = PySide2.QtWidgets.QHBoxLayout()
            text = PySide2.QtWidgets.QLabel("Natt-tävling " + str(k+1))
            name = PySide2.QtWidgets.QLabel(" ")
            w = PySide2.QtWidgets.QLineEdit(str(night_ids[k]), parent=self)
            w.setFixedWidth(120)
            w.setAlignment(PySide2.QtCore.Qt.AlignLeft)
            Qbox.addWidget(text)
            Qbox.addWidget(w)
            Qbox.addWidget(name)
            self.layout.addLayout(Qbox)

        self.line = PySide2.QtWidgets.QFrame()
        self.layout.addWidget(self.line)

        self.output1 = QLabel("--Inget analyserat än--")
        self.output1.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output1)

        self.output2 = QLabel(" ")
        self.output2.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output2)

        self.button_getname = QPushButton("Hämta tävlingsnamn")
        self.layout.addWidget(self.button_getname)

        self.button_analyse = QPushButton("Extrahera och analysera tävlingsresultat")
        self.layout.addWidget(self.button_analyse)

        self.setLayout(self.layout)

        # Connecting the signal
        self.button_analyse.clicked.connect(self.magic)
        self.button_getname.clicked.connect(self.getnames)
        self.show()


    @Slot()
    def magic(self):
        storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att lagra resultatfiler"))
        self.output1.setText("Analyserar...")
        # Directory selector
        races, night_races = self.list_input_events()

        races = [race for race in races if not (race == 0)]
        night_races = [race for race in night_races if not (race == 0)]

        club_file, ind_file = extract_and_analyse(storage_path, races, night_races, self.key)
        self.output1.setText('Sparat: ' + club_file)
        self.output2.setText('Sparat: ' + ind_file)

    @Slot()
    def getnames(self):
        self.output1.setText("Hämtar namn...")
        races, night_races = self.list_input_events()
        for race in races:
            name, year = get_event_name(race, self.key)
            print(name + ' (' + str(year) + ')')

        self.output1.setText("Namn hämtade")

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
    widget = MyWidget(key)
    widget.setWindowTitle('Beräknaren: Skånes ungdomsserie')
    widget.resize(800, 300)
    widget.show()

    sys.exit(app.exec_())

    # < div > Icons
    # made
    # by < a
    # href = "https://www.flaticon.com/authors/srip"
    # title = "srip" > srip < / a >
    # from < a
    # href = "https://www.flaticon.com/"
    # title = "Flaticon" > www.flaticon.com < / a > is licensed
    # by < a
    # href = "http://creativecommons.org/licenses/by/3.0/"
    # title = "Creative Commons BY 3.0"
    # target = "_blank" > CC
    # 3.0
    # BY < / a > < / div >