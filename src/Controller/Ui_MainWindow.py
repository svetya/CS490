from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import cv2
from ultralytics import YOLO
import os
from View.CameraThread import CameraThread
from View.VideoThread import VideoThread
from Controller.SettingsDialog import SettingsDialog
import uuid
import requests

from PyQt5.QtGui import QMovie

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

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
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
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
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
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(1, 111, 111))
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

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.SettingsButton = QtWidgets.QPushButton(self.centralwidget)
        self.SettingsButton.setObjectName("SettingsButton")
        self.SettingsButton.clicked.connect(self.show_settings_dialog)  # Connect settings button
        self.gridLayout.addWidget(self.SettingsButton, 0, 0, 1, 1)
        self.ScanButton = QtWidgets.QPushButton(self.centralwidget)
        self.ScanButton.setObjectName("ScanButton")
        self.ScanButton.clicked.connect(self.scan_dialog)  # Connect scanning button
        self.gridLayout.addWidget(self.ScanButton, 0, 4, 1, 1)
        self.ImageFeedLabel = QtWidgets.QLabel(self.centralwidget)
        self.ImageFeedLabel.setObjectName("ImageFeedLabel")
        self.gridLayout.addWidget(self.ImageFeedLabel, 1, 1, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(118, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.LiveFeedButton = QtWidgets.QPushButton(self.centralwidget)
        self.LiveFeedButton.setObjectName("LiveFeedButton")
        self.LiveFeedButton.clicked.connect(self.start_camera)
        self.horizontalLayout.addWidget(self.LiveFeedButton)
        self.UploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.UploadButton.setObjectName("UploadButton")
        self.UploadButton.clicked.connect(self.openFileDialog)
        self.horizontalLayout.addWidget(self.UploadButton)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(128, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 2)
        self.TitleLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(42)
        self.TitleLabel.setFont(font)
        self.TitleLabel.setObjectName("TitleLabel")
        self.gridLayout.addWidget(self.TitleLabel, 0, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 4, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 441, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.camera_thread = None  # Thread for the camera
        
        # Store a reference to the MainWindow
        self.MainWindow = MainWindow
        
        # Default settings
        self.settings = {
            'camera_index': 0,
            'model_path': 'AI_Models\\CurtisNet.pt',
            'confidence': 0.5,
            'classes': None
        }
        self.last_uploaded_file = None
        self.current_frame = None


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.SettingsButton.setText(_translate("MainWindow", "Settings"))
        self.ScanButton.setText(_translate("MainWindow", "Scan"))
        #self.ImageFeedLabel.setText(_translate("MainWindow", "TextLabel"))
        self.LiveFeedButton.setText(_translate("MainWindow", "Live Feed"))
        self.UploadButton.setText(_translate("MainWindow", "Upload"))
        self.TitleLabel.setText(_translate("MainWindow", "SmartBin"))
       
     ##GIF
        self.ImageFeedLabel = QtWidgets.QLabel(self.centralwidget)
        self.ImageFeedLabel.setObjectName("ImageFeedLabel")
        self.ImageFeedLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        self.movie = QMovie("resources/painting.gif")
        #self.movie = QMovie("/Users/svetyak/Documents/SmartBin2025/SBa18/CS490/resources/painting.gif")
        #self.movie.setScaledSize(QSize(300, 300))  # Optional resize
        self.gridLayout.addWidget(self.ImageFeedLabel, 1, 1, 1, 3)

        self.ImageFeedLabel.setMovie(self.movie)
        self.movie.start()
    
    
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
            "paper": 1,         #1. Paper Material
            "poster": 1,
            "cardboard": 1,

            "vase": 2,          #2. Plastic Material
            "bottle": 2,
            "plastic bag": 2,

            "glass": 3,         #3. Glass Material
            "glass bottle": 3,

            "can": 4,           #4. Metal Material
            "tin": 4,

            "battery": 5,         #5. Hazardous Material
            "phone": 5,

            "banana peel": 6,     #6. Organic Waste

            "laptop": 4,          # Electronic Waste
            "syringe": 5,         # Medical Waste
            "sludge": 6,           # Sludge
            "motorcycle": 4
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
