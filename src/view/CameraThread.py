from PyQt5 import QtCore, QtGui
import cv2
from Model.detector import Detector
import numpy as np
import time

class CameraThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage, object)

    def __init__(self, camera_index=0, model_path="CurtisNet.pt", confidence=0.75, classes=None):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        self.model = Detector(model_path, confidence)
        self.confidence = confidence
        self.classes = classes
        self.last_frame = None

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True
        prev_time = time.time()

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame.copy()

            
                results = self.model.detect(frame, self.confidence, self.classes, stream=True)

                confidences = []

                for result in results:
                    for box in result.boxes:
                        if box.conf is not None:
                            confidences.append(float(box.conf))

                    frame = result.plot()

                
                current_time = time.time()
                fps = 1.0 / (current_time - prev_time)
                prev_time = current_time

                
                avg_conf = np.mean(confidences) if confidences else 0

                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Avg Conf: {avg_conf:.2f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)

                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_img = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

               
                self.change_pixmap_signal.emit(qt_img, self.last_frame)

            QtCore.QThread.msleep(30)

    def stop(self):
        self.running = False
        self.wait()
        if self.cap:
            self.cap.release()

    def get_current_frame(self):
        return self.last_frame.copy() if self.last_frame is not None else None
