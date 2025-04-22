from PyQt5 import QtCore, QtGui
import cv2
from Model.detector import Detector
import numpy as np
from ultralytics import YOLO
import time

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

        self.previous_boxes = {}
        self.alpha = 0.6  # Smoothing factor

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True
        prev_time = time.time()

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time

                results = self.model.track(frame, conf=self.confidence, classes=self.classes,
                                           verbose=False, tracker="bytetrack.yaml")[0]

                for box in results.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    score = float(box.conf)
                    cls_id = int(box.cls)
                    label = self.model.names[cls_id]
                    color = (0, 255, 0)

                    # Filter overly large boxes
                    frame_h, frame_w = frame.shape[:2]
                    if (x2 - x1 > frame_w * 0.9) or (y2 - y1 > frame_h * 0.9):
                        continue

                    # Smooth box
                    key = str(cls_id)
                    if key in self.previous_boxes:
                        px1, py1, px2, py2 = self.previous_boxes[key]
                        x1 = self.alpha * px1 + (1 - self.alpha) * x1
                        y1 = self.alpha * py1 + (1 - self.alpha) * y1
                        x2 = self.alpha * px2 + (1 - self.alpha) * x2
                        y2 = self.alpha * py2 + (1 - self.alpha) * y2
                    self.previous_boxes[key] = (x1, y1, x2, y2)
                    
                    # Draw box and label
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(frame, f"{label} {score:.2f}", (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Draw FPS
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
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
