from PyQt5.QtWidgets import QMenuBar, QMenu

class MenuBar:
    def __init__(self, layout):
        self.menu_bar = QMenuBar()
        layout.setMenuBar(self.menu_bar)

        # Create the file, processing and visualization menus and add to the menu bar
        self.file_menu = QMenu("File")
        self.menu_bar.addMenu(self.file_menu)
        self.processing_menu = QMenu("Processing")
        self.menu_bar.addMenu(self.processing_menu)
        self.visualization_menu = QMenu("Visualization")
        self.menu_bar.addMenu(self.visualization_menu)

        # Create the open file action and add it to the file menu
        self.open_file_action = self.file_menu.addAction("Open")
        self.open_feature_vec_file_action = self.file_menu.addAction("Load feature vector file")
        self.save_edges_ply_action = self.file_menu.addAction("Save Edges ply")
        self.save_edges_ply_action = self.file_menu.addAction("Save current Segmentation txt")

        # Create the compute Morse action and add it to the processing menu
        self.compute_Morse_action = self.processing_menu.addAction("Compute Morse")
        self.compute_smoothing_action = self.processing_menu.addAction("Compute smoothing")
        self.compute_perona_malik_action = self.processing_menu.addAction("Compute Perona Malik")

        # Create the show sliders action and add it to the visualization menu
        self.show_sliders_action = self.visualization_menu.addAction("Show Sliders")
        self.morsecells_action = self.visualization_menu.addAction("MorseCells persistence")
        self.segment_action = self.visualization_menu.addAction("Segmentation")
        self.cluster_action = self.visualization_menu.addAction("Cluster")
        self.cluster_boundary_action = self.visualization_menu.addAction("Cluster boundary")
        self.cluster_boundary_ridge_intersection_action = self.visualization_menu.addAction("Cluster boundary ridge intersection")
        self.merge_cluster_action = self.visualization_menu.addAction("Merge Cluster")
        self.segment_new_action = self.visualization_menu.addAction("Segmentation new")
        self.show_funvals_action = self.visualization_menu.addAction("Show funvals")

        self.paintbrush_action = self.visualization_menu.addAction("Paintbrush")