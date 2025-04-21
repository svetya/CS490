from PyQt5 import QtCore, QtGui
import cv2
from Model.detector import Detector
import numpy as np
from ultralytics import YOLO
import datetime
import os
import time 
class CameraThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, camera_index=0, model_path="CurtisNet.pt", confidence=0.75, classes=None):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classes = classes

        self.previous_boxes = {}  # For smoothing
        self.alpha = 0.6  # Smoothing factor

        self.save_dir = "Missed_detections"
        os.makedirs(self.save_dir, exist_ok=True)

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True
         
        prev_time = time.time()  # For FPS calculation
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # ----- FPS Calculation -----
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time
                results = self.model.track(frame, conf=self.confidence, classes=self.classes,
                                           verbose=False, tracker="bytetrack.yaml")[0]
                dets = []

                for box in results.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    score = float(box.conf)
                    cls_id = int(box.cls)
                    dets.append([x1, y1, x2, y2, score, cls_id])

                dets = np.array(dets)
                if len(dets) > 0:
                    dets_nms = self.soft_nms(dets[:, :5], sigma=0.5, Nt=0.4, threshold=0.3, method='gaussian')

                    for i in range(len(dets_nms)):
                        x1, y1, x2, y2, score = dets_nms[i][:5]
                        cls_id = int(dets[i][5])
                        label = self.model.names[cls_id]
                        color = (0, 255, 0)

                        # Filter overly large boxes
                        frame_h, frame_w = frame.shape[:2]
                        box_width = x2 - x1
                        box_height = y2 - y1
                        if box_width > frame_w * 0.9 or box_height > frame_h * 0.9:
                            continue

                        # Smooth box per class_id (could use tracker ID if available)
                        key = str(cls_id)
                        if key in self.previous_boxes:
                            px1, py1, px2, py2 = self.previous_boxes[key]
                            x1 = self.alpha * px1 + (1 - self.alpha) * x1
                            y1 = self.alpha * py1 + (1 - self.alpha) * y1
                            x2 = self.alpha * px2 + (1 - self.alpha) * x2
                            y2 = self.alpha * py2 + (1 - self.alpha) * y2

                        self.previous_boxes[key] = (x1, y1, x2, y2)

                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(frame, f"{label} {score:.2f}", (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                else:
                    # Auto-save if no detections
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(self.save_dir, f"nodetect_{timestamp}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"[⚠️] No detections, frame saved: {filename}")
                # --- Draw FPS ---
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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

    # --- Soft-NMS Function ---
    def soft_nms(self, boxes, sigma=0.5, Nt=0.4, threshold=0.3, method='gaussian'):
        N = boxes.shape[0]
        for i in range(N):
            maxscore = boxes[i, 4]
            maxpos = i
            for pos in range(i + 1, N):
                if boxes[pos, 4] > maxscore:
                    maxscore = boxes[pos, 4]
                    maxpos = pos
            boxes[[i, maxpos]] = boxes[[maxpos, i]]

            boxA = boxes[i]
            pos = i + 1
            while pos < N:
                boxB = boxes[pos]
                iou = self.compute_iou(boxA[:4], boxB[:4])
                if method == 'linear':
                    if iou > Nt:
                        boxes[pos, 4] *= (1 - iou)
                elif method == 'gaussian':
                    boxes[pos, 4] *= np.exp(-(iou ** 2) / sigma)
                else:
                    if iou > Nt:
                        boxes[pos, 4] = 0

                if boxes[pos, 4] < threshold:
                    boxes[[pos, N - 1]] = boxes[[N - 1, pos]]
                    N -= 1
                else:
                    pos += 1

        return boxes[:N]

    def compute_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

        return interArea / float(boxAArea + boxBArea - interArea)
