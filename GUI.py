import numpy as np

import vtk
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QVBoxLayout, QMenuBar, QMenu, QLabel, QPushButton, QGroupBox, QLineEdit, QHBoxLayout, QGridLayout, QCheckBox
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.morse import Morse
from gui_menubar import MenuBar

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

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        self.AddObserver("MouseWheelForwardEvent", self.zoomIn)
        self.AddObserver("MouseWheelBackwardEvent", self.zoomOut)

    def zoomIn(self, obj, event):
        self.GetCurrentRenderer().ResetCameraClippingRange()
        self.GetCurrentRenderer().GetActiveCamera().Zoom(1.1)
        self.GetInteractor().GetRenderWindow().Render()
    
    def zoomOut(self, obj, event):
        self.GetCurrentRenderer().ResetCameraClippingRange()
        self.GetCurrentRenderer().GetActiveCamera().Zoom(0.9)
        self.GetInteractor().GetRenderWindow().Render()

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
        ren.SetBackground(0.1, 0.1, 0.1)
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)
        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = CustomInteractorStyle()
        interactor.SetInteractorStyle(style)
        
        # Create the menu bar and add it to the layout
        self.menu_bar = MenuBar(self.layout)
        self.connect_functions_to_menu_buttons()

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
        self.mode = "ridge"
        self.min_length = 1
        self.max_length = None

        self.high_percent = 50
        self.low_percent = 45

        self.persistence = 0.04
        self.merge_threshold = 0.3
        self.cluster_seed_number = 150

        self.size_threshold = 500

        self.color_points = set()
        self.current_segmentation = {}
        self.current_segmentation_params = None
        self.center = [0,0,0]

    def connect_functions_to_menu_buttons(self):
        self.menu_bar.open_file_action.triggered.connect(self.browse_file)
        self.menu_bar.open_feature_vec_file_action.triggered.connect(self.browse_feature_vector_file)
        self.menu_bar.save_edges_ply_action.triggered.connect(self.save_edges_ply_file)
        self.menu_bar.save_edges_ply_action.triggered.connect(self.save_segmentation_result)

        # Create the compute Morse action and add it to the processing menu
        self.menu_bar.compute_Morse_action.triggered.connect(self.compute_morse)
        self.menu_bar.compute_smoothing_action.triggered.connect(self.smoothing)
        self.menu_bar.compute_perona_malik_action.triggered.connect(self.compute_perona_malik)

        # Create the show sliders action and add it to the visualization menu
        self.menu_bar.show_sliders_action.triggered.connect(self.show_slider)
        self.menu_bar.morsecells_action.triggered.connect(self.compute_persistent_morse_cells)
        self.menu_bar.segment_action.triggered.connect(self.compute_segmentation)
        self.menu_bar.cluster_action.triggered.connect(self.cluster)
        self.menu_bar.cluster_boundary_action.triggered.connect(self.cluster_boundary)
        self.menu_bar.cluster_boundary_ridge_intersection_action.triggered.connect(self.cluster_boundary_ridge_intersection)
        self.menu_bar.merge_cluster_action.triggered.connect(self.merge_cluster)
        self.menu_bar.segment_new_action.triggered.connect(self.compute_segmentation_new)
        self.menu_bar.show_funvals_action.triggered.connect(self.color_funvals)

    def update_buttons(self):
        self.menu_bar.show_sliders_action.setEnabled(True if self.flag_morse_computations and not self.flag_sliders_shown else False)
        self.menu_bar.compute_Morse_action.setEnabled(True if self.flag_loaded_data else False)
        self.menu_bar.save_edges_ply_action.setEnabled(True if self.flag_morse_computations else False)
        self.menu_bar.segment_action.setEnabled(True if self.flag_morse_computations else False)


    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Ply File", "", "Ply Files (*.ply)", options=options)
        if file_name:
            self.reset_data()
            self.data.load_mesh_new(file_name, morse_function="quality", inverted=True)
            self.update_mesh()

            self.flag_loaded_data = True
            self.flag_morse_computations = False
            self.update_buttons()

    def browse_feature_vector_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select feature vector File", "", "Mat Files (*.mat)", options=options)
        if file_name:
            self.data.load_new_funvals(file_name, operation="maxabs")

    def save_edges_ply_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save Edges File (filename will be extended by _OverlayPoints)", 
                                                  "", "Ply Files (*.ply)", options=options)
        if filename:
            # Save the edge ply file:
            self.data.plot_salient_edges_ply(filename, self.high_thresh, self.low_thresh, only_strong=True)

    def save_segmentation_result(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save current Segmentation as .txt file.",
                                                  "", "Txt Files (*.txt)", options=options)

        if filename:
            self.data.plot_labels_txt(self.current_segmentation, filename)

    def update_mesh(self):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        if ren != None:
            ren.RemoveAllViewProps()

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
        if self.mode == "ridge":
            self.color_points = self.data.get_salient_ridges(self.high_thresh, self.low_thresh, self.min_length, self.max_length)
        elif self.mode == "valley":
            self.color_points = self.data.get_salient_valleys(self.high_thresh, self.low_thresh, self.min_length, self.max_length)
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

    def update_mesh_color_segmentation(self, label_dict: dict, partial: bool = False):
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

        if partial: # write all points in white and update color points afterwards
            number_of_points = mesh.GetNumberOfPoints()
            white = (255, 255, 255)
            for i in range(number_of_points):
                color_array.InsertTypedTuple(i, white)

        for label, cell in label_dict.items():
            cell_color = color_list[label%len(color_list)]
            for ind in cell.vertices:
                color_array.InsertTypedTuple(ind, (cell_color[0],cell_color[1],cell_color[2]))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def color_segmentation(self, partial: bool = False):
        self.update_mesh_color_segmentation(self.current_segmentation, partial=partial)
        
    def cluster(self):
        self.current_segmentation = self.data.seed_cluster_mesh(self.color_points, self.cluster_seed_number)
        self.color_segmentation()

    def cluster_boundary(self):
        cluster_dict = self.data.seed_cluster_mesh(self.color_points, self.cluster_seed_number)
        for comp in cluster_dict.values():
            comp.vertices = comp.boundary
        self.current_segmentation = cluster_dict
        self.color_segmentation(partial=True)

    def cluster_boundary_ridge_intersection(self):
        cluster_dict = self.data.seed_cluster_mesh(self.color_points, self.cluster_seed_number)
        for comp in cluster_dict.values():
            comp.vertices = comp.boundary.intersection(self.color_points)
        self.current_segmentation = cluster_dict
        self.color_segmentation(partial=True)

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

    def compute_morse(self):
        self.data.process_lower_stars()
        self.data.extract_morse_complex()
        self.data.reduce_morse_complex(self.data.range)
        #self.data.reduce_morse_complex(self.persistence)

        self.high_thresh = (self.data.max_separatrix_persistence-self.data.min_separatrix_persistence)*self.high_percent/100
        self.low_thresh = (self.data.max_separatrix_persistence-self.data.min_separatrix_persistence)*self.low_percent/100
        self.color_points = self.data.get_salient_ridges(self.high_thresh, self.low_thresh)

        self.flag_morse_computations = True
        self.update_buttons()

        self.update_edge_color()

        self.show_slider()

    def compute_perona_malik(self):
        self.data.apply_perona_malik(1,0.6,0.2)
        self.color_funvals()

    def smoothing(self):
        self.data.smooth_fun_vals(3)
        self.color_funvals()

    def compute_persistent_morse_cells(self):
        self.data.reduce_morse_complex(self.persistence)
        self.data.extract_morse_cells(self.persistence)
        self.current_segmentation = self.data.reducedMorseComplexes[self.persistence].MorseCells.Cells
        self.color_segmentation()

    def compute_segmentation(self):
        if self.persistence not in self.data.reducedMorseComplexes.keys():
            self.data.reduce_morse_complex(self.persistence)
        if (self.high_thresh, self.low_thresh) not in self.data.reducedMorseComplexes[self.persistence].Segmentations.keys():
            self.data.segmentation(self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold, size_threshold=self.size_threshold)    
        else:
            if self.merge_threshold not in self.data.reducedMorseComplexes[self.persistence].Segmentations[(self.high_thresh, self.low_thresh)].keys():
                self.data.segmentation(self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold, size_threshold=self.size_threshold)
                
        self.current_segmentation_params = np.array([self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold])
        self.current_segmentation = self.data.reducedMorseComplexes[self.current_segmentation_params[0]].Segmentations[(self.current_segmentation_params[1], self.current_segmentation_params[2])][self.current_segmentation_params[3]].Cells

        self.color_segmentation()

    def compute_segmentation_new(self): 
        self.data.segmentation_salient_reduction(self.high_thresh, self.low_thresh, self.merge_threshold, self.persistence)
                
        self.current_segmentation_params = np.array([self.persistence, self.high_thresh, self.low_thresh, self.merge_threshold])
        self.current_segmentation = self.data.salientreducedMorseComplexes[(self.current_segmentation_params[0],self.current_segmentation_params[1],self.current_segmentation_params[2])].Segmentations[(self.current_segmentation_params[1], self.current_segmentation_params[2])][self.current_segmentation_params[3]].Cells

        self.color_segmentation()

    # Create a function to update the parameter based on the slider value
    def update_high_thresh(self, value, label1):
        self.high_percent = value
        self.high_thresh = (self.data.max_separatrix_persistence-self.data.min_separatrix_persistence)*self.high_percent/100
        label1.setText("High threshold: {} % -> {}".format(value, self.high_thresh))
        self.update_edge_color()
        self.param4_input.setText("{:.5f}".format(self.high_thresh))

    # Create a function to update the parameter based on the slider value
    def update_low_thresh(self, value, label2):
        self.low_percent = value
        self.low_thresh = (self.data.max_separatrix_persistence-self.data.min_separatrix_persistence)*self.low_percent/100
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
        self.param6_input = QLineEdit()
        self.param6_input.setText(str(self.size_threshold))
        self.param6_input.setMaximumSize(75, 25)

        self.param8_input = QLineEdit()
        self.param8_input.setText(str(self.min_length))
        self.param8_input.setMaximumSize(75, 25)
        self.param9_input = QLineEdit()
        self.param9_input.setText(str(self.max_length))
        self.param9_input.setMaximumSize(75, 25)

        # create three checkable boxes
        self.box1 = QCheckBox("Ridges", checked=True)
        self.mode = "ridge"
        self.box2 = QCheckBox("Valleys", checked=False)
        self.box3 = QCheckBox("Both", checked=False)

        # connect the stateChanged signal of the boxes to a slot
        self.box1.stateChanged.connect(lambda state, checkbox=self.box1: self.check_boxes(state, checkbox))
        self.box2.stateChanged.connect(lambda state, checkbox=self.box2: self.check_boxes(state, checkbox))
        self.box3.stateChanged.connect(lambda state, checkbox=self.box3: self.check_boxes(state, checkbox))

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
        self.sidebar_layout.addWidget(QLabel("Size threshold segmentation (per label)"))
        self.sidebar_layout.addWidget(self.param6_input)
        self.sidebar_layout.addWidget(QLabel("Min sepa length"))
        self.sidebar_layout.addWidget(self.param8_input)
        self.sidebar_layout.addWidget(QLabel("Max sepa length"))
        self.sidebar_layout.addWidget(self.param9_input)

        # add the boxes to the layout
        self.sidebar_layout.addWidget(self.box1)
        self.sidebar_layout.addWidget(self.box2)
        self.sidebar_layout.addWidget(self.box3)

        self.param1_input.editingFinished.connect(self.update_pers)
        self.param2_input.editingFinished.connect(self.update_merge_thr)
        self.param3_input.editingFinished.connect(self.update_seed_number)
        self.param4_input.editingFinished.connect(self.update_high_edge_thr)
        self.param5_input.editingFinished.connect(self.update_low_edge_thr)
        self.param6_input.editingFinished.connect(self.update_size_threshold)
        self.param8_input.editingFinished.connect(self.update_min_sepa_length)
        self.param9_input.editingFinished.connect(self.update_max_sepa_length)

        # Add the sidebar to the main layout
        self.layout.addWidget(self.sidebar,0,1)

    def check_boxes(self, state, checkbox):
        boxes = [self.box1, self.box2, self.box3]
        checked_boxes = [box for box in boxes if box.isChecked()]

        # make sure exactly one box is checked
        if len(checked_boxes) == 0:
            checkbox.setChecked(True)
        elif len(checked_boxes) > 1:
            for box in boxes:
                if box != checkbox:
                    box.setChecked(False)

        if self.box1.isChecked():
            self.mode = "ridge"
        elif self.box2.isChecked():
            self.mode = "valley"
        elif self.box3.isChecked():
            self.mode = "both"
        else:
            raise ValueError("One of the ridge/valley/both boxes should be checked at all times!")

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

    def update_size_threshold(self):
        self.size_threshold = float(self.param6_input.text())

    def update_min_sepa_length(self):
        self.min_length = float(self.param8_input.text())

    def update_max_sepa_length(self):
        self.max_length = float(self.param9_input.text())

