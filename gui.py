"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

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

from gui.gui_functions import Gui_Window

from PyQt5 import QtWidgets
import sys

darkstyle_import = True
try:
    import qdarkstyle
except ImportError:
    darkstyle_import = False
    pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if darkstyle_import:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = Gui_Window()
    ui.setup(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())