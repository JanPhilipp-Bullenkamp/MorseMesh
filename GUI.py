import numpy as np

import vtk
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider, QLabel, QPushButton

from gui_data import Data, Flags, Parameters
from gui_menubar import MenuBar
from gui_sidebar import SideBar
from gui_window import Window

class PaintbrushInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.left_button_release_event)

        self.paintbrush = vtk.vtkPolyData()
        self.paintbrush_points = vtk.vtkPoints()
        self.paintbrush_cells = vtk.vtkCellArray()

        self.paintbrush.SetPoints(self.paintbrush_points)
        self.paintbrush.SetVerts(self.paintbrush_cells)

        self.paintbrush_mapper = vtk.vtkPolyDataMapper()
        self.paintbrush_mapper.SetInputData(self.paintbrush)
        self.paintbrush_actor = vtk.vtkActor()
        self.paintbrush_actor.SetMapper(self.paintbrush_mapper)
        self.paintbrush_actor.GetProperty().SetPointSize(10)
        self.paintbrush_actor.GetProperty().SetColor(1, 0, 0)
        
        self.paint_radius = 10 # set the paint radius here

    def left_button_press_event(self, obj, event):
        self.OnLeftButtonDown()
        self.paint_at_mouse_position()

    def left_button_release_event(self, obj, event):
        self.OnLeftButtonUp()

    def paint_at_mouse_position(self):
        # Get the mouse position in screen coordinates
        screen_x, screen_y = self.GetInteractor().GetEventPosition()

        # Convert the screen coordinates to world coordinates
        picker = vtk.vtkPropPicker()
        picker.Pick(screen_x, screen_y, 0, self.GetDefaultRenderer())
        position = picker.GetPickPosition()

        # Find all the points within the paint radius of the mouse position
        point_ids = self.GetPointsWithinRadius(position)

        # Add the points to the paintbrush
        for point_id in point_ids:
            self.paintbrush_points.InsertNextPoint(self.points.GetPoint(point_id))
            self.paintbrush_cells.InsertNextCell(1)
            self.paintbrush_cells.InsertCellPoint(self.paintbrush_points.GetNumberOfPoints() - 1)

        # Update the paintbrush actor
        self.paintbrush_points.Modified()
        self.paintbrush_cells.Modified()
        self.paintbrush_actor.Modified()
        self.GetDefaultRenderer().AddActor(self.paintbrush_actor)

    def GetPointsWithinRadius(self, position):
        point_ids = []
        radius_squared = self.paint_radius * self.paint_radius

        for i in range(self.points.GetNumberOfPoints()):
            point = self.points.GetPoint(i)
            distance_squared = vtk.vtkMath.Distance2BetweenPoints(point, position)
            if distance_squared <= radius_squared:
                point_ids.append(i)

        return point_ids


