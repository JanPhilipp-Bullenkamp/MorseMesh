import numpy as np

import vtk
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QVBoxLayout, QMenuBar, QMenu, QLabel, QPushButton, QGroupBox, QLineEdit, QHBoxLayout, QGridLayout
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
        self.window.setGeometry(100,100,800,800)
        self.window.setWindowTitle("Mesh GUI")
        self.layout = QGridLayout()

        # Create the VTK widget and add it to the layout
        self.vtkWidget = QVTKRenderWindowInteractor(self.window)
        self.layout.addWidget(self.vtkWidget, 0,0)
        ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)
        
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

        self.save_edges_ply_action = self.file_menu.addAction("Save current Segmentation ply")
        self.save_edges_ply_action.triggered.connect(lambda: self.save_segmentation_result())

        # Create the compute Morse action and add it to the processing menu
        self.compute_Morse_action = self.processing_menu.addAction("Compute Morse")
        self.compute_Morse_action.triggered.connect(lambda: self.compute_Morse())

        self.compute_perona_malik_action = self.processing_menu.addAction("Compute Perona Malik")
        self.compute_perona_malik_action.triggered.connect(lambda: self.compute_perona_malik())

        # Create the show sliders action and add it to the visualization menu
        self.show_sliders_action = self.visualization_menu.addAction("Show Sliders")
        self.show_sliders_action.triggered.connect(lambda: self.show_slider())

        # Create the segment action and add it to the visualization menu
        self.segment_action = self.visualization_menu.addAction("Segmentation")
        self.segment_action.triggered.connect(lambda: self.compute_Segmentation())

        self.cluster_action = self.visualization_menu.addAction("Cluster")
        self.cluster_action.triggered.connect(lambda: self.cluster())

        self.merge_cluster_action = self.visualization_menu.addAction("Merge Cluster")
        self.merge_cluster_action.triggered.connect(lambda: self.merge_cluster())

        self.segment_new_action = self.visualization_menu.addAction("Segmentation new")
        self.segment_new_action.triggered.connect(lambda: self.compute_Segmentation_new())

        self.show_funvals_action = self.visualization_menu.addAction("Show funvals")
        self.show_funvals_action.triggered.connect(lambda: self.color_funvals())

        self.update_buttons()
        self.add_param_sidebar()

        self.window.setLayout(self.layout)
        self.window.show()

        self.app.exec_()

    def reset_data(self):
        self.data = Morse()

        try:
            if self.flag_sliders_shown:
                self.remove_sliders()
        except AttributeError:
            self.flag_sliders_shown = False


        self.flag_morse_computations = False
        self.flag_loaded_data = False
        self.flag_sliders_shown = False

        self.high_thresh = None
        self.low_thresh = None

        self.high_percent = 50
        self.low_percent = 45

        self.persistence = 0.04
        self.merge_threshold = 0.3
        self.cluster_seed_number = 150

        self.color_points = set()
        self.current_segmentation = {}
        self.current_segmentation_params = None
        self.center = [0,0,0]


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
            self.reset_data()
            self.data.load_mesh_ply(file_name, quality_index=3, inverted=True)
            self.update_mesh()

            self.flag_loaded_data = True
            self.flag_morse_computations = False
            self.update_buttons()
            #self.reset_camera_position()

    def save_edges_ply_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save Edges File (filename will be extended by _OverlayPoints)", 
                                                  "", "Ply Files (*.ply)", options=options)
        if filename:
            # Save the edge ply file:
            self.data.plot_SalientEdges_ply(filename, self.high_thresh, self.low_thresh, only_strong=True)

    def save_segmentation_result(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFilename(None, "Save current Segmentation as .txt file.",
                                                  "", "Txt Files (*.txt)", options=options)

        if filename:
            self.data.plot_labels_txt(self.current_segmentation, filename)

    def update_mesh(self):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        if ren != None:
            ren.RemoveAllViewProps()
        #ren = vtk.vtkRenderer()
        #self.vtkWidget.GetRenderWindow().AddRenderer(ren)

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
        ren.ResetCamera()

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

    def update_mesh_color_segmentation(self, label_dict: dict):
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
        for label, cell in label_dict.items():
            cell_color = color_list[label%len(color_list)]
            for ind in cell.vertices:
                color_array.InsertTypedTuple(ind, (cell_color[0],cell_color[1],cell_color[2]))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def color_segmentation(self):
        self.update_mesh_color_segmentation(self.current_segmentation)
        
    def cluster(self):
        self.current_segmentation = self.data.seed_cluster_mesh(self.color_points, self.cluster_seed_number)
        self.color_segmentation()

    def merge_cluster(self):
        clust  = self.data.seed_cluster_mesh(self.color_points, self.cluster_seed_number)
        self.current_segmentation = self.data.cluster_segmentation(clust, self.color_points, self.merge_threshold)
        self.color_segmentation()

    def color_funvals(self):
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
        for ind, vert in self.data.Vertices.items():
            lamb = (vert.fun_val-self.data.min)/self.data.range
            color = int(lamb*255) 
            color_array.InsertTypedTuple(ind, (color,color,color))
            
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def compute_Morse(self):
        self.data.ProcessLowerStars()
        self.data.ExtractMorseComplex()
        self.data.ReduceMorseComplex(self.data.range)
        #self.data.ReduceMorseComplex(self.persistence)

        self.high_thresh = self.data.max_separatrix_persistence*self.high_percent/100
        self.low_thresh = self.data.max_separatrix_persistence*self.low_percent/100
        self.color_points = self.data.get_salient_edges(self.high_thresh, self.low_thresh)

        self.flag_morse_computations = True
        self.update_buttons()

        self.update_edge_color()

    def compute_perona_malik(self):
        self.data.apply_Perona_Malik(4,0.1,0.1)
        self.color_funvals()

    def compute_Segmentation(self):
        if self.persistence not in self.data.reducedMorseComplexes.keys():
            self.data.ReduceMorseComplex(self.persistence)
        if (self.high_thresh, self.low_thresh) not in self.data.reducedMorseComplexes[self.persistence].Segmentations.keys():
            self.data.Segmentation(self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold)    
        else:
            if self.merge_threshold not in self.data.reducedMorseComplexes[self.persistence].Segmentations[(self.high_thresh, self.low_thresh)].keys():
                self.data.Segmentation(self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold)
                
        self.current_segmentation_params = np.array([self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold])
        self.current_segmentation = self.data.reducedMorseComplexes[self.current_segmentation_params[0]].Segmentations[(self.current_segmentation_params[1], self.current_segmentation_params[2])][self.current_segmentation_params[3]].Cells

        self.color_segmentation()

    def compute_Segmentation_new(self): 
        self.data.Segmentation_SalientReduction(self.high_thresh, self.low_thresh, self.merge_threshold, self.persistence)
                
        self.current_segmentation_params = np.array([self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold])
        self.current_segmentation = self.data.salientreducedMorseComplexes[(self.current_segmentation_params[0],self.current_segmentation_params[1],self.current_segmentation_params[2])].Segmentations[(self.current_segmentation_params[1], self.current_segmentation_params[2])][self.current_segmentation_params[3]].Cells

        self.color_segmentation()

    # Create a function to update the parameter based on the slider value
    def update_high_thresh(self, value, label1):
        self.high_percent = value
        self.high_thresh = self.data.max_separatrix_persistence*self.high_percent/100
        label1.setText("High threshold: {} % -> {}".format(value, self.high_thresh))
        self.update_edge_color()
        self.param4_input.setText("{:.5f}".format(self.high_thresh))

    # Create a function to update the parameter based on the slider value
    def update_low_thresh(self, value, label2):
        self.low_percent = value
        self.low_thresh = self.data.max_separatrix_persistence*self.low_percent/100
        label2.setText("Low threshold: {} % -> {}".format(value, self.low_thresh))
        self.update_edge_color()
        self.param5_input.setText("{:.5f}".format(self.low_thresh))

    # Create a function to show the slider when the button is clicked
    def show_slider(self):
        # Create the slider and set its range and default value
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setRange(0,100)
        self.slider1.setValue(self.high_percent)
        # Create a label to display above the first slider
        self.label1 = QLabel("High edge threshold: {} % -> {}".format(self.high_percent, self.high_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider1.valueChanged.connect(lambda value: self.update_high_thresh(value, self.label1))
        

        # Create the slider and set its range and default value
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0,100)
        self.slider2.setValue(self.low_percent)
        # Create a label to display above the second slider
        self.label2 = QLabel("Low edge threshold: {} % -> {}".format(self.low_percent, self.low_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider2.valueChanged.connect(lambda value: self.update_low_thresh(value, self.label2))

        self.layout.addWidget(self.label1,1,0)
        self.layout.addWidget(self.slider1,2,0)
        self.layout.addWidget(self.label2,3,0)
        self.layout.addWidget(self.slider2,4,0)

        # Create the exit button
        self.exit_button = QPushButton("Close Sliders")
        # Connect the clicked signal to the remove_sliders function
        self.exit_button.clicked.connect(self.remove_sliders)
        self.layout.addWidget(self.exit_button)

        # Add the layout to the main window
        self.window.setLayout(self.layout)

        self.flag_sliders_shown = True
        self.update_buttons()

    def remove_sliders(self):
        # Remove the first slider and its label from the layout
        self.layout.removeWidget(self.slider1)
        self.slider1.setParent(None)
        self.layout.removeWidget(self.label1)
        self.label1.setParent(None)

        # Remove the second slider and its label from the layout
        self.layout.removeWidget(self.slider2)
        self.slider2.setParent(None)
        self.layout.removeWidget(self.label2)
        self.label2.setParent(None)

        # remove exit button
        self.layout.removeWidget(self.exit_button)
        self.exit_button.setParent(None)

        #delete the object from memory
        del self.slider1
        del self.label1
        del self.slider2
        del self.label2
        del self.exit_button

        self.flag_sliders_shown = False

    def add_param_sidebar(self):
        # Create the sidebar group box
        self.sidebar = QGroupBox("Further Parameters:")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setMaximumSize(175, 400)

        # Create the input widgets and their default values
        self.param1_input = QLineEdit()
        self.param1_input.setText(str(self.persistence))
        self.param1_input.setMaximumSize(75, 25)
        self.param2_input = QLineEdit()
        self.param2_input.setText(str(self.merge_threshold))
        self.param2_input.setMaximumSize(75, 25)
        self.param3_input = QLineEdit()
        self.param3_input.setText(str(self.cluster_seed_number))
        self.param3_input.setMaximumSize(75, 25)
        self.param4_input = QLineEdit()
        self.param4_input.setText(str(self.high_thresh))
        self.param4_input.setMaximumSize(75, 25)
        self.param5_input = QLineEdit()
        self.param5_input.setText(str(self.low_thresh))
        self.param5_input.setMaximumSize(75, 25)

        # Add the input widgets to the sidebar layout
        self.sidebar_layout.addWidget(QLabel("Persistence"))
        self.sidebar_layout.addWidget(self.param1_input)
        self.sidebar_layout.addWidget(QLabel("Merge threshold"))
        self.sidebar_layout.addWidget(self.param2_input)
        self.sidebar_layout.addWidget(QLabel("Cluster Seed number"))
        self.sidebar_layout.addWidget(self.param3_input)
        self.sidebar_layout.addWidget(QLabel("High edge Thr"))
        self.sidebar_layout.addWidget(self.param4_input)
        self.sidebar_layout.addWidget(QLabel("Low edge Thr"))
        self.sidebar_layout.addWidget(self.param5_input)

        self.param1_input.editingFinished.connect(self.update_pers)
        self.param2_input.editingFinished.connect(self.update_merge_thr)
        self.param3_input.editingFinished.connect(self.update_seed_number)
        self.param1_input.editingFinished.connect(self.update_high_edge_thr)
        self.param1_input.editingFinished.connect(self.update_low_edge_thr)

        # Add the sidebar to the main layout
        self.layout.addWidget(self.sidebar,0,1)

    def update_pers(self):
        self.persistence = float(self.param1_input.text())

    def update_merge_thr(self):
        self.merge_threshold = float(self.param2_input.text())

    def update_seed_number(self):
        self.cluster_seed_number = int(self.param3_input.text())

    def update_high_edge_thr(self):
        self.persistence = float(self.param4_input.text())

    def update_low_edge_thr(self):
        self.persistence = float(self.param5_input.text())

if __name__ == '__main__':
    Gui()