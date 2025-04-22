from PyQt5 import QtCore, QtGui, QtWidgets

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)

        # Set the background color to match the main application
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.setPalette(palette)
        
        # Create layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        # Settings title
        self.title_label = QtWidgets.QLabel("SmartBin Settings")
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Settings form layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setVerticalSpacing(15)
        
        # Camera settings
        self.cam_label = QtWidgets.QLabel("Camera Settings")
        font = QtGui.QFont()
        font.setBold(True)
        self.cam_label.setFont(font)
        self.main_layout.addWidget(self.cam_label)
        
        # Camera selection
        self.camera_label = QtWidgets.QLabel("Camera Device:")
        self.camera_combo = QtWidgets.QComboBox()
        self.camera_combo.addItems(["0: Default Camera", "1: External Camera"])
        self.form_layout.addRow(self.camera_label, self.camera_combo)
        
        # Detection settings
        self.detection_label = QtWidgets.QLabel("Detection Settings")
        self.detection_label.setFont(font)
        self.main_layout.addWidget(self.detection_label)
        
        # Confidence threshold
        self.confidence_label = QtWidgets.QLabel("Confidence Threshold:")
        self.confidence_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(50)
        self.confidence_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        self.confidence_value = QtWidgets.QLabel("0.5")
        self.confidence_slider.valueChanged.connect(
            lambda value: self.confidence_value.setText(str(value/100))
        )
        
        conf_layout = QtWidgets.QHBoxLayout()
        conf_layout.addWidget(self.confidence_slider)
        conf_layout.addWidget(self.confidence_value)
        self.form_layout.addRow(self.confidence_label, conf_layout)
        
        # Model selection
        self.model_label = QtWidgets.QLabel("YOLO Model:")
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(["CurtisNet.pt","yolov8n.pt", "yolov5nu.pt"])
        self.form_layout.addRow(self.model_label, self.model_combo)
        
        # Classes to detect
        self.classes_label = QtWidgets.QLabel("Classes to Detect:")
        self.classes_layout = QtWidgets.QVBoxLayout()
        
        # Add some common recyclable items as checkboxes
        common_classes = ["Plastic", "Paper", "Glass", "Metal", "Cardboard", "Organic"]
        self.class_checkboxes = {}
        
        for cls in common_classes:
            checkbox = QtWidgets.QCheckBox(cls)
            checkbox.setChecked(True)
            self.class_checkboxes[cls] = checkbox
            self.classes_layout.addWidget(checkbox)
        
        self.form_layout.addRow(self.classes_label, self.classes_layout)
        
        # Add form layout to main layout
        self.main_layout.addLayout(self.form_layout)
        
        # Buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        # Connect buttons
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
