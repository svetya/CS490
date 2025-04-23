from PyQt5 import QtCore, QtGui
import cv2
from Model.detector import Detector
import numpy as np
from ultralytics import YOLO

class CameraThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage)


    def __init__(self, camera_index=0, model_path="CurtisNet.pt", confidence=0.75, classes=None):

        super().__init__()
        self.camera_index = camera_index
        self.running = False  # Flag to control the thread
        self.cap = None
        self.model = Detector(model_path, confidence)
        self.confidence = confidence
        self.classes = classes  # None means detect all classes

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = self.model.detect(frame, self.confidence, self.classes)
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
