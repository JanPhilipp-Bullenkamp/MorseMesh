from PyQt5 import QtWidgets


class QuickGuide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        
        self.setGeometry(300,300,300,300)
        self.setWindowTitle("Quick Guide")
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setMarkdown(
            "### **1. Load ply file** <br />"
            "<br />"
            "Select *Load ply* under the *File* menu. Note that you need a .ply file that "
            "contains a function value under **quality**. <br />"
            "<br />"
            "### **2. Compute Morse Complex** <br />"
            "<br />"
            "Compute the Morse complex for a loaded mesh in the *Compute* menu under "
            "*Compute Morse complex*. <br />"
            "<br />"
            "### **Comments on the mesh:** <br />"
            "<br />"
            "Please make sure that your mesh has a manifold-like structure, i.e. especially "
            "there should be no edges with more than 2 adjacent triangles. Holes or "
            "boundaries in the mesh are no problem algorithmically, but depending on the "
            "application it might make sense to fill them. <br />"
            "To do mesh preprocessing we recommend using e.g. "
            "[GigaMesh](https://gigamesh.eu/). <br />"
        )
        self.setCentralWidget(text)
