from ultralytics import YOLO
import cv2
import time

class Detector:

    def __init__(self, model_path:str, confidence_thres:float):

        self.model = YOLO(model_path)
        self.confidence_thres = confidence_thres
        self.start_time = 0
        self.prev_time = 0
        print(self.model.names)
    
    def detect(self, frame, conf, classes, verbose=False):
        
        self.start_time = time.time()
        results = self.model(frame, conf=conf, classes=classes, verbose=verbose)[0]
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

        
        cv2.putText(annotated_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        cv2.putText(annotated_frame, entity_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(annotated_frame, conf_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        return frame 
