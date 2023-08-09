"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp, Theresa Häberle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
