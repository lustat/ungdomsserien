import sys
import PySide2
import pandas as pd
from PySide2.QtWidgets import (QApplication, QPushButton, QFileDialog,
                               QVBoxLayout, QWidget)
from PySide2.QtCore import Slot, Qt
from loader.read_results import extract_and_analyse
from PySide2.QtGui import QIcon
from loader.read_manual_excel import read_manual_input
from base_utils import get_version
import os
from loader.input_structure import create_excel_template, get_input_structure


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

        help_action = PySide2.QtWidgets.QAction('Hjälp', self)
        help_action.triggered.connect(self.help_window)
        filemenu.addAction(help_action)

        about_action = PySide2.QtWidgets.QAction('Om', self)
        about_action.triggered.connect(self.info_window)
        filemenu.addAction(about_action)

        exit_action = PySide2.QtWidgets.QAction('Avsluta', self)
        exit_action.triggered.connect(sys.exit)
        filemenu.addAction(exit_action)

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
            # TODO check Excel input using structure-function

    def info_window(self):
        version_number = get_version()
        msg_box = PySide2.QtWidgets.QMessageBox()
        msg_str = """SkofCounter Version {0} \n\nPoängberäknare för SKOF:s Ungdomsserie \nKällkod: https://github.com/lustat/ungdomsserien""".format(version_number)
        msg_box.about(self, 'Information', msg_str)

    def help_window(self):
        msg_box = PySide2.QtWidgets.QMessageBox()
        msg_box.setIcon(PySide2.QtWidgets.QMessageBox.Question)
        msg_box.setText("Vill du skapa en Excel-mall?")
        msg_box.setInformativeText('Input till beräkningen sker via Excel-fil. Excel-filen måste följa en given mall.')
        msg_box.setStandardButtons(PySide2.QtWidgets.QMessageBox.Yes | PySide2.QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(PySide2.QtWidgets.QMessageBox.No)
        reply = msg_box.exec_()
        if reply == PySide2.QtWidgets.QMessageBox.Yes:
            storage_path = str(QFileDialog.getExistingDirectory(self, "Välj mapp att spara Excel-mall"))
            if os.path.exists(storage_path):
                template = get_input_structure()
                create_excel_template(structure=template, template_path=storage_path)

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

    # TODO present division sorted club results with lines and bold headers
    # TODO add ability to restart gui after calculation

    debug = False
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
    app.exec_()
    input('Tryck ENTER för att avsluta')
    sys.exit()

