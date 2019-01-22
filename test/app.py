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

        add_layout = QHBoxLayout()
        lbl1 = QLabel("Tävling 1: ")
        self.event1 = QLineEdit()
        self.event1.setFixedWidth(120)
        self.event1.setText(str(event_ids[0]))
        self.button1 = QPushButton("Hämta namn")
        self.name1 = QLabel("?")
        add_layout.addWidget(lbl1)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event1)
        add_layout.addWidget(self.button1)
        add_layout.addWidget(self.name1)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl2 = QLabel("Tävling 2: ")
        self.event2 = QLineEdit()
        self.event2.setFixedWidth(120)
        self.event2.setText(str(event_ids[1]))
        self.button2 = QPushButton("Hämta namn")
        self.name2 = QLabel("?")
        add_layout.addWidget(lbl2)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event2)
        add_layout.addWidget(self.button2)
        add_layout.addWidget(self.name2)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl3 = QLabel("Tävling 3: ")
        self.event3 = QLineEdit()
        self.event3.setFixedWidth(120)
        self.event3.setText(str(event_ids[2]))
        self.button3 = QPushButton("Hämta namn")
        self.name3 = QLabel("?")
        add_layout.addWidget(lbl3)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event3)
        add_layout.addWidget(self.button3)
        add_layout.addWidget(self.name3)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl4 = QLabel("Tävling 4: ")
        self.event4 = QLineEdit()
        self.event4.setFixedWidth(120)
        self.event4.setText(str(event_ids[3]))
        self.button4 = QPushButton("Hämta namn")
        self.name4 = QLabel("?")
        add_layout.addWidget(lbl4)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event4)
        add_layout.addWidget(self.button4)
        add_layout.addWidget(self.name4)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl5 = QLabel("Tävling 5: ")
        self.event5 = QLineEdit()
        self.event5.setFixedWidth(120)
        self.event5.setText(str(event_ids[4]))
        self.button5 = QPushButton("Hämta namn")
        self.name5 = QLabel("?")
        add_layout.addWidget(lbl5)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event5)
        add_layout.addWidget(self.button5)
        add_layout.addWidget(self.name5)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl6 = QLabel("Tävling 6: ")
        self.event6 = QLineEdit()
        self.event6.setFixedWidth(120)
        self.event6.setText(str(event_ids[5]))
        self.button6 = QPushButton("Hämta namn")
        self.name6 = QLabel("?")
        add_layout.addWidget(lbl6)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.event6)
        add_layout.addWidget(self.button6)
        add_layout.addWidget(self.name6)
        self.layout.addLayout(add_layout, stretch=False)

        self.line = PySide2.QtWidgets.QFrame()
        self.layout.addWidget(self.line)

        add_layout = QHBoxLayout()
        lbl = QLabel("Natt-tävling 1: ")
        self.night1 = QLineEdit()
        self.night1.setFixedWidth(120)
        self.night1.setText(str(night_ids[0]))
        self.button_n1 = QPushButton("Hämta namn")
        self.name_n1 = QLabel("?")
        add_layout.addWidget(lbl)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.night1)
        add_layout.addWidget(self.button_n1)
        add_layout.addWidget(self.name_n1)
        self.layout.addLayout(add_layout, stretch=False)

        add_layout = QHBoxLayout()
        lbl = QLabel("Natt-tävling 2: ")
        self.night2 = QLineEdit()
        self.night2.setFixedWidth(120)
        self.night2.setText(str(night_ids[1]))
        self.button_n2 = QPushButton("Hämta namn")
        self.name_n2 = QLabel("?")
        add_layout.addWidget(lbl)
        add_layout.setSpacing(100)
        add_layout.addWidget(self.night2)
        add_layout.addWidget(self.button_n2)
        add_layout.addWidget(self.name_n2)
        self.layout.addLayout(add_layout, stretch=False)

        self.output1 = QLabel("--Inget analyserat än--")
        self.output1.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output1)

        self.output2 = QLabel(" ")
        self.output2.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output2)

        self.button = QPushButton("Extrahera och analysera tävlingsresultat")
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        # Connecting the signal
        self.button.clicked.connect(self.magic)
        self.button1.clicked.connect(self.button1_pressed)

    @Slot()
    def magic(self):
        storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att lagra resultatfiler"))
        self.output1.setText("Analyserar...")
        eventlist = [self.event1.text(), self.event2.text(), self.event3.text(),
                     self.event4.text(), self.event5.text(), self.event6.text()]

        nightlist = [self.night1.text(), self.night2.text()]

        club_file, ind_file = extract_and_analyse(storage_path, eventlist, nightlist, self.key)
        self.output1.setText('Sparat: ' + club_file)
        self.output2.setText('Sparat: ' + ind_file)

    def button1_pressed(self):
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