import numpy as np

import vtk
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QVBoxLayout, QMenuBar, QMenu, QLabel
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.morse import Morse

color_list = [[255,0,0],  #red
              [0,255,0], #lime
              [0,0,255], # blue
              [255,255,0], # yellow
              [0,255,255], #cyan
              [255,0,255], #magenta
              [192,192,192], #silver
              [128,0,0], #maroon
              [128,128,0], #olive
              [0,128,0], # green
              [128,0,128], #purple
              [0,128,128], #teal
              [0,0,128] #navy
             ]

class Gui:
    def __init__(self):
        self.reset_data()

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

        self.save_edges_ply_action = self.file_menu.addAction("Save Edges ply")
        self.save_edges_ply_action.triggered.connect(lambda: self.save_edges_ply_file())

        # Create the compute Morse action and add it to the file menu
        self.compute_Morse_action = self.processing_menu.addAction("Compute Morse")
        self.compute_Morse_action.triggered.connect(lambda: self.compute_Morse())

        # Create the show sliders action and add it to the file menu
        self.show_sliders_action = self.visualization_menu.addAction("Show Sliders")
        self.show_sliders_action.triggered.connect(lambda: self.show_slider())

        # Create the segment action and add it to the file menu
        self.segment_action = self.visualization_menu.addAction("Segmentation")
        self.segment_action.triggered.connect(lambda: self.compute_Segmentation())

        self.update_buttons()

        self.window.setLayout(self.layout)
        self.window.show()

        self.app.exec_()

    def reset_data(self):
        self.data = Morse()

        self.flag_morse_computations = False
        self.flag_loaded_data = False
        self.flag_sliders_shown = False

        self.high_thresh = None
        self.low_thresh = None

        self.high_percent = 15
        self.low_percent = 10

        self.color_points = set()

        self.current_segmentation_params = None

    def update_buttons(self):
        self.show_sliders_action.setEnabled(True if self.flag_morse_computations and not self.flag_sliders_shown else False)
        self.compute_Morse_action.setEnabled(True if self.flag_loaded_data else False)
        self.save_edges_ply_action.setEnabled(True if self.flag_morse_computations else False)
        self.segment_action.setEnabled(True if self.flag_morse_computations else False)


    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Ply File", "", "Ply Files (*.ply)", options=options)
        if file_name:
            self.data.load_mesh_ply(file_name, quality_index=3, inverted=True)
            self.update_mesh()

            self.flag_loaded_data = True
            self.flag_morse_computations = False
            self.update_buttons()

    def save_edges_ply_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save Edges File (filename will be extended by _OverlayPoints)", 
                                                  "", "Ply Files (*.ply)", options=options)
        if filename:
            # Save the edge ply file:
            self.data.plot_SalientEdges_ply(filename, self.high_thresh, self.low_thresh, only_strong=True)

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

    def update_edge_color(self):
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

    def update_segmentation_color(self):
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
        for label, cell in self.data.reducedMorseComplexes[self.current_segmentation_params[0]].Segmentations[(self.current_segmentation_params[1], self.current_segmentation_params[2])][self.current_segmentation_params[3]].Cells.items():
            cell_color = color_list[label%len(color_list)]
            for ind in cell.vertices:
                color_array.InsertTypedTuple(ind, (cell_color[0],cell_color[1],cell_color[2]))
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

        self.flag_morse_computations = True
        self.update_buttons()

        self.update_edge_color()

    def compute_Segmentation(self):
        if 0.04 not in self.data.reducedMorseComplexes.keys():
            self.data.ReduceMorseComplex(0.04)
        if (self.high_thresh, self.low_thresh) not in self.data.reducedMorseComplexes[0.04].Segmentations.keys():
            self.data.Segmentation(0.04, self.high_thresh, self.low_thresh, 0.3)    
        else:
            if 0.3 not in self.data.reducedMorseComplexes[0.04].Segmentations[(self.high_thresh, self.low_thresh)].keys():
                self.data.Segmentation(0.04, self.high_thresh, self.low_thresh, 0.3)
                
        self.current_segmentation_params = np.array([0.04, self.high_thresh, self.low_thresh, 0.3])

        self.update_segmentation_color()

    # Create a function to update the parameter based on the slider value
    def update_high_thresh(self, value, label1):
        self.high_percent = value
        self.high_thresh = self.data.max_separatrix_persistence*self.high_percent/100
        label1.setText("High threshold: {} % -> {}".format(value, self.high_thresh))
        self.update_edge_color()

    # Create a function to update the parameter based on the slider value
    def update_low_thresh(self, value, label2):
        self.low_percent = value
        self.low_thresh = self.data.max_separatrix_persistence*self.low_percent/100
        label2.setText("Low threshold: {} % -> {}".format(value, self.low_thresh))
        self.update_edge_color()

    # Create a function to show the slider when the button is clicked
    def show_slider(self):
        # Create the slider and set its range and default value
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(0,100)
        slider1.setValue(self.high_percent)
        # Create a label to display above the first slider
        label1 = QLabel("High threshold: {} % -> {}".format(self.high_percent, self.high_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        slider1.valueChanged.connect(lambda value: self.update_high_thresh(value, label1))
        

        # Create the slider and set its range and default value
        slider2 = QSlider(Qt.Horizontal)
        slider2.setRange(0,100)
        slider2.setValue(self.low_percent)
        # Create a label to display above the second slider
        label2 = QLabel("Low threshold: {} % -> {}".format(self.low_percent, self.low_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        slider2.valueChanged.connect(lambda value: self.update_low_thresh(value, label2))

        self.layout.addWidget(label1)
        self.layout.addWidget(slider1)
        self.layout.addWidget(label2)
        self.layout.addWidget(slider2)
        # Add the layout to the main window
        self.window.setLayout(self.layout)

        self.flag_sliders_shown = True
        self.update_buttons()

if __name__ == '__main__':
    Gui()