class Application:
    def __init__(self):
        self.data = Data()
        self.flags = Flags()
        self.parameters = Parameters()

        self.app = QtWidgets.QApplication([])

        self.window = Window()

        # Create the menu bar and add it to the layout
        self.menu_bar = MenuBar(self.window.layout)
        self.connect_functions_to_menu_buttons()

        self.update_buttons()
        self.parameters_sidebar = SideBar(self.window.layout, self.parameters)

        self.app.exec_()

    def reset_data(self):
        self.data.reset()
        self.flags.reset()
        self.parameters.reset()

        try:
            if self.flags.flag_sliders_shown:
                self.remove_sliders()
        except AttributeError:
            self.flags.flag_sliders_shown = False

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

        self.menu_bar.paintbrush_action.triggered.connect(self.paint_test)

    def update_buttons(self):
        self.menu_bar.show_sliders_action.setEnabled(True if self.flags.flag_morse_computations and not self.flags.flag_sliders_shown else False)
        self.menu_bar.compute_Morse_action.setEnabled(True if self.flags.flag_loaded_data else False)
        self.menu_bar.save_edges_ply_action.setEnabled(True if self.flags.flag_morse_computations else False)
        self.menu_bar.segment_action.setEnabled(True if self.flags.flag_morse_computations else False)

    def paint_test(self):
        # set the interactor style to the paintbrush style
        paintbrush_style = PaintbrushInteractorStyle()
        self.window.vtkWidget.SetInteractorStyle(paintbrush_style)

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Ply File", "", "Ply Files (*.ply)", options=options)
        if file_name:
            self.reset_data()
            self.data.morse.load_mesh_new(file_name, morse_function="quality", inverted=True)
            self.update_mesh()

            self.flags.flag_loaded_data = True
            self.flags.flag_morse_computations = False
            self.update_buttons()

    def browse_feature_vector_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Select feature vector File", "", "Mat Files (*.mat)", options=options)
        if file_name:
            self.data.morse.load_new_funvals(file_name, operation="maxabs")
            self.color_funvals()

    def save_edges_ply_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save Edges File (filename will be extended by _OverlayPoints)", 
                                                  "", "Ply Files (*.ply)", options=options)
        if filename:
            # Save the edge ply file:
            self.data.morse.plot_salient_edges_ply(filename, self.parameters.high_thresh, self.parameters.low_thresh, only_strong=True)

    def save_segmentation_result(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getSaveFileName(None, "Save current Segmentation as .txt file.",
                                                  "", "Txt Files (*.txt)", options=options)

        if filename:
            self.data.morse.plot_labels_txt(self.data.current_segmentation, filename)

    def update_mesh(self):
        self.window.update_mesh(self.data.morse.Vertices, self.data.morse.Faces)

    def update_edge_color(self):
        if self.parameters.mode == "ridge":
            self.data.color_points = self.data.morse.get_salient_ridges(self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.min_length, self.parameters.max_length)
        elif self.parameters.mode == "valley":
            self.data.color_points = self.data.morse.get_salient_valleys(self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.min_length, self.parameters.max_length)
        color_dict = {1: self.data.color_points}
        self.window.update_mesh_color(color_dict, partial=True, cell_structure=False)

    def color_segmentation(self, partial: bool = False):
        self.window.update_mesh_color(self.data.current_segmentation, partial=partial)

    def cluster(self):
        self.data.current_segmentation = self.data.morse.seed_cluster_mesh(self.data.color_points, self.parameters.cluster_seed_number)
        self.color_segmentation()

    def cluster_boundary(self):
        cluster_dict = self.data.morse.seed_cluster_mesh(self.data.color_points, self.parameters.cluster_seed_number)
        for comp in cluster_dict.values():
            comp.vertices = comp.boundary
        self.data.current_segmentation = cluster_dict
        self.color_segmentation(partial=True)

    def cluster_boundary_ridge_intersection(self):
        cluster_dict = self.data.morse.seed_cluster_mesh(self.data.color_points, self.parameters.cluster_seed_number)
        for comp in cluster_dict.values():
            comp.vertices = comp.boundary.intersection(self.data.color_points)
        self.data.current_segmentation = cluster_dict
        self.color_segmentation(partial=True)

    def merge_cluster(self):
        clust  = self.data.morse.seed_cluster_mesh(self.data.color_points, self.parameters.cluster_seed_number)
        self.data.current_segmentation = self.data.morse.cluster_segmentation(clust, self.data.color_points, self.parameters.merge_threshold)
        self.color_segmentation()

    def color_funvals(self):
        self.window.update_fun_val_color(self.data.morse.Vertices, self.data.morse.range, self.data.morse.min)

    def compute_morse(self):
        self.data.morse.process_lower_stars()
        self.data.morse.extract_morse_complex()
        self.data.morse.reduce_morse_complex(self.data.morse.range)

        self.parameters.high_thresh = (self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)*self.parameters.high_percent/100
        self.parameters.low_thresh = (self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)*self.parameters.low_percent/100
        self.data.color_points = self.data.morse.get_salient_ridges(self.parameters.high_thresh, self.parameters.low_thresh)

        self.flags.flag_morse_computations = True
        self.update_buttons()

        self.update_edge_color()

        self.show_slider()

    def compute_perona_malik(self):
        self.data.morse.apply_perona_malik(1,0.6,0.2)
        self.color_funvals()

    def smoothing(self):
        self.data.morse.smooth_fun_vals(3)
        self.color_funvals()

    def compute_persistent_morse_cells(self):
        self.data.morse.reduce_morse_complex(self.parameters.persistence)
        self.data.morse.extract_morse_cells(self.parameters.persistence)
        self.data.current_segmentation = self.data.morse.reducedMorseComplexes[self.parameters.persistence].MorseCells.Cells
        self.color_segmentation()

    def compute_segmentation(self):
        if self.parameters.persistence not in self.data.morse.reducedMorseComplexes.keys():
            self.data.morse.reduce_morse_complex(self.parameters.persistence)
        if (self.parameters.high_thresh, self.parameters.low_thresh) not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations.keys():
            self.data.morse.segmentation(self.parameters.persistence, self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.merge_threshold, size_threshold=self.parameters.size_threshold)    
        else:
            if self.parameters.merge_threshold not in self.data.morse.reducedMorseComplexes[self.parameters.persistence].Segmentations[(self.parameters.high_thresh, self.parameters.low_thresh)].keys():
                self.data.morse.segmentation(self.parameters.persistence, self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.merge_threshold, size_threshold=self.parameters.size_threshold)
                
        self.data.current_segmentation_params = np.array([self.parameters.persistence, self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.merge_threshold])
        self.data.current_segmentation = self.data.morse.reducedMorseComplexes[self.data.current_segmentation_params[0]].Segmentations[(self.data.current_segmentation_params[1], self.data.current_segmentation_params[2])][self.data.current_segmentation_params[3]].Cells

        self.color_segmentation()

    def compute_segmentation_new(self): 
        self.data.morse.segmentation_salient_reduction(self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.merge_threshold, self.parameters.persistence)
                
        self.data.current_segmentation_params = np.array([self.parameters.persistence, self.parameters.high_thresh, self.parameters.low_thresh, self.parameters.merge_threshold])
        self.data.current_segmentation = self.data.morse.salient_reduced_morse_complexes[(self.data.current_segmentation_params[0],self.data.current_segmentation_params[1],self.data.current_segmentation_params[2])].Segmentations[(self.data.current_segmentation_params[1], self.data.current_segmentation_params[2])][self.data.current_segmentation_params[3]].Cells

        self.color_segmentation()

    # Create a function to update the parameter based on the slider value
    def update_high_thresh(self, value, label1):
        self.parameters.high_percent = value
        self.parameters.high_thresh = (self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)*self.parameters.high_percent/100
        label1.setText("High threshold: {} % -> {}".format(value, self.parameters.high_thresh))
        self.update_edge_color()
        self.parameters_sidebar.param4_input.setText("{:.5f}".format(self.parameters.high_thresh))

    # Create a function to update the parameter based on the slider value
    def update_low_thresh(self, value, label2):
        self.parameters.low_percent = value
        self.parameters.low_thresh = (self.data.morse.max_separatrix_persistence-self.data.morse.min_separatrix_persistence)*self.parameters.low_percent/100
        label2.setText("Low threshold: {} % -> {}".format(value, self.parameters.low_thresh))
        self.update_edge_color()
        self.parameters_sidebar.param5_input.setText("{:.5f}".format(self.parameters.low_thresh))

    # Create a function to show the slider when the button is clicked
    def show_slider(self):
        # Create the slider and set its range and default value
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setRange(0,100)
        self.slider1.setValue(self.parameters.high_percent)
        # Create a label to display above the first slider
        self.label1 = QLabel("High edge threshold: {} % -> {}".format(self.parameters.high_percent, self.parameters.high_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider1.valueChanged.connect(lambda value: self.update_high_thresh(value, self.label1))
        

        # Create the slider and set its range and default value
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0,100)
        self.slider2.setValue(self.parameters.low_percent)
        # Create a label to display above the second slider
        self.label2 = QLabel("Low edge threshold: {} % -> {}".format(self.parameters.low_percent, self.parameters.low_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider2.valueChanged.connect(lambda value: self.update_low_thresh(value, self.label2))

        self.window.layout.addWidget(self.label1,1,0)
        self.window.layout.addWidget(self.slider1,2,0)
        self.window.layout.addWidget(self.label2,3,0)
        self.window.layout.addWidget(self.slider2,4,0)

        # Create the exit button
        self.exit_button = QPushButton("Close Sliders")
        # Connect the clicked signal to the remove_sliders function
        self.exit_button.clicked.connect(self.remove_sliders)
        self.window.layout.addWidget(self.exit_button)

        # Add the layout to the main window
        self.window.window.setLayout(self.window.layout)

        self.flag_sliders_shown = True
        self.update_buttons()

    def remove_sliders(self):
        # Remove the first slider and its label from the layout
        self.window.layout.removeWidget(self.slider1)
        self.slider1.setParent(None)
        self.window.layout.removeWidget(self.label1)
        self.label1.setParent(None)

        # Remove the second slider and its label from the layout
        self.window.layout.removeWidget(self.slider2)
        self.slider2.setParent(None)
        self.window.layout.removeWidget(self.label2)
        self.label2.setParent(None)

        # remove exit button
        self.window.layout.removeWidget(self.exit_button)
        self.exit_button.setParent(None)

        #delete the object from memory
        del self.slider1
        del self.label1
        del self.slider2
        del self.label2
        del self.exit_button

        self.flags.flag_sliders_shown = False


if __name__ == '__main__':
    Application()