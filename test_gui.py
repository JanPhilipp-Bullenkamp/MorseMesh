import numpy as np

import vtk
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QHBoxLayout
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
def update_parameter(value):
    global parameter
    parameter = value

# Create a function to show the slider when the button is clicked
def show_slider():
    # Create the slider and set its range and default value
    slider = QSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(50)
    # Connect the valueChanged signal of the slider to the update_parameter function
    slider.valueChanged.connect(update_parameter)
    # Create a horizontal layout to hold the slider
    layout = QHBoxLayout()
    layout.addWidget(slider)
    # Show the layout in a new window
    window = QtWidgets.QDialog()
    window.setLayout(layout)
    window.show()

def main():
    data = Morse()
    color_points = set()

    # Create a PyQt5 window and vtk renderer
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    frame = QtWidgets.QFrame()
    layout = QtWidgets.QVBoxLayout(frame)


    vtkWidget = QVTKRenderWindowInteractor(frame)

    layout.addWidget(vtkWidget)

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

    # Create a button to trigger the file browsing dialog
    browse_button = QtWidgets.QPushButton("Browse")
    browse_button.clicked.connect(lambda: browse_file(vtkWidget, data))
    layout.addWidget(browse_button)

    # Create a button to perform Morse Computations
    morse_button = QtWidgets.QPushButton("Morse Computations")
    morse_button.clicked.connect(lambda: compute_Morse(data))
    layout.addWidget(morse_button)


    # Create a button to show the slider when clicked
    slider_button = QtWidgets.QPushButton("Set Edge Threshold")
    slider_button.clicked.connect(show_slider)
    layout.addWidget(slider_button)

    frame.setLayout(layout)
    window.setCentralWidget(frame)
    window.show()
    iren.Initialize()
    iren.Start()

    app.exec_()

if __name__ == '__main__':
    main()