class SideBar:
    def __init__(self, layout):
        # Create the sidebar group box
        self.sidebar = QGroupBox("Further Parameters:")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setMaximumSize(175, 400)

        self.create_boxes()
        
        # connect the stateChanged signal of the boxes to a slot
        self.box1.stateChanged.connect(self.check_boxes)
        self.box2.stateChanged.connect(self.check_boxes)
        self.box3.stateChanged.connect(self.check_boxes)

        self.add_boxes_to_sidebar_layout()
        self.connect_update_functions_to_boxes()
        
        # Add the sidebar to the main layout
        layout.addWidget(self.sidebar,0,1)

    def create_boxes(self):
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
        self.param6_input = QLineEdit()
        self.param6_input.setText(str(self.size_threshold))
        self.param6_input.setMaximumSize(75, 25)

        self.param8_input = QLineEdit()
        self.param8_input.setText(str(self.min_length))
        self.param8_input.setMaximumSize(75, 25)
        self.param9_input = QLineEdit()
        self.param9_input.setText(str(self.max_length))
        self.param9_input.setMaximumSize(75, 25)

        # create three checkable boxes
        self.box1 = QCheckBox("Ridges")
        self.box2 = QCheckBox("Valleys")
        self.box3 = QCheckBox("Both")

    def add_boxes_to_sidebar_layout(self):
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
        self.sidebar_layout.addWidget(QLabel("Size threshold segmentation (per label)"))
        self.sidebar_layout.addWidget(self.param6_input)
        self.sidebar_layout.addWidget(QLabel("Min sepa length"))
        self.sidebar_layout.addWidget(self.param8_input)
        self.sidebar_layout.addWidget(QLabel("Max sepa length"))
        self.sidebar_layout.addWidget(self.param9_input)

        # add the boxes to the layout
        self.sidebar_layout.addWidget(self.box1)
        self.sidebar_layout.addWidget(self.box2)
        self.sidebar_layout.addWidget(self.box3)

    def connect_update_functions_to_boxes(self):
        self.param1_input.editingFinished.connect(self.update_pers)
        self.param2_input.editingFinished.connect(self.update_merge_thr)
        self.param3_input.editingFinished.connect(self.update_seed_number)
        self.param4_input.editingFinished.connect(self.update_high_edge_thr)
        self.param5_input.editingFinished.connect(self.update_low_edge_thr)
        self.param6_input.editingFinished.connect(self.update_size_threshold)
        self.param8_input.editingFinished.connect(self.update_min_sepa_length)
        self.param9_input.editingFinished.connect(self.update_max_sepa_length)



if __name__ == '__main__':
    Gui()