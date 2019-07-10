import sys
import PySide2
import pandas as pd
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QFileDialog,
                               QVBoxLayout, QWidget, QLineEdit, QHBoxLayout)
from PySide2.QtCore import Slot, Qt
from loader.read_results import extract_and_analyse
from PySide2.QtGui import QIcon
from loader.read_manual_excel import read_manual_input
from base_utils import get_version
import os


class SimpleWidget(QWidget):
    def __init__(self, api_key, icon_file=''):
        self.key = api_key
        QWidget.__init__(self)

        self.manual_info = {}
        self.division_df = pd.DataFrame()
        self.user_input = {}
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
        if icon_file:
            self.setWindowIcon(QIcon(icon_file))

        self.button_get_manual = QPushButton("Välj fil med manuell input")
        self.button_analyse = QPushButton("Extrahera och analysera tävlingsresultat")

        self.layout.addWidget(self.button_get_manual)
        self.setLayout(self.layout)

        # Connecting the signal
        self.button_analyse.clicked.connect(self.magic)
        self.button_get_manual.clicked.connect(self.choose_excel_file)
        self.show()

    def choose_excel_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Välj Excel-fil med manuell input", '*.xlsx')
        if file_path[0]:
            self.manual_info, self.division_df, self.user_input = read_manual_input(file_path[0])
            self.layout.addWidget(self.button_analyse)
            self.setLayout(self.layout)

    def info_window(self):
        version_number = get_version()
        msg_box = PySide2.QtWidgets.QMessageBox()
        msg_str = """SkofCounter Version {0} \n
                        Poängberäknare för SKOF:s Ungdomsserie""".format(version_number)
        msg_box.about(self, 'Information', msg_str)

    @Slot()
    def magic(self):
        storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att lagra resultatfiler"))
        if os.path.exists(storage_path):
            self.quit_function()
            extract_and_analyse(storage_path, self.manual_info, self.division_df, self.user_input, self.key)

    def quit_function(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    version = get_version()

    debug = True
    if debug:
        print('Debug mode')
        api_key = os.environ["apikey"]
    else:
        api_key = input('Ange API nyckel: ')

    icon_file_name = 'run1.ico'
    widget = SimpleWidget(api_key, icon_file_name)
    widget.setWindowTitle('Skofcounter Version ' + version + ': Skånes ungdomsserie-beräknare')
    widget.resize(800, 90)
    widget.show()
    sys.exit(app.exec_())

