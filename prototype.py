import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import numpy as np
from ultralytics import YOLO
import uuid
import requests

from PyQt5.QtWidgets import QApplication, QMenuBar, QStatusBar, QStackedLayout, QSpacerItem, QSizePolicy, QMainWindow, QFrame, QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, QPushButton, QHBoxLayout, QDialog, QFormLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QPushButton, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush
import random

# Load the model
yolo = YOLO('yolov8n.pt')
# Bootstrap Local API
base_url = "http://localhost:5000/wastemanagementapi"



def getColours(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] * 
    (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)

#get all categories
def get_categories():
    response = requests.get(f"{base_url}/categories")
    return response.json()

#get tips for a specific category
def get_tips_for_category(category_id):
    url = f"{base_url}/categories/{category_id}/tips"
    try:
        response = requests.get(url)
        response.raise_for_status()  #HTTPError for bad responses (4xx, 5xx)

        #if the response is empty before attempting to parse it as JSON
        if not response.text.strip():  #the response body is empty
            print(f"Empty response from API for category {category_id}.")
            return []

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return []
    
#get guidelines for a specific category
def get_guidelines_for_category(category_id):
    url = f"{base_url}/categories/{category_id}/guidelines"
    try:
        response = requests.get(url)
        response.raise_for_status()  #HTTPError for bad responses (4xx, 5xx)

        #if the response is empty before attempting to parse it as JSON
        if not response.text.strip():  #the response body is empty
            print(f"Empty response from API for category {category_id}.")
            return []

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return []

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)

        #Background color 
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.setPalette(palette)
        
        #Layouts
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setVerticalSpacing(15)
        #self.button_layout = QtWidgets.QHBoxLayout()

        #Settings title
        self.title_label = QtWidgets.QLabel("SmartBin Settings")
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
    
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
        
        #Model selection
        self.model_label = QtWidgets.QLabel("YOLO Model:")
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(["yolov8n.pt", "WIP"])
        self.form_layout.addRow(self.model_label, self.model_combo)
        
        #Classes to detect
        self.classes_label = QtWidgets.QLabel("Classes to Detect:")
        self.classes_layout = QtWidgets.QVBoxLayout()
        
        #common recyclable items checkboxes
        common_classes = ["Plastic", "Paper", "Glass", "Metal", "Cardboard", "Organic"]
        self.class_checkboxes = {}
        
        for cls in common_classes:
            checkbox = QtWidgets.QCheckBox(cls)
            checkbox.setChecked(True)
            self.class_checkboxes[cls] = checkbox
            self.classes_layout.addWidget(checkbox)
        
        self.form_layout.addRow(self.classes_label, self.classes_layout)
        
        #Adds form to main layout
        self.main_layout.addLayout(self.form_layout)
        
        #Buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        #Connect buttons
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)



class CameraThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, camera_index=0, model_path="yolov8n.pt", confidence=0.5, classes=None):
        super().__init__()
        self.camera_index = camera_index
        self.running = False  # Flag to control the thread
        self.cap = None
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classes = classes  # None means detect all classes

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Pass confidence threshold and classes to the model
                results = self.model(frame, conf=self.confidence, classes=self.classes, verbose=False)[0]
                annotated_frame = results.plot()
                # Convert frame from BGR to RGB
                frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_img = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.change_pixmap_signal.emit(qt_img)
            QtCore.QThread.msleep(30)

    def stop(self):
        self.running = False
        self.wait()
        if self.cap:
            self.cap.release()


