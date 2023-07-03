from PyQt5 import QtWidgets

from .quick_guide import Ui_dialog_quickguide
from .info_contact import Ui_dialog_info_contact


class QuickGuide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setGeometry(300,300,600,600)
        self.setWindowTitle("Quick Guide")
        self.dialog_quickguide = QtWidgets.QDialog()
        self.ui = Ui_dialog_quickguide()
        self.ui.setupUi(self.dialog_quickguide)
        self.setCentralWidget(self.dialog_quickguide)
        self.ui.buttonBox.clicked.connect(self.close_window)

    def close_window(self):
        self.close()


class InfoContact(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setGeometry(300,300,600,600)
        self.setWindowTitle("Info/Contact")
        self.dialog_quickguide = QtWidgets.QDialog()
        self.ui = Ui_dialog_info_contact()
        self.ui.setupUi(self.dialog_quickguide)
        self.setCentralWidget(self.dialog_quickguide)
        self.ui.buttonBox.clicked.connect(self.close_window)

    def close_window(self):
        self.close()
