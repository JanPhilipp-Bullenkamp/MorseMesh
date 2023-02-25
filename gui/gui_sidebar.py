from PyQt5.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QLineEdit, QCheckBox

class SideBar:
    def __init__(self, layout, parameters):
        # Create the sidebar group box
        self.sidebar = QGroupBox("Further Parameters:")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setMaximumSize(175, 400)

        self.create_boxes(parameters)
        
        # connect the stateChanged signal of the boxes to a slot
        self.box_ridge.stateChanged.connect(lambda state, checkbox=self.box_ridge: self.check_boxes(state, checkbox, parameters))
        self.box_valley.stateChanged.connect(lambda state, checkbox=self.box_valley: self.check_boxes(state, checkbox, parameters))
        self.box_both.stateChanged.connect(lambda state, checkbox=self.box_both: self.check_boxes(state, checkbox, parameters))

        self.add_boxes_to_sidebar_layout()
        self.connect_update_boxes(parameters)
        self.connect_update_functions_to_boxes(parameters)
        
        # Add the sidebar to the main layout
        layout.addWidget(self.sidebar,0,1)

    def create_boxes(self, parameters):
        # Create the input widgets and their default values
        self.param1_input = QLineEdit()
        self.param1_input.setText(str(parameters.persistence))
        self.param1_input.setMaximumSize(75, 25)
        self.param2_input = QLineEdit()
        self.param2_input.setText(str(parameters.merge_threshold))
        self.param2_input.setMaximumSize(75, 25)
        self.param3_input = QLineEdit()
        self.param3_input.setText(str(parameters.cluster_seed_number))
        self.param3_input.setMaximumSize(75, 25)
        self.param4_input = QLineEdit()
        self.param4_input.setText(str(parameters.high_thresh))
        self.param4_input.setMaximumSize(75, 25)
        self.param5_input = QLineEdit()
        self.param5_input.setText(str(parameters.low_thresh))
        self.param5_input.setMaximumSize(75, 25)
        self.param6_input = QLineEdit()
        self.param6_input.setText(str(parameters.size_threshold))
        self.param6_input.setMaximumSize(75, 25)

        self.param8_input = QLineEdit()
        self.param8_input.setText(str(parameters.min_length))
        self.param8_input.setMaximumSize(75, 25)
        self.param9_input = QLineEdit()
        self.param9_input.setText(str(parameters.max_length))
        self.param9_input.setMaximumSize(75, 25)

        # create three checkable boxes
        self.box_ridge = QCheckBox("Ridges", checked=True)
        self.box_valley = QCheckBox("Valleys", checked=False)
        self.box_both = QCheckBox("Both", checked=False)
        parameters.mode = "ridge"

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
        self.sidebar_layout.addWidget(QLabel("Min separatrix length"))
        self.sidebar_layout.addWidget(self.param8_input)
        self.sidebar_layout.addWidget(QLabel("Max separatrix length"))
        self.sidebar_layout.addWidget(self.param9_input)
    
        # add the boxes to the layout
        self.sidebar_layout.addWidget(self.box_ridge)
        self.sidebar_layout.addWidget(self.box_valley)
        self.sidebar_layout.addWidget(self.box_both)

    def connect_update_boxes(self, parameters):
        # connect the stateChanged signal of the boxes to a slot
        self.box_ridge.stateChanged.connect(lambda state, checkbox=self.box_ridge: self.check_boxes(state, checkbox, parameters))
        self.box_valley.stateChanged.connect(lambda state, checkbox=self.box_valley: self.check_boxes(state, checkbox, parameters))
        self.box_both.stateChanged.connect(lambda state, checkbox=self.box_both: self.check_boxes(state, checkbox, parameters))

    
    def check_boxes(self, state, checkbox, parameters):
        boxes = [self.box_ridge, self.box_valley, self.box_both]
        checked_boxes = [box for box in boxes if box.isChecked()]

        # make sure exactly one box is checked
        if len(checked_boxes) == 0:
            checkbox.setChecked(True)
        elif len(checked_boxes) > 1:
            for box in boxes:
                if box != checkbox:
                    box.setChecked(False)

        if self.box_ridge.isChecked():
            parameters.mode = "ridge"
        elif self.box_valley.isChecked():
            parameters.mode = "valley"
        elif self.box_both.isChecked():
            parameters.mode = "both"
        else:
            raise ValueError("One of the ridge/valley/both boxes should be checked at all times!")

    def connect_update_functions_to_boxes(self, parameters):
        self.param1_input.editingFinished.connect(lambda: parameters.update(float(self.param1_input.text()), "persistence"))
        self.param2_input.editingFinished.connect(lambda: parameters.update(float(self.param2_input.text()), "merge_threshold"))
        self.param3_input.editingFinished.connect(lambda: parameters.update(int(self.param3_input.text()), "cluster_seed_number"))
        self.param4_input.editingFinished.connect(lambda: parameters.update(float(self.param4_input.text()), "high_thresh"))
        self.param5_input.editingFinished.connect(lambda: parameters.update(float(self.param5_input.text()), "low_thresh"))
        self.param6_input.editingFinished.connect(lambda: parameters.update(int(self.param6_input.text()), "size_threshold"))
        self.param8_input.editingFinished.connect(lambda: parameters.update(int(self.param8_input.text()), "min_length"))
        self.param9_input.editingFinished.connect(lambda: parameters.update(int(self.param9_input.text()), "max_length"))