class Ui_MainWindow(object):
    def update_frame(self, frame):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
            self.ImageFeedLabel.clear()  #Clears the Welcome GIF from the label
        
    #Convert to RGB and display in label
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_img)

        self.ImageFeedLabel.setPixmap(pixmap.scaled(
            self.ImageFeedLabel.width(),
            self.ImageFeedLabel.height(),
            QtCore.Qt.KeepAspectRatio
        ))

    #video thread
    class VideoThread(QThread):
        change_pixmap_signal = pyqtSignal(QtGui.QImage)

        def __init__(self, file_path, model_path='yolov8n.pt'):
            super().__init__()
            self.file_path = file_path
            self.model_path = model_path
            #self.run_flag
            self._run_flag = True

        def run(self):
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(self.file_path)

            while self._run_flag and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model(frame)
                annotated_frame = results[0].plot()
                annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

                h, w, ch = annotated_frame.shape
                bytes_per_line = ch * w
                q_image = QtGui.QImage(annotated_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

                #send signal here
                self.change_pixmap_signal.emit(q_image)

                self.msleep(30)  #30fps

            cap.release()

        def stop(self):
            self._run_flag = False
            self.wait()


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        #Palette
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 62, 146))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Link, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 26, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.LinkVisited, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 62, 146))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Link, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 26, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.LinkVisited, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(22, 52, 143))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 62, 146))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Link, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 26, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.LinkVisited, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        
        MainWindow.setPalette(palette)
        
        #Central Widget & Layouts
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer_3, 3, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer, 1, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(118, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer, 5, 0, 1, 2)

        self.horizontalSpacer_2 = QSpacerItem(128, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer_2, 5, 3, 1, 2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer_3, 2, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer_4, 2, 4, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer_5, 0, 1, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer_6, 0, 3, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
 # Image feed label (centered GIF)
        self.ImageFeedLabel = QtWidgets.QLabel(self.centralwidget)
        self.ImageFeedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.movie = QMovie("resources/painting.gif")
        self.ImageFeedLabel.setMovie(self.movie)
        self.movie.start()

        self.gridLayout.addWidget(self.ImageFeedLabel, 2, 1, 1, 3)

        self.movie = QMovie("resources/painting.gif")
        self.ImageFeedLabel.setMovie(self.movie)
        self.movie.start()

        #Gear GIF
        self.gear_widget = QWidget(self.centralwidget)
        self.gear_widget.setFixedSize(80, 80)
        gear_layout = QStackedLayout(self.gear_widget)
        gear_layout.setContentsMargins(0, 0, 0, 0)

        self.gear_gif_label = QtWidgets.QLabel(self.centralwidget)
        self.gear_gif_label.setFixedSize(80, 80)  # Make it bigger
        self.gear_movie = QMovie("resources/settings1.gif")
        self.gear_movie.setScaledSize(QtCore.QSize(80, 80))  # Scale GIF to match size
        self.gear_gif_label.setMovie(self.gear_movie)
        self.gear_movie.start()

        # Transparent clickable 
        self.gear_button = QtWidgets.QPushButton(self.centralwidget)
        self.gear_button.setStyleSheet("background-color: transparent; border: none;")
        self.gear_button.setFixedSize(80, 80)
        self.gear_button.clicked.connect(self.show_settings_dialog)

        #-------Lightbulb GIF Button-----------
        #Lightbulb GIF added down here
        self.lightbulb_widget = QtWidgets.QWidget(self.centralwidget)
        self.lightbulb_layout = QtWidgets.QStackedLayout(self.lightbulb_widget)

        self.lightbulb_gif_label = QtWidgets.QLabel(self.centralwidget)
        self.lightbulb_gif_label.setFixedSize(80, 80)  # Set the size of the label
        self.lightbulb_movie = QMovie("resources/lightbulb1.gif")
        self.lightbulb_movie.setScaledSize(QtCore.QSize(80, 80))  # Scale the GIF to fit
        self.lightbulb_gif_label.setMovie(self.lightbulb_movie)
        self.lightbulb_movie.start()

        # Transparent clickable 
        self.lightbulb_button = QtWidgets.QPushButton(self.centralwidget)
        self.lightbulb_button.setToolTip("Lightbulb Action")  # You can customize the tooltip
        self.lightbulb_button.setStyleSheet("background-color: transparent; border: none;")
        self.lightbulb_button.setFixedSize(80, 80)
        self.lightbulb_gif_label.move(50, 300)
        self.lightbulb_button.move(50, 300)
        self.lightbulb_button.clicked.connect(self.scan_dialog)  # Define this slot

       #Image feed label
        self.ImageFeedLabel = QLabel(self.centralwidget)
        self.ImageFeedLabel.setObjectName(u"ImageFeedLabel")
        self.gridLayout.addWidget(self.ImageFeedLabel, 2, 1, 1, 3)
        
        #buttons layout for bottom
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        

        #------Live Feed Button-----
        self.LiveFeedButton = QtWidgets.QPushButton(self.centralwidget)
        self.LiveFeedButton.setObjectName("LiveFeedButton")
        self.LiveFeedButton.clicked.connect(self.start_camera)
        self.horizontalLayout.addWidget(self.LiveFeedButton)

        #LiveFeedButton 
        self.LiveFeedButton.setStyleSheet("""
        QPushButton#LiveFeedButton {
            font-size: 16px;
            padding: 10px 20px;
            background-color: #1558b2;
            color:#FFFFFF;
            border: 2px solid white;
            border-radius: 8px;
            box-shadow: 4px 4px 6px rgba(255, 255, 255, 0.3);
        }

        QPushButton#LiveFeedButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #99e8b2, stop:0.33 #75d894, stop:0.66 #43c26b, stop:1 #11a840);
    }

        QPushButton#LiveFeedButton:pressed {
            padding-left: 12px;
            padding-top: 12px;
            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        """)

        #------Upload Image Button-----
        self.UploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.UploadButton.setObjectName("UploadButton")
        self.UploadButton.clicked.connect(self.openFileDialog)
        self.horizontalLayout.addWidget(self.UploadButton)

        #UploadButton
        self.UploadButton.setStyleSheet("""
            QPushButton#UploadButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #1558b2;
                color:#FFFFFF;
                border: 2px solid white;
                border-radius: 8px;
                box-shadow: 4px 4px 6px rgba(255, 255, 255, 0.3);
            }

            QPushButton#UploadButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #99e8b2, stop:0.33 #75d894, stop:0.66 #43c26b, stop:1 #11a840);
            }

            QPushButton#UploadButton:pressed {
                padding-left: 12px;
                padding-top: 12px;
                box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
       """)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
      
        #------First Title Line------
        self.TitleLine = QtWidgets.QFrame(self.centralwidget)
        self.TitleLine.setFrameShape(QtWidgets.QFrame.HLine)  # Set the frame shape to horizontal line
        self.TitleLine.setFrameShadow(QtWidgets.QFrame.Sunken)  # Set the shadow to sunken
        self.TitleLine.setLineWidth(10)  # Set the line width
        self.TitleLine.setStyleSheet("color: white;")  # Set the color to white

        # Add the first TitleLine to the grid layout at row 1 (adjusted to avoid overlap)
        self.gridLayout.addWidget(self.TitleLine, 0, 0, 1, 5)  # Span across all columns

        #------Second Title Line (Above Title Label)------
        self.SecondTitleLine = QtWidgets.QFrame(self.centralwidget)
        self.SecondTitleLine.setFrameShape(QtWidgets.QFrame.HLine)  # Set the frame shape to horizontal line
        self.SecondTitleLine.setFrameShadow(QtWidgets.QFrame.Sunken)  # Set the shadow to sunken
        self.SecondTitleLine.setLineWidth(10)  # Set the line width
        self.SecondTitleLine.setStyleSheet("color: white;")  # Set the color to white

        # Add the second TitleLine to the grid layout above the TitleLabel (row 1, adjusted)
        self.gridLayout.addWidget(self.SecondTitleLine, 4, 0, 1, 5)  # Span across all columns

        #------Title Label (SmartBin)------
        
        self.TitleLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(42)
        self.TitleLabel.setFont(font)
        self.TitleLabel.setObjectName("TitleLabel")
        self.TitleLabel.setText("SmartBin")  # Set the text for the title label
        self.TitleLabel.setStyleSheet("color: pink;") 

        # Add the TitleLabel to the grid layout at row 2, column 2, and center it (adjusted)
        self.gridLayout.addWidget(self.TitleLabel, 1, 2, 1, 1, QtCore.Qt.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #-----Camera thread and default settings-----
        self.camera_thread = None  # Thread for the camera
        
        # Store a reference to the MainWindow
        self.MainWindow = MainWindow
        
        # Default settings
        self.settings = {
            'camera_index': 0,
            'model_path': 'yolov8n.pt',
            'confidence': 0.5,
            'classes': None
        }
        self.last_uploaded_file = None
        self.current_frame = None


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
         
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.SettingsButton.setText(_translate("MainWindow", "Settings"))
        #self.SettingsButton.setText(_translate("MainWindow", "Settings"))
        #self.ScanButton.setText(_translate("MainWindow", "Scan"))
        #self.ImageFeedLabel.setText(_translate("MainWindow", "TextLabel"))
        self.LiveFeedButton.setText(_translate("MainWindow", "Live Feed"))
        self.UploadButton.setText(_translate("MainWindow", "Upload Image"))
        self.TitleLabel.setText(_translate("MainWindow", "SmartBin"))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    

    def open_settings(self):
        """Open the settings dialog when the gear button is clicked"""
        self.settings_dialog = SettingsDialog(self.MainWindow)

        # Set current values in the dialog
        self.settings_dialog.camera_combo.setCurrentIndex(self.settings['camera_index'])
        self.settings_dialog.model_combo.setCurrentText(self.settings['model_path'])

        # Show the settings dialog
        self.settings_dialog.exec_()

    def show_settings_dialog(self):
        """Open the settings dialog when settings button is clicked"""
        dialog = SettingsDialog(self.MainWindow)
        
        # Set current values in the dialog
        dialog.camera_combo.setCurrentIndex(self.settings['camera_index'])
        dialog.model_combo.setCurrentText(self.settings['model_path'])
        dialog.confidence_slider.setValue(int(self.settings['confidence'] * 100))
        
        # Show dialog and get result
        result = dialog.exec_()
        
        if result == QtWidgets.QDialog.Accepted:
            # Apply settings changes
            camera_index = int(dialog.camera_combo.currentText().split(':')[0])
            model_path = dialog.model_combo.currentText()
            confidence = float(dialog.confidence_value.text())
            
            # Get selected classes
            selected_classes = []
            class_indices = []
            
            # Get class indices based on COCO dataset for the selected checkboxes
            # This is a simplified mapping - you may need to adjust based on your model's classes
            class_mapping = {
                "Plastic": 76,  # 'bottle'
                "Paper": 77,    # 'cup'
                "Glass": 44,    # 'bottle'
                "Metal": 65,    # 'can'
                "Cardboard": 78, # 'box'
                "Organic": 52    # 'banana'
            }
            
            for cls_name, checkbox in dialog.class_checkboxes.items():
                if checkbox.isChecked() and cls_name in class_mapping:
                    class_indices.append(class_mapping[cls_name])
            
            # Set classes to None if all are selected
            classes = None if len(class_indices) == len(dialog.class_checkboxes) else class_indices
            
            # Update settings
            self.settings = {
                'camera_index': camera_index,
                'model_path': model_path,
                'confidence': confidence,
                'classes': classes
            }
            
            # If camera thread is running, restart it with new settings
            if self.camera_thread and self.camera_thread.isRunning():
                self.stop_camera()
                self.start_camera()
    
    def displayVideo(self, file_path, model_path='yolov8n.pt'):
        self.stop_camera()  #stop camera just in case
        #stop other from playing
        if hasattr(self, 'video_thread') and self.video_thread.isRunning():
            self.video_thread.stop()
        #use video thread
        self.video_thread = self.VideoThread(file_path, model_path)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()
   

    def update_image(self, qt_img):
        """Update QLabel with new frame"""
        pixmap = QtGui.QPixmap.fromImage(qt_img)  #convert
        self.ImageFeedLabel.setPixmap(pixmap)

    def openFileDialog(self, model_path='yolov8n.pt'):
        """Open a file dialog to select an image and display it."""
        self.stop_camera()
        options = QFileDialog.Options()
        #file_filter = "Images (*.png *.jpg *.jpeg *.bmp *.gif);;Videos (*.mp4 *.avi *.mov *.mkv)"
        file_filter = "Files (*.png *.jpg *.jpeg *.bmp *.gif *.mp4 *.avi *.mov *.mkv)"
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", "", file_filter, options=options
        )

        if not file_path:
             return

        self.last_uploaded_file = file_path  # Save last uploaded file path

        if self.isVideo(file_path):
            self.displayVideo(file_path)
        else:
            self.displayImage(file_path)

        #if not file_path:
        #    QtWidgets.QMessageBox.warning(self.centralwidget, "No File Selected", "No file was selected.")
        #    return


    def isVideo(self, file_path):
        image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv'}
        ext = os.path.splitext(file_path)[1].lower()
        if ext in video_exts:
            return True
        elif ext in image_exts:
            return False

    def start_camera(self):
        """Start the camera thread with current settings and update UI"""
        if self.camera_thread is None or not self.camera_thread.isRunning():
            self.camera_thread = CameraThread(
                camera_index=self.settings['camera_index'],
                model_path=self.settings['model_path'],
                confidence=self.settings['confidence'],
                classes=self.settings['classes']
            )
            self.camera_thread.change_pixmap_signal.connect(self.update_image)
            self.camera_thread.start()

    def stop_camera(self):
        """Stop the camera thread"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

    #def update_image(self, qt_img):
    #    """Update QLabel with new frame"""
    #    self.ImageFeedLabel.setPixmap(QtGui.QPixmap.fromImage(qt_img))

    def displayImage(self, file_path, model_path="yolov8n.pt"):
        """Display the selected image in the QLabel."""
        model = YOLO(model_path)
        results = model(file_path)
        annotatedFrame = results[0].plot()
        annotatedFrame = cv2.cvtColor(annotatedFrame, cv2.COLOR_BGR2RGB)
        h, w, ch = annotatedFrame.shape
        bytes_per_line = ch * w
        q_image = QtGui.QImage(annotatedFrame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(q_image)
        if pixmap.isNull():
            QtWidgets.QMessageBox.critical(self, "Image Load Error", "Could not load image!")
            return
        pixmap = pixmap.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        self.ImageFeedLabel.setPixmap(pixmap)
        self.ImageFeedLabel.setAlignment(QtCore.Qt.AlignCenter)
        
    def convertFrametoQPixmap(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w 
        q_image = QtGui.QPixmap(frame.data, w,h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return
    
    def scan_dialog(self):
        """Handle scan button click event."""
        if not hasattr(self, 'last_uploaded_file') or self.last_uploaded_file is None:
            QtWidgets.QMessageBox.warning(self.centralwidget, "No File", "Please upload an image or video first.")
            return

        # mapping for categories
        label_to_category_id = {
             "vase": 2,  
             "paper": 1,         #1. Paper Material
             "poster": 1,
             "cardboard": 1,
 
             "vase": 2,          #2. Plastic Material
             "bottle": 2,
             "battery": 2,         # Hazardous Materials
             "banana peel": 3,     # Organic Waste
             "plastic bag": 2,
 
             "glass": 3,         #3. Glass Material
             "glass bottle": 3,
 
             "can": 4,           #4. Metal Material
             "tin": 4,
 
             "battery": 5,         #5. Hazardous Material
             "laptop": 5,
             "phone": 5,
 
             "banana peel": 6,     #6. Organic Waste
 
             "laptop": 4,          # Electronic Waste
             "syringe": 5,         # Medical Waste
             "sludge": 6,           # Sludge
        }

        #model
        model = YOLO(self.settings['model_path'])
        file_path = self.last_uploaded_file  #set last uploaded file path

        #inference with yolo
        results = model(file_path)

        #get ids/scores
        boxes = results[0].boxes  
        confidences = boxes.conf  
        class_ids = boxes.cls  

        #hold class names that align with ids
        object_names = [model.names[int(class_id)] for class_id in class_ids]

        #gather result text for detected objects
        result_text = "Detected objects:\n"
        category_ids = []  #store categories detected

        for name, confidence in zip(object_names, confidences):
            result_text += f"{name}: {confidence:.2f}\n"
            
            #check object matches category in label_to_category_id mapping
            detected_label = name.lower()
            category_id = label_to_category_id.get(detected_label)
            
            if category_id:
                category_ids.append(category_id)

        #for detected objects, collect tips for category
        #also collect guidelines
        if category_ids:
            result_text += "\nTips:\n"
            for category_id in set(category_ids):  #avoid repeating categories
                tips = get_tips_for_category(category_id)
                print(f"Tips for category {category_id}: {tips}")  #log the response for debugging
                
                if tips:
                    for tip in tips:
                        result_text += f"  📝 {tip['title']}: {tip['content']}\n"
                else:
                    result_text += f"  No tips available for category {category_id}.\n"
            result_text += "\nGuidelines:\n"
            for category_id in set(category_ids):  #avoid repeating categories
                guidelines = get_guidelines_for_category(category_id)
                print(f"Guidelines for category {category_id}: {guidelines}")  #log the response for debugging
                
                if guidelines:
                    for guideline in guidelines:
                        result_text += f"  📝 {guideline['title']}: {guideline['instructions']}\n"
                else:
                    result_text += f"  No guideliness available for category {category_id}.\n"
        else:
            result_text += "\nNo relevant categories detected for guidelines."

        #display the result in box on UI
        QtWidgets.QMessageBox.information(self.centralwidget, "Detection Results", result_text)

if __name__ == "__main__": 
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())