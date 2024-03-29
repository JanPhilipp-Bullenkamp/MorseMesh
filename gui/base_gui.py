# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1211, 1129)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setStyleSheet("qdarkstyle")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(700, 600))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.whole_grid = QtWidgets.QGridLayout()
        self.whole_grid.setObjectName("whole_grid")
        self.frame_vtk = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_vtk.sizePolicy().hasHeightForWidth())
        self.frame_vtk.setSizePolicy(sizePolicy)
        self.frame_vtk.setMinimumSize(QtCore.QSize(400, 400))
        self.frame_vtk.setAcceptDrops(True)
        self.frame_vtk.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_vtk.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_vtk.setObjectName("frame_vtk")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_vtk)
        self.gridLayout.setObjectName("gridLayout")
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame_vtk)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vtkWidget.sizePolicy().hasHeightForWidth())
        self.vtkWidget.setSizePolicy(sizePolicy)
        self.vtkWidget.setMinimumSize(QtCore.QSize(400, 400))
        self.vtkWidget.setObjectName("vtkWidget")
        self.gridLayout.addWidget(self.vtkWidget, 0, 0, 1, 1)
        self.whole_grid.addWidget(self.frame_vtk, 0, 0, 1, 1)
        self.frame_sidebar = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_sidebar.sizePolicy().hasHeightForWidth())
        self.frame_sidebar.setSizePolicy(sizePolicy)
        self.frame_sidebar.setMinimumSize(QtCore.QSize(250, 400))
        self.frame_sidebar.setMaximumSize(QtCore.QSize(250, 16777215))
        self.frame_sidebar.setAcceptDrops(True)
        self.frame_sidebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sidebar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sidebar.setObjectName("frame_sidebar")
        self.sidebar_layout = QtWidgets.QGridLayout(self.frame_sidebar)
        self.sidebar_layout.setObjectName("sidebar_layout")
        self.sidebar = QtWidgets.QGroupBox(self.frame_sidebar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidebar.sizePolicy().hasHeightForWidth())
        self.sidebar.setSizePolicy(sizePolicy)
        self.sidebar.setMinimumSize(QtCore.QSize(250, 400))
        self.sidebar.setMaximumSize(QtCore.QSize(250, 16777215))
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout.addWidget(self.sidebar, 0, 0, 1, 1)
        self.whole_grid.addWidget(self.frame_sidebar, 0, 1, 1, 1)
        self.frame_bottom = QtWidgets.QFrame(self.centralwidget)
        self.frame_bottom.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_bottom.sizePolicy().hasHeightForWidth())
        self.frame_bottom.setSizePolicy(sizePolicy)
        self.frame_bottom.setMinimumSize(QtCore.QSize(650, 70))
        self.frame_bottom.setMaximumSize(QtCore.QSize(16777215, 70))
        self.frame_bottom.setAcceptDrops(True)
        self.frame_bottom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_bottom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_bottom.setObjectName("frame_bottom")
        self.bottom_layout = QtWidgets.QGridLayout(self.frame_bottom)
        self.bottom_layout.setObjectName("bottom_layout")
        self.high_thresh_slider = QtWidgets.QSlider(self.frame_bottom)
        self.high_thresh_slider.setMinimumSize(QtCore.QSize(400, 30))
        self.high_thresh_slider.setMaximumSize(QtCore.QSize(16777215, 30))
        self.high_thresh_slider.setOrientation(QtCore.Qt.Horizontal)
        self.high_thresh_slider.setObjectName("high_thresh_slider")
        self.bottom_layout.addWidget(self.high_thresh_slider, 0, 0, 1, 1)
        self.high_thresh_text = QtWidgets.QLineEdit(self.frame_bottom)
        self.high_thresh_text.setMinimumSize(QtCore.QSize(250, 30))
        self.high_thresh_text.setMaximumSize(QtCore.QSize(250, 30))
        self.high_thresh_text.setObjectName("high_thresh_text")
        self.bottom_layout.addWidget(self.high_thresh_text, 0, 1, 1, 1)
        self.low_thresh_slider = QtWidgets.QSlider(self.frame_bottom)
        self.low_thresh_slider.setMinimumSize(QtCore.QSize(400, 30))
        self.low_thresh_slider.setMaximumSize(QtCore.QSize(16777215, 30))
        self.low_thresh_slider.setOrientation(QtCore.Qt.Horizontal)
        self.low_thresh_slider.setObjectName("low_thresh_slider")
        self.bottom_layout.addWidget(self.low_thresh_slider, 1, 0, 1, 1)
        self.low_thresh_text = QtWidgets.QLineEdit(self.frame_bottom)
        self.low_thresh_text.setMinimumSize(QtCore.QSize(250, 30))
        self.low_thresh_text.setMaximumSize(QtCore.QSize(250, 30))
        self.low_thresh_text.setObjectName("low_thresh_text")
        self.bottom_layout.addWidget(self.low_thresh_text, 1, 1, 1, 1)
        self.whole_grid.addWidget(self.frame_bottom, 1, 0, 1, 2)
        self.gridLayout_5.addLayout(self.whole_grid, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1211, 22))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_compute = QtWidgets.QMenu(self.menubar)
        self.menu_compute.setObjectName("menu_compute")
        self.menu_segmentations = QtWidgets.QMenu(self.menubar)
        self.menu_segmentations.setObjectName("menu_segmentations")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")
        self.menu_visualizations = QtWidgets.QMenu(self.menubar)
        self.menu_visualizations.setObjectName("menu_visualizations")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_load_ply = QtWidgets.QAction(MainWindow)
        self.action_load_ply.setObjectName("action_load_ply")
        self.action_load_feature_vector_file = QtWidgets.QAction(MainWindow)
        self.action_load_feature_vector_file.setEnabled(False)
        self.action_load_feature_vector_file.setObjectName("action_load_feature_vector_file")
        self.action_save_segmentation_label_txt = QtWidgets.QAction(MainWindow)
        self.action_save_segmentation_label_txt.setEnabled(False)
        self.action_save_segmentation_label_txt.setObjectName("action_save_segmentation_label_txt")
        self.action_load_label_txt = QtWidgets.QAction(MainWindow)
        self.action_load_label_txt.setEnabled(False)
        self.action_load_label_txt.setObjectName("action_load_label_txt")
        self.action_compute_morse_complex = QtWidgets.QAction(MainWindow)
        self.action_compute_morse_complex.setEnabled(False)
        self.action_compute_morse_complex.setObjectName("action_compute_morse_complex")
        self.action_morse_cells_persistence = QtWidgets.QAction(MainWindow)
        self.action_morse_cells_persistence.setEnabled(False)
        self.action_morse_cells_persistence.setObjectName("action_morse_cells_persistence")
        self.action_cluster = QtWidgets.QAction(MainWindow)
        self.action_cluster.setEnabled(False)
        self.action_cluster.setObjectName("action_cluster")
        self.action_segmentation_method = QtWidgets.QAction(MainWindow)
        self.action_segmentation_method.setEnabled(False)
        self.action_segmentation_method.setObjectName("action_segmentation_method")
        self.action_cluster_segmentation_method = QtWidgets.QAction(MainWindow)
        self.action_cluster_segmentation_method.setEnabled(False)
        self.action_cluster_segmentation_method.setObjectName("action_cluster_segmentation_method")
        self.action_morse_segementation_ridge_first = QtWidgets.QAction(MainWindow)
        self.action_morse_segementation_ridge_first.setEnabled(False)
        self.action_morse_segementation_ridge_first.setObjectName("action_morse_segementation_ridge_first")
        self.action_quick_guide = QtWidgets.QAction(MainWindow)
        self.action_quick_guide.setObjectName("action_quick_guide")
        self.action_info_contact = QtWidgets.QAction(MainWindow)
        self.action_info_contact.setObjectName("action_info_contact")
        self.action_morse_segmentation_conforming = QtWidgets.QAction(MainWindow)
        self.action_morse_segmentation_conforming.setCheckable(False)
        self.action_morse_segmentation_conforming.setEnabled(False)
        self.action_morse_segmentation_conforming.setObjectName("action_morse_segmentation_conforming")
        self.action_load_conforming_labels_label_txt = QtWidgets.QAction(MainWindow)
        self.action_load_conforming_labels_label_txt.setEnabled(False)
        self.action_load_conforming_labels_label_txt.setObjectName("action_load_conforming_labels_label_txt")
        self.action_merging_steps = QtWidgets.QAction(MainWindow)
        self.action_merging_steps.setEnabled(False)
        self.action_merging_steps.setObjectName("action_merging_steps")
        self.action_load_Txt_Funvals = QtWidgets.QAction(MainWindow)
        self.action_load_Txt_Funvals.setEnabled(False)
        self.action_load_Txt_Funvals.setObjectName("action_load_Txt_Funvals")
        self.action_cluster_edges = QtWidgets.QAction(MainWindow)
        self.action_cluster_edges.setEnabled(False)
        self.action_cluster_edges.setObjectName("action_cluster_edges")
        self.menu_file.addAction(self.action_load_ply)
        self.menu_file.addAction(self.action_load_feature_vector_file)
        self.menu_file.addAction(self.action_save_segmentation_label_txt)
        self.menu_file.addAction(self.action_load_label_txt)
        self.menu_file.addAction(self.action_load_conforming_labels_label_txt)
        self.menu_compute.addAction(self.action_compute_morse_complex)
        self.menu_segmentations.addAction(self.action_segmentation_method)
        self.menu_segmentations.addAction(self.action_cluster_segmentation_method)
        self.menu_segmentations.addAction(self.action_morse_cells_persistence)
        self.menu_segmentations.addAction(self.action_cluster)
        self.menu_segmentations.addAction(self.action_morse_segementation_ridge_first)
        self.menu_segmentations.addAction(self.action_morse_segmentation_conforming)
        self.menu_help.addAction(self.action_quick_guide)
        self.menu_help.addAction(self.action_info_contact)
        self.menu_visualizations.addAction(self.action_merging_steps)
        self.menu_visualizations.addAction(self.action_load_Txt_Funvals)
        self.menu_visualizations.addAction(self.action_cluster_edges)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_compute.menuAction())
        self.menubar.addAction(self.menu_segmentations.menuAction())
        self.menubar.addAction(self.menu_visualizations.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MorseMesh"))
        self.sidebar.setTitle(_translate("MainWindow", "Parameter Settings"))
        self.high_thresh_text.setText(_translate("MainWindow", "high thresh: "))
        self.low_thresh_text.setText(_translate("MainWindow", "low thresh: "))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.menu_compute.setTitle(_translate("MainWindow", "Compute"))
        self.menu_segmentations.setTitle(_translate("MainWindow", "Segmentations"))
        self.menu_help.setTitle(_translate("MainWindow", "Help"))
        self.menu_visualizations.setTitle(_translate("MainWindow", "Visualizations"))
        self.action_load_ply.setText(_translate("MainWindow", "Load ply"))
        self.action_load_feature_vector_file.setText(_translate("MainWindow", "Load feature vector file"))
        self.action_save_segmentation_label_txt.setText(_translate("MainWindow", "Save segmentation (label txt)"))
        self.action_load_label_txt.setText(_translate("MainWindow", "Load label txt"))
        self.action_compute_morse_complex.setText(_translate("MainWindow", "Compute Morse complex"))
        self.action_morse_cells_persistence.setText(_translate("MainWindow", "Morse cells (persistence)"))
        self.action_cluster.setText(_translate("MainWindow", "Cluster"))
        self.action_segmentation_method.setText(_translate("MainWindow", "Morse segmentation method"))
        self.action_cluster_segmentation_method.setText(_translate("MainWindow", "Cluster segmentation method"))
        self.action_morse_segementation_ridge_first.setText(_translate("MainWindow", "Morse segementation (ridge first)"))
        self.action_quick_guide.setText(_translate("MainWindow", "Quick Guide"))
        self.action_info_contact.setText(_translate("MainWindow", "Info/Contact"))
        self.action_morse_segmentation_conforming.setText(_translate("MainWindow", "Morse segmentation (conforming)"))
        self.action_load_conforming_labels_label_txt.setText(_translate("MainWindow", "Load conforming labels (label txt)"))
        self.action_merging_steps.setText(_translate("MainWindow", "Merging Steps (Beta)"))
        self.action_load_Txt_Funvals.setText(_translate("MainWindow", "load Txt Funvals"))
        self.action_cluster_edges.setText(_translate("MainWindow", "cluster around edges"))
