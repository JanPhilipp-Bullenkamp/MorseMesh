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

from gui.base_gui import Ui_MainWindow
from gui.help_files import QuickGuide, InfoContact

from PyQt5 import QtCore, QtGui, QtWidgets

import vtk
import qdarkstyle
import numpy as np

from gui.gui_data import Data, Flags, Parameters
from gui.collapsible_boxes import CollapsibleDialog

from src.evaluation_and_conversion import label_txt_to_label_dict

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

color_list_old = [[255,0,0],  #red
              [0,0,255], # blue
              [0,255,0], #lime
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

# new colors from color brewer
color_list = [
              [141,211,199], # turquoise
              [251,128,114], # red
              [255,255,179], # light yellow
              [190,186,218], # light purple
              [128,177,211], # blue
              [253,180,98], # orange
              [179,222,105], # green
              [252,205,229], #light pink
              [217,217,217] # grey
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

class vtkWindow:
    def __init__(self, qwidget):
        # Create the VTK widget and add it to the layout
        self.window = QtWidgets.QWidget(qwidget)
        self.layout = QtWidgets.QGridLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.window)
        self.layout.addWidget(self.vtkWidget)
        ren = vtk.vtkRenderer()
        ren.SetBackground(1, 1, 1)
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)
        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = CustomInteractorStyle()
        interactor.SetInteractorStyle(style)
        self.window.setLayout(self.layout)
        self.window.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.window.setMinimumSize(400,400)
        
    def update_mesh(self, vert_dict: dict, face_dict: dict):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        if ren != None:
            ren.RemoveAllViewProps()

        mesh = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        for vert in vert_dict.values():
            points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
        for face in face_dict.values():
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

    def update_mesh_color(self, 
                          label_dict: dict, 
                          partial: bool = False, 
                          cell_structure: bool = True):
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
        if cell_structure:
            for label, cell in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in cell.vertices:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        else:
            for label, points in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in points:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def update_fun_val_color(self, vert_dict: dict, value_range: float, min_value: float):
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
        for ind, vert in vert_dict.items():
            lamb = (vert.fun_val-min_value)/value_range
            color = int(lamb*255) 
            color_array.InsertTypedTuple(ind, (color,color,color))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

