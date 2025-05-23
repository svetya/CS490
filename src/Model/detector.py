from ultralytics import YOLO
import cv2
import time
import numpy as np

class Detector:

    def __init__(self, model_path:str, confidence_thres:float):

        self.model = YOLO(model_path)
        self.confidence_thres = confidence_thres
        self.start_time = 0
        self.prev_time = 0
        self.alpha = 0.6
        self.previous_boxes = {}  # For smoothing
        print(self.model.names)
    
    def detect(self, frame, conf, classes, verbose=False):
        
        self.start_time = time.time()
        results = self.model.track(frame, conf=conf, classes=classes, verbose=verbose, tracker="bytetrack.yaml")[0]
        annotated_frame = results.plot()

        instances = len(results.boxes)

        if instances > 0:
            avg_conf = results.boxes.conf.mean().item()
            conf_text = f"AvgConf: {avg_conf:.2f}"
        else:
            conf_text = "AvgConf: N/A"

        fps = 1/(self.start_time-self.prev_time)
        self.prev_time = self.start_time
        fps = int(fps)
        fps_text = "FPS: " + str(fps)
        entity_text = f"E: {instances}"

        frame_h, frame_w = frame.shape[:2]

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            score = float(box.conf)
            cls_id = int(box.cls)

            # Clip overly large boxes
            box_width = x2 - x1
            box_height = y2 - y1
            if box_width > frame_w * 0.9 or box_height > frame_h * 0.9:
                continue

            # Smooth boxes
            key = str(cls_id)
            if key in self.previous_boxes:
                px1, py1, px2, py2 = self.previous_boxes[key]
                x1 = self.alpha * px1 + (1 - self.alpha) * x1
                y1 = self.alpha * py1 + (1 - self.alpha) * y1
                x2 = self.alpha * px2 + (1 - self.alpha) * x2
                y2 = self.alpha * py2 + (1 - self.alpha) * y2

            self.previous_boxes[key] = (x1, y1, x2, y2)

            label = self.model.names[cls_id]
            color = (0, 255, 0)
        
        cv2.putText(annotated_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        cv2.putText(annotated_frame, entity_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(annotated_frame, conf_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        return frame 
