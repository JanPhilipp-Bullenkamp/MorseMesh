from PyQt5 import QtWidgets

class QuickGuide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setGeometry(300,300,300,300)
        self.setWindowTitle("Quck Guide")
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setMarkdown(
            "### 1. Load ply file <br />"
            "<br />"
            "Select *Load ply* under the *File* menu. Note that you need a .ply file that"
            "contains a function value under **quality**. <br />"
            "<br />"
            " ### 2. Compute Morse Complex <br />"
            "<br />"
            "Compute the Morse complex for a loaded mesh in the *Compute* menu under"
            "*Compute Morse complex*.<br />"
        )
        self.setCentralWidget(text)