class Gui_Window(Ui_MainWindow):
    def setup(self, MainWindow):
        # setup UI
        self.setupUi(MainWindow)
        # setup vtk
        self.setupVtk()
        # setup data
        self.setup_data()
        # connect buttons
        self.connect_buttons_to_functions()
        # add sidebar
        self.add_sidebar()
        # add tooltips
        self.add_tooltips()

    def setupVtk(self):
        # vtk setup
        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = CustomInteractorStyle()
        interactor.SetInteractorStyle(style)
        ren = vtk.vtkRenderer()
        ren.SetBackground(1, 1, 1)
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)

    def setup_data(self):
        self.data = Data()
        self.flags = Flags()
        self.parameters = Parameters()
    
    def reset_data(self):
        self.data.reset()
        self.flags.reset()
        self.parameters.reset()

    def connect_buttons_to_functions(self):
        self.action_load_ply.triggered.connect(self.load_ply)
        self.action_load_feature_vector_file.triggered.connect(self.load_feature_vector_file)
        self.action_load_label_txt.triggered.connect(self.load_label_txt_file)
        self.action_save_segmentation_label_txt.triggered.connect(self.save_segmentation_result)
        self.action_load_conforming_labels_label_txt.triggered.connect(self.load_conforming_labels)

        self.action_compute_morse_complex.triggered.connect(self.compute_morse)

        self.action_morse_cells_persistence.triggered.connect(self.compute_persistent_morse_cells)
        self.action_segmentation_method.triggered.connect(self.compute_segmentation)
        self.action_morse_segementation_ridge_first.triggered.connect(self.compute_segmentation_new)
        self.action_cluster.triggered.connect(self.cluster)
        self.action_cluster_segmentation_method.triggered.connect(self.merge_cluster)
        self.action_morse_segmentation_conforming.triggered.connect(self.compute_confoming_segmentation)

        self.action_quick_guide.triggered.connect(self.quick_guide)
        self.action_info_contact.triggered.connect(self.info_contact)

        self.add_slider_functionality()

    def enable_disable_menu_actions(self):
        # buttons for loaded data
        self.action_compute_morse_complex.setEnabled(self.flags.flag_loaded_data)
        self.action_load_feature_vector_file.setEnabled(self.flags.flag_loaded_data)
        self.action_load_label_txt.setEnabled(self.flags.flag_loaded_data)
        self.action_load_conforming_labels_label_txt.setEnabled(self.flags.flag_loaded_data)

        # buttons for computed morse complex
        self.action_morse_cells_persistence.setEnabled(self.flags.flag_morse_computations)
        self.action_cluster.setEnabled(self.flags.flag_morse_computations)
        self.action_cluster_segmentation_method.setEnabled(self.flags.flag_morse_computations)
        self.action_morse_segementation_ridge_first.setEnabled(self.flags.flag_morse_computations)
        self.action_segmentation_method.setEnabled(self.flags.flag_morse_computations)
        self.frame_bottom.setHidden(not self.flags.flag_morse_computations)
        self.frame_bottom.setEnabled(self.flags.flag_morse_computations)

        # buttons for computed segmentation
        self.action_save_segmentation_label_txt.setEnabled(self.flags.flag_current_segmentation)

        # buttons for conforming input loaded
        self.action_morse_segmentation_conforming.setEnabled(self.flags.flag_conforming_input)

        if self.flags.flag_sliders_shown:
            do=0

    def add_slider_functionality(self):
        # make 0.5% steps, so range from 0,200 (percent *2)
        self.high_thresh_slider.setRange(0,200)
        self.low_thresh_slider.setRange(0,200)

        self.high_thresh_slider.setValue(self.parameters.high_percent*2)
        self.low_thresh_slider.setValue(self.parameters.low_percent*2)

        self.high_thresh_slider.valueChanged.connect(lambda value: self.update_high_thresh(value))
        self.low_thresh_slider.valueChanged.connect(lambda value: self.update_low_thresh(value))

    def update_high_thresh(self, value):
        self.parameters.high_percent = value*0.5
        self.parameters.high_thresh = ((self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)
                                        *self.parameters.high_percent/100 + self.data.morse.min_separatrix_persistence)
        self.update_edge_color()

        self.high_thresh_text.setText("High thresh: "+"{:.5f}".format(self.parameters.high_thresh)
                                      +"  ("+str(self.parameters.high_percent)+"%)")

    def update_low_thresh(self, value):
        self.parameters.low_percent = value*0.5
        self.parameters.low_thresh = ((self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)
                                        *self.parameters.low_percent/100 + self.data.morse.min_separatrix_persistence)
        self.update_edge_color()
        
        self.low_thresh_text.setText("Low thresh: "+"{:.5f}".format(self.parameters.low_thresh)
                                     +"  ("+str(self.parameters.low_percent)+"%)")

    def add_sidebar(self):
        self.sidebar = CollapsibleDialog(self.parameters)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidebar.sizePolicy().hasHeightForWidth())
        self.sidebar.setSizePolicy(sizePolicy)
        self.sidebar.setMinimumSize(QtCore.QSize(250, 400))
        self.sidebar.setMaximumSize(QtCore.QSize(250, 16777215))
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout.addWidget(self.sidebar, 0, 0, 1, 1)

    def load_ply(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 
                                                             "Select Ply File", 
                                                             "", 
                                                             "Ply Files (*.ply)", 
                                                             options=options)
        if file_name:
            self.reset_data()
            self.data.morse.load_mesh_new(file_name, 
                                          morse_function="quality", 
                                          inverted=True)
            self.update_mesh()
            self.flags.flag_loaded_data = True
            self.enable_disable_menu_actions()

    def load_feature_vector_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 
                                                   "Select feature vector File", 
                                                   "", 
                                                   "Mat Files (*.mat)", 
                                                   options=options)
        if file_name:
            self.data.morse.load_new_funvals(file_name, 
                                             operation=self.parameters.feature_vector_function)
            self.color_funvals()

    def load_label_txt_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 
                                                   "Select label txt File", 
                                                   "", 
                                                   "Txt Files (*.txt)", 
                                                   options=options)
        if file_name:
            self.data.current_segmentation = label_txt_to_label_dict(file_name)
            self.color_segmentation(cell_structure=False)
            self.flags.flag_current_segmentation = True
            self.enable_disable_menu_actions()

    def load_conforming_labels(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 
                                                   "Select conforming label txt File", 
                                                   "", 
                                                   "Txt Files (*.txt)", 
                                                   options=options)
        if file_name:
            self.data.morse.load_labels(file_name)
            self.flags.flag_conforming_input = True
            self.enable_disable_menu_actions()

    """Currently not used!"""
    #def save_edges_ply_file(self):
    #    options = QtWidgets.QFileDialog.Options()
    #    options |= QtWidgets.QFileDialog.ReadOnly
    #    filename, _ = QtWidgets.QFileDialog.getSaveFileName(None, 
    #                                              "Save Edges File (filename will be extended by _OverlayPoints)", 
    #                                              "", 
    #                                              "Ply Files (*.ply)", 
    #                                              options=options)
    #    if filename:
            # Save the edge ply file:
    #        self.data.morse.plot_salient_edges_ply(filename, 
    #                                               self.parameters.high_thresh, 
    #                                               self.parameters.low_thresh, 
    #                                               only_strong=True)

    def save_segmentation_result(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(None, 
                                                  "Save current Segmentation as .txt file.",
                                                  "", 
                                                  "Txt Files (*.txt)", 
                                                  options=options)

        if filename:
            self.data.morse.plot_labels_txt(self.data.current_segmentation, filename)

    def update_mesh(self):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        if ren != None:
            ren.RemoveAllViewProps()

        mesh = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        for vert in self.data.morse.Vertices.values():
            points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
        for face in self.data.morse.Faces.values():
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

    def update_mesh_color(self, 
                          label_dict: dict, 
                          partial: bool = False, 
                          cell_structure: bool = True,
                          fun_val_coloring: bool = False):
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
        if cell_structure:
            for label, cell in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in cell.vertices:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        elif fun_val_coloring:
            for ind, vert in self.data.morse.Vertices.items():
                lamb = (vert.fun_val-self.data.morse.min)/self.data.morse.range
                color = int(lamb*255) 
                color_array.InsertTypedTuple(ind, (color,color,color))

        else:
            for label, points in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in points:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def update_edge_color(self):
        if self.parameters.mode == "ridge":
            self.data.color_points = self.data.morse.get_salient_ridges(self.parameters.high_thresh, 
                                                                        self.parameters.low_thresh, 
                                                                        self.parameters.min_length, 
                                                                        self.parameters.max_length,
                                                                        self.parameters.separatrix_type)
        elif self.parameters.mode == "valley":
            self.data.color_points = self.data.morse.get_salient_valleys(self.parameters.high_thresh, 
                                                                         self.parameters.low_thresh, 
                                                                         self.parameters.min_length, 
                                                                         self.parameters.max_length,
                                                                         self.parameters.separatrix_type)
        color_dict = {1: self.data.color_points}
        self.update_mesh_color(color_dict, partial=True, cell_structure=False)

    def color_segmentation(self, partial: bool = False, cell_structure: bool = True):
        self.update_mesh_color(self.data.current_segmentation, 
                               partial=partial, 
                               cell_structure=cell_structure)
        self.flags.flag_current_segmentation = True
        self.enable_disable_menu_actions()

    def compute_morse(self):
        self.data.morse.process_lower_stars(conforming=self.flags.flag_conforming_input)
        self.data.morse.extract_morse_complex()
        self.data.morse.reduce_morse_complex(self.data.morse.range, 
                                             conforming=self.flags.flag_conforming_input)
        
        self.update_high_thresh(self.parameters.high_percent*2) # need *2 because goes in 0.5% steps, so need to scale here
        self.update_low_thresh(self.parameters.low_percent*2) # need *2 because goes in 0.5% steps, so need to scale here
        
        self.data.color_points = self.data.morse.get_salient_ridges(self.parameters.high_thresh, 
                                                                    self.parameters.low_thresh,
                                                                    separatrix_type=self.parameters.separatrix_type)
        self.update_edge_color()
        if self.flags.flag_conforming_input:
            self.flags.flag_conforming_morse = True
        else:
            self.flags.flag_morse_computations = True
        self.enable_disable_menu_actions()

    def compute_persistent_morse_cells(self):
        self.data.morse.reduce_morse_complex(self.parameters.persistence)
        self.data.morse.extract_morse_cells(self.parameters.persistence)
        self.data.current_segmentation = self.data.morse.reducedMorseComplexes[self.parameters.persistence].MorseCells.Cells
        self.color_segmentation()

    def compute_segmentation(self):
        if self.parameters.persistence not in self.data.morse.reducedMorseComplexes.keys():
            self.data.morse.reduce_morse_complex(self.parameters.persistence)
        if (self.parameters.high_thresh, self.parameters.low_thresh) not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations.keys():
            self.data.morse.segmentation(self.parameters.persistence, 
                                         self.parameters.high_thresh, 
                                         self.parameters.low_thresh, 
                                         self.parameters.merge_threshold, 
                                         size_threshold=self.parameters.size_threshold)    
        else:
            if self.parameters.merge_threshold not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations[(self.parameters.high_thresh, self.parameters.low_thresh)].keys():
                self.data.morse.segmentation(self.parameters.persistence, 
                                             self.parameters.high_thresh, 
                                             self.parameters.low_thresh, 
                                             self.parameters.merge_threshold, 
                                             size_threshold=self.parameters.size_threshold)
                
        self.data.current_segmentation_params = np.array([self.parameters.persistence, 
                                                          self.parameters.high_thresh, 
                                                          self.parameters.low_thresh, 
                                                          self.parameters.merge_threshold])
        self.data.current_segmentation = self.data.morse.reducedMorseComplexes[self.data.current_segmentation_params[0]].Segmentations[(self.data.current_segmentation_params[1], self.data.current_segmentation_params[2])][self.data.current_segmentation_params[3]].Cells

        self.color_segmentation()

    def compute_segmentation_new(self): 
        self.data.morse.segmentation_salient_reduction(self.parameters.high_thresh, 
                                                       self.parameters.low_thresh, 
                                                       self.parameters.merge_threshold, 
                                                       self.parameters.persistence)
        self.data.current_segmentation_params = np.array([self.parameters.persistence, 
                                                          self.parameters.high_thresh, 
                                                          self.parameters.low_thresh, 
                                                          self.parameters.merge_threshold])
        self.data.current_segmentation = self.data.morse.salient_reduced_morse_complexes[(self.data.current_segmentation_params[0],
                                                                                          self.data.current_segmentation_params[1],
                                                                                          self.data.current_segmentation_params[2])].Segmentations[(self.data.current_segmentation_params[1], 
                                                                                                                                                    self.data.current_segmentation_params[2])][self.data.current_segmentation_params[3]].Cells
        self.color_segmentation()

    def cluster(self):
        self.data.current_segmentation = self.data.morse.seed_cluster_mesh(self.data.color_points, 
                                                                           self.parameters.cluster_seed_number)
        self.color_segmentation()

    def merge_cluster(self):
        clust  = self.data.morse.seed_cluster_mesh(self.data.color_points, 
                                                   self.parameters.cluster_seed_number)
        self.data.current_segmentation = self.data.morse.cluster_segmentation(clust, 
                                                                              self.data.color_points, 
                                                                              self.parameters.merge_threshold_cluster)
        self.color_segmentation()

    def compute_confoming_segmentation(self):
        self.compute_morse()
        if self.parameters.persistence not in self.data.morse.reducedMorseComplexes.keys():
            self.data.morse.reduce_morse_complex(self.parameters.persistence,
                                                 conforming=True)
        if (self.parameters.high_thresh, self.parameters.low_thresh) not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations.keys():
            self.data.morse.segmentation(self.parameters.persistence, 
                                         self.parameters.high_thresh, 
                                         self.parameters.low_thresh, 
                                         self.parameters.merge_threshold, 
                                         size_threshold=self.parameters.size_threshold,
                                         conforming=True)    
        else:
            if self.parameters.merge_threshold not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations[(self.parameters.high_thresh, self.parameters.low_thresh)].keys():
                self.data.morse.segmentation(self.parameters.persistence, 
                                             self.parameters.high_thresh, 
                                             self.parameters.low_thresh, 
                                             self.parameters.merge_threshold, 
                                             size_threshold=self.parameters.size_threshold,
                                             conforming=True)
                
        self.data.current_segmentation_params = np.array([self.parameters.persistence, 
                                                          self.parameters.high_thresh, 
                                                          self.parameters.low_thresh, 
                                                          self.parameters.merge_threshold])
        self.data.current_segmentation = self.data.morse.reducedMorseComplexes[self.data.current_segmentation_params[0]].Segmentations[(self.data.current_segmentation_params[1], self.data.current_segmentation_params[2])][self.data.current_segmentation_params[3]].Cells

        self.color_segmentation()

    def quick_guide(self):
        self.w = QuickGuide()
        self.w.show()

    def info_contact(self):
        self.w = InfoContact()
        self.w.show()

    def add_tooltips(self):
        QtWidgets.QToolTip.setFont(QtGui.QFont('Georgia', 11))

        self.menu_file.setToolTipsVisible(True)
        self.menu_compute.setToolTipsVisible(True)
        self.menu_segmentations.setToolTipsVisible(True)
        self.menu_help.setToolTipsVisible(True)
        self.action_load_ply.setToolTip("<span class=nobr>Load a .ply file")
        self.action_load_feature_vector_file.setToolTip("<span class=nobr>Load a .mat "
                                                        "feature vector file "
                                                        "generated by GigaMesh for the "
                                                        "loaded mesh</span>")
        self.action_load_label_txt.setToolTip("<span class=nobr>Load a segmentation "
                                              ".txt file with index - label rows</span>")
        self.action_load_conforming_labels_label_txt.setToolTip("<span class=nobr>Load "
                                                                "labels for conforming "
                                                                "method.</span>")
        self.action_save_segmentation_label_txt.setToolTip("<span class=nobr>Save the "
                                                           "segmentation as .txt file "
                                                           "with index - label "
                                                           "rows</span>")
        self.action_compute_morse_complex.setToolTip("<span class=nobr>Computes a "
                                                     "Morse-Smale Complex for "
                                                     "the loaded mesh and already stores "
                                                     "a maximally reduced complex for "
                                                     "edge detection as well</span>")
        self.action_morse_cells_persistence.setToolTip("<span class=nobr>Calculates "
                                                       "the Morse cells at a "
                                                       "given persistence and visualizes "
                                                       "them in different colors on the "
                                                       "mesh</span>")
        self.action_cluster.setToolTip("<span class=nobr>Splits the mesh into "
                                       "at lest the given number of "
                                       "clusters, respecting the calculated edges. "
                                       "Creates additional clusters if there are patches "
                                       "left enclosed by edges that do not have "
                                       "an initial seed.</span>")
        self.action_cluster_segmentation_method.setToolTip("<span class=nobr>Segments "
                                                           "the mesh based on "
                                                           "an initial clustering into "
                                                           "a given number of clusters "
                                                           "(respecting the calculated "
                                                           "edges) and then merging them "
                                                           "up until there are no more "
                                                           "neighboring clusters with "
                                                           "less than a merging threshold "
                                                           "percentage of edge separating "
                                                           "them.</span>")
        self.action_morse_segementation_ridge_first.setToolTip("<span class=nobr>Segment "
                                                               "the mesh with a Morse "
                                                               "cell based method, that "
                                                               "makes sure that no ridges "
                                                               "are merged during Morse "
                                                               "complex simplification "
                                                               "with persistence</span>")
        self.action_segmentation_method.setToolTip("<span class=nobr>Segment the mesh "
                                                   "with a Morse cell based method, "
                                                   "simplifying the MS complex first "
                                                   "with a given persistence, using the "
                                                   "calculated edges to merge the initial "
                                                   "oversegmentation up to the given "
                                                   "merge threshold. So all adjacent "
                                                   "cells will have at least the merge "
                                                   "threshold percent of edge between "
                                                   "them.</span>")
        self.action_morse_segmentation_conforming.setToolTip("<span class=nobr>Segment "
                                                             "mesh using the conforming "
                                                             "input loaded previously. "
                                                             "</span>")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = Gui_Window()
    ui.setup(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())