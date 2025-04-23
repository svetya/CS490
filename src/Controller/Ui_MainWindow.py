import sys
import os
import uuid
import random
import requests
import cv2
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QMovie, QIcon, QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import (
    QApplication, QMenuBar, QStatusBar, QStackedLayout, QSpacerItem, QSizePolicy,
    QMainWindow, QFrame, QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox,
    QSpinBox, QPushButton, QHBoxLayout, QDialog, QFormLayout, QFileDialog
)

from ultralytics import YOLO

from view.CameraThread import CameraThread
from view.VideoThread import VideoThread
from Controller.SettingsDialog import SettingsDialog


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
    
class MyWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.green)
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawLine(50, 50, 200, 200)


class Ui_MainWindow(object):

    def update_frame(self, frame):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
            self.ImageFeedLabel.clear()  # Clears the GIF from the label

    # Convert to RGB and display in label
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


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        # Palette (your palette setup code remains the same)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
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
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
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
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(18, 123, 123))
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

        # Central Widget & Layouts
        self.horizontalLayout = QtWidgets.QHBoxLayout()
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
        self.movie = QMovie("resources/welcome.gif")
        self.ImageFeedLabel.setMovie(self.movie)
        self.movie.start()
        
        self.gridLayout.addWidget(self.ImageFeedLabel, 2, 1, 1, 3)

       
        # Gear GIF (QLabel with Movie)
        self.gear_widget = QtWidgets.QLabel(self.centralwidget)
        self.gear_widget.setAlignment(QtCore.Qt.AlignCenter)  # Align center
        self.gear_movie = QMovie("resources/settings1.gif")
        self.gear_widget.setMovie(self.gear_movie)
        self.gear_movie.start()

        # Add gear widget to your grid layout (adjust row/column as needed)
        self.gridLayout.addWidget(self.gear_widget, 1, 0, 1, 1)  # Example: position it at row 0, column 0

        # Transparent clickable Gear button
        self.gear_button = QtWidgets.QPushButton(self.centralwidget)
        self.gear_button.setStyleSheet("background-color: transparent; border: none;")
        self.gear_button.setFixedSize(80, 80)  # Same size as the GIF
        self.gear_button.clicked.connect(self.show_settings_dialog)

        # Add gear button to the same grid layout (same position as the GIF)
        self.gridLayout.addWidget(self.gear_button, 1, 0, 1, 1)

        # Lightbulb GIF (QLabel with Movie)
        self.lightbulb_widget = QtWidgets.QLabel(self.centralwidget)
        self.lightbulb_widget.setAlignment(QtCore.Qt.AlignCenter)  # Align center
        self.lightbulb_movie = QMovie("resources/lightbulb1.gif")
        self.lightbulb_widget.setMovie(self.lightbulb_movie)
        self.lightbulb_movie.start()

        # Add lightbulb widget to your grid layout at the top-right corner
        self.gridLayout.addWidget(self.lightbulb_widget, 1, 4, 1, 1)  # Position it at row 0, column 3 (right side)

        # Transparent clickable Lightbulb button
        self.lightbulb_button = QtWidgets.QPushButton(self.centralwidget)
        self.lightbulb_button.setToolTip("Lightbulb Action")
        self.lightbulb_button.setStyleSheet("background-color: transparent; border: none;")
        self.lightbulb_button.setFixedSize(80, 80)  # Same size as the GIF
        self.lightbulb_button.clicked.connect(self.scan_dialog)

        # Add lightbulb button to the same grid layout (same position as the GIF)
        self.gridLayout.addWidget(self.lightbulb_button, 1, 4, 1, 1)  # Ensure it overlays the GIF


        #------Add Gear and Lightbulb to the Layout----------
        #self.horizontalLayout.addWidget(self.gear_widget)
        #self.horizontalLayout.addWidget(self.lightbulb_widget)

        #------Live Feed Button Setup--------------------------
        self.LiveFeedButton = QtWidgets.QPushButton(self.centralwidget)
        self.LiveFeedButton.setObjectName("LiveFeedButton")
        self.LiveFeedButton.setText("Live Feed")
        self.LiveFeedButton.clicked.connect(self.start_camera)
        self.horizontalLayout.addWidget(self.LiveFeedButton)

        #------Upload Image Button Setup-----------------------
        self.UploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.UploadButton.setObjectName("UploadButton")
        self.UploadButton.setText("Upload Image or Videos")
        self.UploadButton.clicked.connect(self.openFileDialog)
        self.horizontalLayout.addWidget(self.UploadButton)

        self.horizontalLayout.setAlignment(QtCore.Qt.AlignRight)  # Align to the right (or use AlignCenter for center)


        #------Styling for the Buttons--------------------------
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
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #99e8b2, stop:0.33 #75d894, stop:0.66 #43c26b, stop:1 #11a840);
        }
        QPushButton#LiveFeedButton:pressed {
            padding-left: 12px;
            padding-top: 12px;
            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        """)

        # Same for the Upload Button
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
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #99e8b2, stop:0.33 #75d894, stop:0.66 #43c26b, stop:1 #11a840);
        }
        QPushButton#UploadButton:pressed {
            padding-left: 12px;
            padding-top: 12px;
            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        """)

        #------Add Layout to Grid--------------------------
        self.gridLayout.addLayout(self.horizontalLayout, 3, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

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
        font.setFamily("Helvetica")
        font.setPointSize(60)
        self.TitleLabel.setFont(font)
        self.TitleLabel.setObjectName("TitleLabel")
        self.TitleLabel.setText("SmartBin")  # Set the text for the title label
        self.TitleLabel.setStyleSheet("color: white;") 

        # Add the TitleLabel to the grid layout at row 2, column 2, and center it (adjusted)
        self.gridLayout.addWidget(self.TitleLabel, 1, 2, 1, 1, QtCore.Qt.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)

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
                "Plastic": [4,5,7,21,24, 27, 29, 35, 36, 37, 38, 39, 44, 47, 48, 49, 55],  # 'bottle'
                "Paper": [20,30,31,32,33,34,40,56,59],    # 'cup'
                "Glass": [6,9,23,26],    # 'bottle'
                "Metal": [0,1,2,8,10,11,12,18,28,50,52],    # 'can'
                "Cardboard": [13, 14, 15, 16, 17, 18, 19,45,] # 'box'
                # "Organic": 52    # 'banana'
            }
            
            for cls_name, checkbox in dialog.class_checkboxes.items():
                if checkbox.isChecked() and cls_name in class_mapping:
                    indices = class_mapping[cls_name]
                    if isinstance(indices, list):
                        class_indices.extend(indices)  # Add all class IDs
                    else:
                        class_indices.append(indices)  # Add single class ID

            # Set classes to None if all are selected
            classes = None if len(class_indices) == len(dialog.class_checkboxes) else class_indices
            
            # Update settings
            self.settings = {
                'camera_index': camera_index,
                'model_path': "AI_Models\\" + model_path,
                'confidence': confidence,
                'classes': classes
            }
            
            # If camera thread is running, restart it with new settings
            if self.camera_thread and self.camera_thread.isRunning():
                self.stop_camera()
                self.start_camera()
    
    def displayVideo(self, file_path):
        self.stop_camera()  #stop camera just in case
        #stop other from playing
        if hasattr(self, 'video_thread') and self.video_thread.isRunning():
            self.video_thread.stop()
        #use video thread
        self.video_thread = VideoThread(
            file_path, 
            self.settings['model_path'],
            self.settings['confidence'],
            self.settings['classes']
            )
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    # def update_image(self, qt_img, raw_frame):
    #     """Update QLabel with new frame"""
    #     pixmap = QtGui.QPixmap.fromImage(qt_img)  #convert
    #     self.ImageFeedLabel.setPixmap(pixmap)

    #     if raw_frame is not None:
    #         self.latest_frame = raw_frame  # Store the current frame

    def openFileDialog(self):
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

    def update_image(self, qt_img):
       """Update QLabel with new frame"""
       self.ImageFeedLabel.setPixmap(QtGui.QPixmap.fromImage(qt_img))


    def displayImage(self, file_path):
        """Display the selected image in the QLabel."""
        model = YOLO(self.settings['model_path'])
        results = model(file_path,conf=self.settings['confidence'], classes=self.settings['classes'])
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
        if not hasattr(self, 'last_uploaded_file') and not hasattr(self, 'latest_frame'):
            QtWidgets.QMessageBox.warning(self.centralwidget, "No Input", "Please upload an image/video or start the camera first.")
            return

        model = YOLO(self.settings['model_path'])

        # Decide what to scan: frame or image file
        frame_to_scan = None
        if hasattr(self, 'latest_frame') and self.latest_frame is not None:
            frame_to_scan = self.latest_frame
        elif self.last_uploaded_file:
            frame_to_scan = self.last_uploaded_file
        else:
            QtWidgets.QMessageBox.warning(self.centralwidget, "No Frame", "No valid image or video frame to scan.")
            return

        results = model(frame_to_scan)
        # mapping for categories
        label_to_category_id = {
            # 1. Paper Material
            "toilet tube": 1,
            "other carton": 1,
            "egg carton": 1,
            "drink carton": 1,
            "corrugated carton": 1,
            "meal carton": 1,
            "pizza box": 1,
            "paper cup": 1,
            "magazine paper": 1,
            "tissues": 1,
            "wrapping paper": 1,
            "normal paper": 1,
            "paper bag": 1,
            "paper straw": 1,
            
            # 2. Plastic Material
            "aluminium blister pack": 2,  
            "carded blister pack": 2,
            "other plastic bottle": 2,
            "clear plastic bottle": 2,
            "plastic bottle cap": 2,
            "disposable plastic cup": 2,
            "other plastic cup": 2,
            "plastic lid": 2,
            "other plastic": 2,
            "plastified paper bag": 2,
            "plastic film": 2,
            "six pack rings": 2,
            "garbage bag": 2,
            "other plastic wrapper": 2,
            "single-use carrier bag": 2,
            "polypropylene bag": 2,
            "crisp packet": 2,
            "spread tub": 2,
            "tupperware": 2,
            "disposable food container": 2,
            "foam food container": 2,
            "other plastic container": 2,
            "plastic glooves": 2,
            "plastic utensils": 2,
            "squeezable tube": 2,
            "plastic straw": 2,
            "styrofoam piece": 2,

            # 3. Glass Material
            "glass bottle": 3,
            "broken glass": 3,
            "glass cup": 3,
            "glass jar": 3,

            # 4. Metal Material
            "aluminium foil": 4,
            "metal bottle cap": 4,
            "food Can": 4,
            "aerosol": 4,
            "drink can": 4,
            "metal lid": 4,
            "pop tab": 4,
            "scrap metal": 4,

            # 5. Hazardous Material
            "battery": 5,
            "cigarette": 5,
            "unlabeled litter": 5,

            # 6. Organic Waste
            "food waste": 6,

            # 7. Electronic Waste

            # 8. Medical Waste

            # 9. Sludge
           
            # 10. Textile
            "shoe": 10,
            "rope & strings": 10
        }

        #model
        #model = YOLO(self.settings['model_path'])
        #file_path = self.last_uploaded_file  #set last uploaded file path

        #inference with yolo
        #results = model(file_path)

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
            result_text += "\nSmart Tips:\n"
            for category_id in set(category_ids):  #avoid repeating categories
                tips = get_tips_for_category(category_id)
                print(f"Tips for category {category_id}: {tips}")  #log the response for debugging
                
                if tips:
                    for tip in tips:
                        result_text += f"  📝 {tip['title']}: {tip['content']}\n"
                else:
                    result_text += f"  No tips available for category {category_id}.\n"
            result_text += "\nSmart Guidelines:\n"
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
