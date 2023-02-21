
from PyQt5.QtWidgets import QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt

class Slider:
    def __init__(self, layout, parameters):
        # Create the slider and set its range and default value
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setRange(0,100)
        self.slider1.setValue(parameters.high_percent)
        # Create a label to display above the first slider
        self.label1 = QLabel("High edge threshold: {} % -> {}".format(parameters.high_percent, parameters.high_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider1.valueChanged.connect(lambda value: self.update_high_thresh(value, self.label1))
        

        # Create the slider and set its range and default value
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0,100)
        self.slider2.setValue(parameters.low_percent)
        # Create a label to display above the second slider
        self.label2 = QLabel("Low edge threshold: {} % -> {}".format(parameters.low_percent, parameters.low_thresh))
        
        # Connect the valueChanged signal of the slider to the update_parameter function
        self.slider2.valueChanged.connect(lambda value: self.update_low_thresh(value, self.label2))

        layout.addWidget(self.label1,1,0)
        layout.addWidget(self.slider1,2,0)
        layout.addWidget(self.label2,3,0)
        layout.addWidget(self.slider2,4,0)

        # Create the exit button
        self.exit_button = QPushButton("Close Sliders")
        # Connect the clicked signal to the remove_sliders function
        self.exit_button.clicked.connect(self.remove_slider)
        layout.addWidget(self.exit_button)

        # Add the layout to the main window
        #self.window.window.setLayout(layout)

    def remove_slider(self):
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