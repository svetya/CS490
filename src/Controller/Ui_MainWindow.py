from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import cv2
from ultralytics import YOLO
import os
from View.CameraThread import CameraThread
from Controller.SettingsDialog import SettingsDialog
import uuid


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
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
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
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
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 255, 232))
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
        self.ImageFeedLabel.setText(_translate("MainWindow", "TextLabel"))
        self.LiveFeedButton.setText(_translate("MainWindow", "Live Feed"))
        self.UploadButton.setText(_translate("MainWindow", "Upload"))
        self.TitleLabel.setText(_translate("MainWindow", "SmartBin"))
        
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
            
            # for cls_name, checkbox in dialog.class_checkboxes.items():
            #     if checkbox.isChecked() and cls_name in class_mapping:
            #         class_indices.append(class_mapping[cls_name])
            
            # # Set classes to None if all are selected
            # classes = None if len(class_indices) == len(dialog.class_checkboxes) else class_indices
            
            for cls_name, checkbox in dialog.class_checkboxes.items():
                if checkbox.isChecked() and cls_name in class_mapping:
                    indices = class_mapping[cls_name]
                    if isinstance(indices, list):
                        class_indices.extend(indices)  # Add all class IDs
                    else:
                        class_indices.append(indices)  # Add single class ID

            # Set classes to None if all are selected (i.e., detect everything)
            classes = None if len(class_indices) == len(dialog.class_checkboxes) else class_indices

            # Update settings
            self.settings = {
                'camera_index': camera_index,
                'model_path': 'AI_Models\\' + model_path,
                'confidence': confidence,
                'classes': classes
            }
            
            # If camera thread is running, restart it with new settings
            if self.camera_thread and self.camera_thread.isRunning():
                self.stop_camera()
                self.start_camera()
    
    def displayVideo(self, file_path, model_path):

        model_path = self.settings(['model_path'])
        change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage)
        model = YOLO(model_path)
        cap = cv2.VideoCapture(file_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.current_frame = frame
            results = model(frame)
            annotated_frame = results[0].plot()
            h, w, ch = annotated_frame.shape
            bytes_per_line = ch * w
            q_image = QtGui.QImage(annotated_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap(q_image)
            if pixmap.isNull():
                QtWidgets.QMessageBox.critical(self, "Image Load Error", "Could not load image!")
                return
            pixmap = pixmap.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
            self.ImageFeedLabel.setPixmap(pixmap)
            self.ImageFeedLabel.setAlignment(QtCore.Qt.AlignCenter)
            change_pixmap_signal.emit(pixmap)

    def openFileDialog(self, model_path='yolov8n.pt'):
        """Open a file dialog to select an image and display it."""
        self.stop_camera()
        options = QFileDialog.Options()
        file_filter = "Images (*.png *.jpg *.jpeg *.bmp *.gif);;Videos (*.mp4 *.avi *.mov *.mkv)"
    
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", "", file_filter, options=options
        )

        self.last_uploaded_file = file_path  # Save last uploaded file path

        if self.isVideo(file_path):
            self.displayVideo(file_path)
        else:
            self.displayImage(file_path)



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
        results = model(file_path)
        annotatedFrame = results[0].plot()
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
        """Handle scan button click event (for image or current video frame)."""

        # Load the model
        model = YOLO(self.settings['model_path'])

        # Determine source for detection
        if hasattr(self, 'last_uploaded_file') and self.last_uploaded_file is not None:
            file_path = self.last_uploaded_file

            # If it's a video, use current frame
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                if hasattr(self, 'current_frame') and self.current_frame is not None:
                    frame = self.current_frame.copy()
                    temp_name = f"screenshot_{uuid.uuid4().hex}.jpg"
                    cv2.imwrite(temp_name, frame)
                    file_path = temp_name
                else:
                    QtWidgets.QMessageBox.warning(self.centralwidget, "No Frame", "No video frame available.")
                    return
        else:
            # If nothing uploaded, fall back to live camera frame
            if hasattr(self, 'current_frame') and self.current_frame is not None:
                frame = self.current_frame.copy()
                temp_name = f"screenshot_{uuid.uuid4().hex}.jpg"
                cv2.imwrite(temp_name, frame)
                file_path = temp_name
            else:
                QtWidgets.QMessageBox.warning(self.centralwidget, "No File", "Please upload a file or use live feed.")
                return

        # Run inference
        results = model(file_path)
        boxes = results[0].boxes
        confidences = boxes.conf
        class_ids = boxes.cls
        object_names = [model.names[int(class_id)] for class_id in class_ids]

        # Display detection results
        result_text = "Detected objects:\n"
        if len(object_names) == 0:
            result_text += "No objects detected."
        else:
            for name, confidence in zip(object_names, confidences):
                result_text += f"{name}: {confidence:.2f}\n"

        QtWidgets.QMessageBox.information(self.centralwidget, "Detection Results", result_text)

        # Show annotated image on the QLabel
        annotated = results[0].plot()
        h, w, ch = annotated.shape
        bytes_per_line = ch * w
        q_image = QtGui.QImage(annotated.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(q_image).scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        self.ImageFeedLabel.setPixmap(pixmap)
        self.ImageFeedLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Clean up temporary file if created
        if 'temp_name' in locals() and os.path.exists(temp_name):
            os.remove(temp_name)