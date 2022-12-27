import numpy as np

import vtk
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QLabel
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.morse import Morse

def browse_file(vtkWidget, data):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    file_name, _ = QFileDialog.getOpenFileName(None, "Select Ply File", "", "Ply Files (*.ply)", options=options)
    if file_name:
        # Load the selected file
        data.load_mesh_ply(file_name, quality_index=3, inverted=True)
        update_mesh(vtkWidget, data)

def compute_Morse(data):
    data.ProcessLowerStars()
    data.ExtractMorseComplex()
    data.ReduceMorseComplex(data.range)

def update_mesh(vtkWidget, data):
    ren = vtk.vtkRenderer()
    vtkWidget.GetRenderWindow().AddRenderer(ren)

    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()

    for vert in data.Vertices.values():
        points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
    for face in data.Faces.values():
        polys.InsertNextCell(len(face.indices), np.array(list(face.indices)))
    mesh.SetPoints(points)
    mesh.SetPolys(polys)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Add the mesh actor to the vtk renderer and show the window
    ren.AddActor(actor)

    vtkWidget.GetRenderWindow().Render()

def update_colors():
    data = 0

# Create a function to update the parameter based on the slider value
def update_parameter1(value, label1):
    global parameter1
    parameter1 = value
    label1.setText("Parameter 1: {}".format(value))

# Create a function to update the parameter based on the slider value
def update_parameter2(value, label2):
    global parameter2
    parameter2 = value
    label2.setText("Parameter 2: {}".format(value))

# Create a function to show the slider when the button is clicked
def show_slider(window, layout):
    # Create the slider and set its range and default value
    slider1 = QSlider(Qt.Horizontal)
    slider1.setRange(0, 100)
    slider1.setValue(50)
    # Create a label to display above the first slider
    label1 = QLabel("Parameter 1: 50")
    
    # Connect the valueChanged signal of the slider to the update_parameter function
    slider1.valueChanged.connect(lambda value: update_parameter1(value, label1))
    

    # Create the slider and set its range and default value
    slider2 = QSlider(Qt.Horizontal)
    slider2.setRange(0, 100)
    slider2.setValue(50)
    # Create a label to display above the first slider
    label2 = QLabel("Parameter 2: 50")
    
    # Connect the valueChanged signal of the slider to the update_parameter function
    slider2.valueChanged.connect(lambda value: update_parameter2(value, label2))
    

    layout.addWidget(label1)
    layout.addWidget(slider1)
    layout.addWidget(label2)
    layout.addWidget(slider2)
    # Add the layout to the main window
    window.setLayout(layout)

def main():
    data = Morse()
    color_points = set()

    # Create a PyQt5 window and vtk renderer
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    frame = QtWidgets.QFrame()
    layout = QtWidgets.QVBoxLayout(frame)


    vtkWidget = QVTKRenderWindowInteractor(frame)

    ren = vtk.vtkRenderer()
    vtkWidget.GetRenderWindow().AddRenderer(ren)
    iren = vtkWidget.GetRenderWindow().GetInteractor()

    # Create a vtk mesh actor using the vtkPolyData class
    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()
    #setup colors
    Colors = vtk.vtkUnsignedCharArray()
    Colors.SetNumberOfComponents(3)
    Colors.SetName("Colors")

    for ind, vert in data.Vertices.items():
        points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
        if ind in color_points:
            Colors.InsertNextTuple3(0,0,255)
        else:
            Colors.InsertNextTuple3(255,255,255)
    for ind, face in data.Faces.items():
        polys.InsertNextCell(len(face.indices), np.array([list(face.indices)]))
    mesh.SetPoints(points)
    mesh.SetPolys(polys)
    mesh.GetPointData().SetScalars(Colors)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Add the mesh actor to the vtk renderer and show the window
    ren.AddActor(actor)

    

    # Create a menu bar
    menu_bar = QMenuBar(window)

    # Create a file menu and add the browse button to it
    file_menu = QMenu("File")
    browse_action = file_menu.addAction("Browse")
    browse_action.triggered.connect(lambda: browse_file(vtkWidget, data))

    # Create a file menu and add the browse button to it
    processing_menu = QMenu("Processing")
    morse_action = processing_menu.addAction("Morse Computations")
    morse_action.triggered.connect(lambda: compute_Morse(data))

    # Create a settings menu and add the slider button to it
    visualization_menu = QMenu("Edge threshold slider")
    slider_action = visualization_menu.addAction("Show Slider")
    slider_action.triggered.connect(lambda: show_slider(window, layout))

    # Add the file and settings menus to the menu bar
    menu_bar.addMenu(file_menu)
    menu_bar.addMenu(processing_menu)
    menu_bar.addMenu(visualization_menu)

    # Create a vertical layout to hold the menu bar and the vtk widget
    layout.addWidget(menu_bar)
    layout.addWidget(vtkWidget)

    # Set the layout of the main window
    window.setLayout(layout)

    frame.setLayout(layout)
    window.setCentralWidget(frame)
    window.show()
    iren.Initialize()
    iren.Start()

    app.exec_()

if __name__ == '__main__':
    main()