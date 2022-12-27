import numpy as np

import vtk
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QLabel
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.morse import Morse

class Gui:
    def __init__(self):
        self.data = Morse()

        self.high_thresh = None
        self.low_thresh = None

        self.high_percent = 15
        self.low_percent = 10

        self.color_points = set()

        self.app = QtWidgets.QApplication([])

        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("Morse GUI Test")
        self.layout = QVBoxLayout()

        # Create the VTK widget and add it to the layout
        self.vtkWidget = QVTKRenderWindowInteractor(self.window)
        self.layout.addWidget(self.vtkWidget)

        # Create the menu bar and add it to the layout
        self.menu_bar = QMenuBar()
        self.layout.setMenuBar(self.menu_bar)

        # Create the file, processing and visualization menus and add to the menu bar
        self.file_menu = QMenu("File")
        self.menu_bar.addMenu(self.file_menu)
        self.processing_menu = QMenu("Processing")
        self.menu_bar.addMenu(self.processing_menu)
        self.visualization_menu = QMenu("Visualization")
        self.menu_bar.addMenu(self.visualization_menu)

        # Create the open file action and add it to the file menu
        self.open_file_action = self.file_menu.addAction("Open")
        self.open_file_action.triggered.connect(lambda: self.browse_file())

        # Create the compute Morse action and add it to the file menu
        self.compute_Morse_action = self.processing_menu.addAction("Compute Morse")
        self.compute_Morse_action.triggered.connect(lambda: self.compute_Morse())

        # Create the update colors action and add it to the file menu -> moved to be computed every time you move the sliders
        #self.update_colors_action = self.visualization_menu.addAction("Update Colors")
        #self.update_colors_action.triggered.connect(lambda: self.update_mesh_color())

        # Create the show sliders action and add it to the file menu
        self.show_sliders_action = self.visualization_menu.addAction("Show Sliders")
        self.show_sliders_action.triggered.connect(lambda: self.show_slider())

        self.window.setLayout(self.layout)
        self.window.show()

        self.app.exec_()

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Ply File", "", "Ply Files (*.ply)", options=options)
        if file_name:
            # Load the selected file
            self.data.load_mesh_ply(file_name, quality_index=3, inverted=True)
            self.update_mesh()

    def update_mesh(self):
        ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)

        mesh = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()

        for vert in self.data.Vertices.values():
            points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
        for face in self.data.Faces.values():
            polys.InsertNextCell(len(face.indices), np.array(list(face.indices)))
        mesh.SetPoints(points)
        mesh.SetPolys(polys)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Add the mesh actor to the vtk renderer and show the window
        ren.AddActor(actor)

        self.vtkWidget.GetRenderWindow().Render()

    def update_mesh_color(self):
        self.color_points = self.data.get_salient_edges(self.high_thresh, self.low_thresh)
        # Get the renderer and mesh actor
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        actor = ren.GetActors().GetLastActor()

        # Get the mapper and the mesh data
        mapper = actor.GetMapper()
        mesh = mapper.GetInput()

        # Set the color of the points in the mesh
        point_data = mesh.GetPointData()
        color_array = vtk.vtkUnsignedCharArray()
        color_array.SetNumberOfComponents(3)
        color_array.SetName("Colors")
        for ind in range(mesh.GetNumberOfPoints()):
            if ind in self.color_points:
                color_array.InsertNextTuple3(0,0,255)
            else:
                color_array.InsertNextTuple3(255,255,255)
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def compute_Morse(self):
        self.data.ProcessLowerStars()
        self.data.ExtractMorseComplex()
        self.data.ReduceMorseComplex(self.data.range)

        self.high_thresh = self.data.max_separatrix_persistence*self.high_percent/100
        self.low_thresh = self.data.max_separatrix_persistence*self.low_percent/100
        self.color_points = self.data.get_salient_edges(self.high_thresh, self.low_thresh)
        self.update_mesh_color()

    # Create a function to update the parameter based on the slider value
    def update_high_thresh(self, value, label1):
        self.high_percent = value
        self.high_thresh = self.data.max_separatrix_persistence*self.high_percent/100
        label1.setText("High threshold: {}".format(value))
        self.update_mesh_color()

    # Create a function to update the parameter based on the slider value
    def update_low_thresh(self, value, label2):
        self.low_percent = value
        self.low_thresh = self.data.max_separatrix_persistence*self.low_percent/100
        label2.setText("Low threshold: {}".format(value))
        self.update_mesh_color()

    # Create a function to show the slider when the button is clicked
    def show_slider(self):
        # Create the slider and set its range and default value
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(0,100)
        slider1.setValue(self.high_percent)
        # Create a label to display above the first slider
        label1 = QLabel("High threshold: {}".format(self.high_percent))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        slider1.valueChanged.connect(lambda value: self.update_high_thresh(value, label1))
        

        # Create the slider and set its range and default value
        slider2 = QSlider(Qt.Horizontal)
        slider2.setRange(0,100)
        slider2.setValue(self.low_percent)
        # Create a label to display above the second slider
        label2 = QLabel("Low threshold: {}".format(self.low_percent))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        slider2.valueChanged.connect(lambda value: self.update_low_thresh(value, label2))
        

        self.layout.addWidget(label1)
        self.layout.addWidget(slider1)
        self.layout.addWidget(label2)
        self.layout.addWidget(slider2)
        # Add the layout to the main window
        self.window.setLayout(self.layout)

if __name__ == '__main__':
    Gui()