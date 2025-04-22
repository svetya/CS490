import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from Model.detector import Detector
class VideoThread(QtCore.QThread):
        #change_pixmap_signal = pyqtSignal(QtGui.QImage)
        change_pixmap_signal = pyqtSignal(QtGui.QImage, object)


        def __init__(self, file_path, model_path='yolov8n.pt', confidence=0.5, classes=None):
            super().__init__()
            self.file_path = file_path
            self.model_path = model_path
            #self.run_flag
            self.confidence= confidence
            self.classes=classes
            self._run_flag = True

        def run(self):
            model = Detector(self.model_path, self.confidence)
            cap = cv2.VideoCapture(self.file_path)

            while self._run_flag and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = model.detect(frame, self.confidence, self.classes)
                
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

                #send signal here
                #self.change_pixmap_signal.emit(q_image)
                self.change_pixmap_signal.emit(q_image, frame)

                self.msleep(30)  #30fps

            cap.release()

        def stop(self):
            self._run_flag = False
            self.wait()