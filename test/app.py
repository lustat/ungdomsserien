import sys
import random
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QLineEdit)
from PySide2.QtCore import Slot, Qt
from loader.read_results import extract_and_analyse


class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        event_ids = [18218, 17412, 18308, 18106, 16981, 18995]
        self.layout = QVBoxLayout()
        self.setWindowIconText('Test')
        self.text = QLabel("Event ID:s")
        self.text.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.text)

        self.event1 = QLineEdit()
        self.event1.setAlignment(Qt.AlignLeft)
        self.event1.setFixedWidth(120)
        self.event1.setText(str(event_ids[0]))
        self.layout.addWidget(self.event1)

        self.event2 = QLineEdit()
        self.event2.setAlignment(Qt.AlignLeft)
        self.event2.setFixedWidth(120)
        self.event2.setText(str(event_ids[1]))
        self.layout.addWidget(self.event2)

        self.event3 = QLineEdit()
        self.event3.setAlignment(Qt.AlignLeft)
        self.event3.setFixedWidth(120)
        self.event3.setText(str(event_ids[2]))
        self.layout.addWidget(self.event3)

        self.event4 = QLineEdit()
        self.event4.setAlignment(Qt.AlignLeft)
        self.event4.setFixedWidth(120)
        self.event4.setText(str(event_ids[3]))
        self.layout.addWidget(self.event4)

        self.event5 = QLineEdit()
        self.event5.setAlignment(Qt.AlignLeft)
        self.event5.setFixedWidth(120)
        self.event5.setText(str(event_ids[4]))
        self.layout.addWidget(self.event5)

        self.event6 = QLineEdit()
        self.event6.setAlignment(Qt.AlignLeft)
        self.event6.setFixedWidth(120)
        self.event6.setText(str(event_ids[5]))
        self.layout.addWidget(self.event6)

        self.output1 = QLabel("--Nothing analysed yet--")
        self.output1.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output1)

        self.output2 = QLabel(" ")
        self.output2.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.output2)

        self.button = QPushButton("Extract and analyse events")
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        # Connecting the signal
        self.button.clicked.connect(self.magic)

    @Slot()
    def magic(self):
        self.output1.setText("Analysing...")
        eventlist = [self.event1.text(), self.event2.text(), self.event3.text(),
                     self.event4.text(), self.event5.text(), self.event6.text()]
        club_file, ind_file = extract_and_analyse(eventlist)
        self.output1.setText('Saved: ' + club_file)
        self.output2.setText('Saved: ' + ind_file)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.setWindowTitle('Beräknaren: Skånes ungdomsserie')
    widget.resize(800, 300)
    widget.show()

    sys.exit(app.exec_())