import numpy as np

#vertices = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
#                     [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]])

#faces = np.array([[0, 1, 3], [4, 5, 7], [0, 1, 5],
#                  [2, 3, 7], [1, 3, 7], [0, 2, 6]])

from src.morse import Morse

data = Morse()
data.load_mesh_ply("../../Data/artefact_31_test/curvature/31_r1.00_n4_v256.volume.ply", quality_index=3, inverted=True)

vertices = np.array([[v.x,v.y,v.z] for v in data.Vertices.values()])
faces = np.array([np.array(list(f.indices)) for f in data.Faces.values()])

data.ProcessLowerStars()
data.ExtractMorseComplex()
color_points = data.get_salient_edges(0.06,0.04)

import vtk
from PyQt5 import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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

for i, p in enumerate(vertices):
    points.InsertNextPoint(p)
    if i in color_points:
        Colors.InsertNextTuple3(0,0,255)
    else:
        Colors.InsertNextTuple3(255,255,255)
for i, f in enumerate(faces):
    polys.InsertNextCell(len(f), f)
mesh.SetPoints(points)
mesh.SetPolys(polys)
mesh.GetPointData().SetScalars(Colors)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(mesh)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Add the mesh actor to the vtk renderer and show the window
ren.AddActor(actor)

frame.setLayout(layout)
window.setCentralWidget(frame)
window.show()
iren.Initialize()
iren.Start()

app.exec_()