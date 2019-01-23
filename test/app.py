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
        # self.text = QLabel("Tävlings-ID")
        # self.text.setAlignment(Qt.AlignLeft)
        # self.layout.addWidget(self.text)

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
        # self.event = []
        # self.buttongroup = PySide2.QtWidgets.QButtonGroup()
        # self.name = []
        #
        # for k in range(6):
        #     add_layout = QHBoxLayout()
        #     lbl1 = QLabel("Tävling : " + str(k+1))
        #     self.event.append(QLineEdit())
        #     self.event[k].setFixedWidth(120)
        #     self.event[k].setText(str(event_ids[k]))
        #     self.buttongroup.addButton(QPushButton(), k+1)
        #     self.name.append(QLabel("?"))
        #     add_layout.addWidget(lbl1)
        #     add_layout.setSpacing(100)
        #     add_layout.addWidget(self.event[k])
        #     add_layout.addWidget(self.buttongroup.button(k+1))
        #     add_layout.addWidget(self.name[k])
        #     self.layout.addLayout(add_layout, stretch=False)
        #     self.buttongroup.button(k + 1).clicked.connect(self.button_pressed)

        # add_layout = QHBoxLayout()
        # lbl2 = QLabel("Tävling 2: ")
        # self.event2 = QLineEdit()
        # self.event2.setFixedWidth(120)
        # self.event2.setText(str(event_ids[1]))
        # self.button2 = QPushButton("Hämta namn")
        # self.button2.race = 2
        # self.name2 = QLabel("?")
        # add_layout.addWidget(lbl2)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.event2)
        # add_layout.addWidget(self.button2)
        # add_layout.addWidget(self.name2)
        # self.layout.addLayout(add_layout, stretch=False)
        #
        # add_layout = QHBoxLayout()
        # lbl3 = QLabel("Tävling 3: ")
        # self.event3 = QLineEdit()
        # self.event3.setFixedWidth(120)
        # self.event3.setText(str(event_ids[2]))
        # self.button3 = QPushButton("Hämta namn")
        # self.button3.race = 3
        # self.name3 = QLabel("?")
        # add_layout.addWidget(lbl3)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.event3)
        # add_layout.addWidget(self.button3)
        # add_layout.addWidget(self.name3)
        # self.layout.addLayout(add_layout, stretch=False)
        #
        # add_layout = QHBoxLayout()
        # lbl4 = QLabel("Tävling 4: ")
        # self.event4 = QLineEdit()
        # self.event4.setFixedWidth(120)
        # self.event4.setText(str(event_ids[3]))
        # self.button4 = QPushButton("Hämta namn")
        # self.name4 = QLabel("?")
        # add_layout.addWidget(lbl4)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.event4)
        # add_layout.addWidget(self.button4)
        # add_layout.addWidget(self.name4)
        # self.layout.addLayout(add_layout, stretch=False)
        #
        # add_layout = QHBoxLayout()
        # lbl5 = QLabel("Tävling 5: ")
        # self.event5 = QLineEdit()
        # self.event5.setFixedWidth(120)
        # self.event5.setText(str(event_ids[4]))
        # self.button5 = QPushButton("Hämta namn")
        # self.name5 = QLabel("?")
        # add_layout.addWidget(lbl5)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.event5)
        # add_layout.addWidget(self.button5)
        # add_layout.addWidget(self.name5)
        # self.layout.addLayout(add_layout, stretch=False)
        #
        # add_layout = QHBoxLayout()
        # lbl6 = QLabel("Tävling 6: ")
        # self.event6 = QLineEdit()
        # self.event6.setFixedWidth(120)
        # self.event6.setText(str(event_ids[5]))
        # self.button6 = QPushButton("Hämta namn")
        # self.button6.id = 6
        # self.name6 = QLabel("?")
        # add_layout.addWidget(lbl6)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.event6)
        # add_layout.addWidget(self.button6)
        # add_layout.addWidget(self.name6)
        # self.layout.addLayout(add_layout, stretch=False)

        self.line = PySide2.QtWidgets.QFrame()
        self.layout.addWidget(self.line)

        # add_layout = QHBoxLayout()
        # lbl = QLabel("Natt-tävling 1: ")
        # self.night1 = QLineEdit()
        # self.night1.setFixedWidth(120)
        # self.night1.setText(str(night_ids[0]))
        # self.button_n1 = QPushButton("Hämta namn")
        # self.name_n1 = QLabel("?")
        # add_layout.addWidget(lbl)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.night1)
        # add_layout.addWidget(self.button_n1)
        # add_layout.addWidget(self.name_n1)
        # self.layout.addLayout(add_layout, stretch=False)
        #
        # add_layout = QHBoxLayout()
        # lbl = QLabel("Natt-tävling 2: ")
        # self.night2 = QLineEdit()
        # self.night2.setFixedWidth(120)
        # self.night2.setText(str(night_ids[1]))
        # self.button_n2 = QPushButton("Hämta namn")
        # self.name_n2 = QLabel("?")
        # add_layout.addWidget(lbl)
        # add_layout.setSpacing(100)
        # add_layout.addWidget(self.night2)
        # add_layout.addWidget(self.button_n2)
        # add_layout.addWidget(self.name_n2)
        # self.layout.addLayout(add_layout, stretch=False)

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
        self.show()


    @Slot()
    def magic(self):
        storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att lagra resultatfiler"))
        self.output1.setText("Analyserar...")
        # Directory selector
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

        races = [race for race in races if not (race == 0)]
        night_races = [race for race in night_races if not (race == 0)]

        club_file, ind_file = extract_and_analyse(storage_path, races, night_races, self.key)
        self.output1.setText('Sparat: ' + club_file)
        self.output2.setText('Sparat: ' + ind_file)


    def button_getname(self):
        self.name1.setText(get_event_name(self.event1))

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