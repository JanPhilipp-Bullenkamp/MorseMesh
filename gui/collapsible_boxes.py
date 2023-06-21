from PyQt5.QtWidgets import (QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QFrame, QLabel,
                             QLineEdit, QCheckBox)


class SectionExpandButton(QPushButton):
    """a QPushbutton that can expand or collapse its section
    """
    def __init__(self, item, text = "", parent = None):
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        """toggle expand/collapse of section by clicking
        """
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)


class CollapsibleDialog(QDialog):
    """a dialog to which collapsible sections can be added;
    subclass and reimplement define_sections() to define sections and
        add them as (title, widget) tuples to self.sections
    """
    def __init__(self, parameters):
        super().__init__()
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        header = QLabel("Parameter Settings:")
        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setIndentation(0)
        self.parameters = parameters

        self.sections = []
        self.define_sections()
        self.add_sections()

    def add_sections(self):
        """adds a collapsible sections for every 
        (title, widget) tuple in self.sections
        """
        for (title, widget) in self.sections:
            button1 = self.add_button(title)
            section1 = self.add_widget(button1, widget)
            button1.addChild(section1)

    def define_sections(self):
        """reimplement this to define all your sections
        and add them as (title, widget) tuples to self.sections
        """
        widget = QFrame(self.tree)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Feat. Vec. Fct."))
        self.feat_vec_fct_input = QLineEdit()
        self.feat_vec_fct_input.setText(str(self.parameters.feature_vector_function))
        layout.addWidget(self.feat_vec_fct_input)
        title = "Data loading:"
        self.sections.append((title, widget))

        widget = QFrame(self.tree)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Seapratrix Density"))
        self.box_all = QCheckBox("All", checked=False)
        self.box_cutoff = QCheckBox("Cutoff", checked=False)
        self.box_reversed = QCheckBox("Reversed", checked=True)
        layout.addWidget(self.box_all)
        layout.addWidget(self.box_cutoff)
        layout.addWidget(self.box_reversed)
        layout.addWidget(QLabel("Min separatrix length"))
        self.min_sepa_length_input = QLineEdit(str(self.parameters.min_length))
        layout.addWidget(self.min_sepa_length_input)
        layout.addWidget(QLabel("Max separatrix length"))
        self.max_sepa_length_input = QLineEdit(str(self.parameters.max_length))
        layout.addWidget(self.max_sepa_length_input)
        layout.addWidget(QLabel("Extremal line type"))
        self.box_ridge = QCheckBox("Ridges", checked=True)
        self.box_valley = QCheckBox("Valleys", checked=False)
        self.box_both = QCheckBox("Both", checked=False)
        layout.addWidget(self.box_ridge)
        layout.addWidget(self.box_valley)
        layout.addWidget(self.box_both)
        title = "Advanced edge detection:"
        self.sections.append((title, widget))

        widget = QFrame(self.tree)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Persistence"))
        self.persistence_input = QLineEdit(str(self.parameters.persistence))
        layout.addWidget(self.persistence_input)
        layout.addWidget(QLabel("Merge threshold"))
        self.merge_threshold_input = QLineEdit(str(self.parameters.merge_threshold))
        layout.addWidget(self.merge_threshold_input)
        layout.addWidget(QLabel("Label size threshold"))
        self.label_size_thresh_input = QLineEdit(str(self.parameters.size_threshold))
        layout.addWidget(self.label_size_thresh_input)
        title = "Morse segmentation:"
        self.sections.append((title, widget))

        widget = QFrame(self.tree)
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Cluster seed number"))
        self.cluster_seed_input = QLineEdit(str(self.parameters.cluster_seed_number))
        layout.addWidget(self.cluster_seed_input)
        layout.addWidget(QLabel("Merge threshold"))
        self.merge_threshold_cluster_input = QLineEdit(str(self.parameters.merge_threshold))
        layout.addWidget(self.merge_threshold_cluster_input)
        title = "Cluster segmentation:"
        self.sections.append((title, widget))

        self.update_boxes()
        self.update_parameters()

    def update_parameters(self):
        self.feat_vec_fct_input.editingFinished.connect(lambda: self.parameters.update(str(self.feat_vec_fct_input.text()), "feature_vector_function"))
        self.persistence_input.editingFinished.connect(lambda: self.parameters.update(float(self.persistence_input.text()), "persistence"))
        self.merge_threshold_input.editingFinished.connect(lambda: self.parameters.update(float(self.merge_threshold_input.text()), "merge_threshold"))
        self.cluster_seed_input.editingFinished.connect(lambda: self.parameters.update(int(self.cluster_seed_input.text()), "cluster_seed_number"))
        self.merge_threshold_cluster_input.editingFinished.connect(lambda: self.parameters.update(float(self.merge_threshold_cluster_input.text()), "merge_threshold_cluster"))
        self.label_size_thresh_input.editingFinished.connect(lambda: self.parameters.update(int(self.label_size_thresh_input.text()), "size_threshold"))
        self.min_sepa_length_input.editingFinished.connect(lambda: self.parameters.update(int(self.min_sepa_length_input.text()), "min_length"))
        self.max_sepa_length_input.editingFinished.connect(lambda: self.parameters.update(int(self.max_sepa_length_input.text()), "max_length"))

    def update_boxes(self):
        # connect the stateChanged signal of the boxes to a slot
        self.box_ridge.stateChanged.connect(lambda state, checkbox=self.box_ridge: 
                                            self.check_boxes(state, 
                                                             checkbox, 
                                                             self.parameters))
        self.box_valley.stateChanged.connect(lambda state, checkbox=self.box_valley: 
                                             self.check_boxes(state, 
                                                              checkbox, 
                                                              self.parameters))
        self.box_both.stateChanged.connect(lambda state, checkbox=self.box_both: 
                                           self.check_boxes(state, 
                                                            checkbox, 
                                                            self.parameters))
        # connect the stateChanged signal of the boxes to a slot
        self.box_all.stateChanged.connect(lambda state, checkbox=self.box_all: 
                                          self.check_sepa_boxes(state, 
                                                                checkbox, 
                                                                self.parameters))
        self.box_cutoff.stateChanged.connect(lambda state, checkbox=self.box_cutoff: 
                                             self.check_sepa_boxes(state, 
                                                                   checkbox, 
                                                                   self.parameters))
        self.box_reversed.stateChanged.connect(lambda state, checkbox=self.box_reversed: 
                                               self.check_sepa_boxes(state, 
                                                                     checkbox, 
                                                                     self.parameters))

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
            raise ValueError("One of the ridge/valley/both boxes should "
                             "be checked at all times!")
        
    def check_sepa_boxes(self, state, checkbox, parameters):
        boxes = [self.box_all, self.box_cutoff, self.box_reversed]
        checked_boxes = [box for box in boxes if box.isChecked()]

        # make sure exactly one box is checked
        if len(checked_boxes) == 0:
            checkbox.setChecked(True)
        elif len(checked_boxes) > 1:
            for box in boxes:
                if box != checkbox:
                    box.setChecked(False)

        if self.box_all.isChecked():
            parameters.separatrix_type = "all"
        elif self.box_cutoff.isChecked():
            parameters.separatrix_type = "cutoff"
        elif self.box_reversed.isChecked():
            parameters.separatrix_type = "reverse"
        else:
            raise ValueError("One of the all/cutoff/reverse boxes "
                             "should be checked at all times!")

    def add_button(self, title):
        """creates a QTreeWidgetItem containing a button 
        to expand or collapse its section
        """
        item = QTreeWidgetItem()
        self.tree.addTopLevelItem(item)
        self.tree.setItemWidget(item, 0, SectionExpandButton(item, text = title))
        return item

    def add_widget(self, button, widget):
        """creates a QWidgetItem containing the widget,
        as child of the button-QWidgetItem
        """
        section = QTreeWidgetItem(button)
        section.setDisabled(True)
        self.tree.setItemWidget(section, 0, widget)
        return section