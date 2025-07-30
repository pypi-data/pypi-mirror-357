import tempfile
import os
from typing import List, Dict, Union
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image


class Detector:
    def __init__(
        self,
        model_stream: bytes,
        confidence_threshold: float = 0.5,
        device: str = "cuda"
    ):
        if not isinstance(model_stream, bytes):
            raise TypeError("model_stream must be a byte stream")

        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")

        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
        elif device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.confidence_threshold = confidence_threshold
        self.device = device

        self.model = self._load_model_from_stream(model_stream)
        self.model.fuse()
        self.class_names = self._extract_class_names()

    def _load_model_from_stream(self, model_stream: bytes) -> YOLO:
        try:
            self.temp_model_file = tempfile.NamedTemporaryFile(
                suffix='.pt',
                delete=False
            )

            self.temp_model_file.write(model_stream)
            self.temp_model_file.close()

            model = YOLO(self.temp_model_file.name)

            return model

        except Exception as e:
            raise

    def _extract_class_names(self) -> List[str]:
        try:
            if hasattr(self.model.model, 'names'):
                names = self.model.model.names
                if isinstance(names, dict):
                    return [names[i] for i in sorted(names.keys())]
                elif isinstance(names, list):
                    return names

            if hasattr(self.model, 'names'):
                names = self.model.names
                if isinstance(names, dict):
                    return [names[i] for i in sorted(names.keys())]
                elif isinstance(names, list):
                    return names

            return []

        except Exception as e:
            return []

    @property
    def class_names(self) -> List[str]:
        return self._class_names

    @class_names.setter
    def class_names(self, value: List[str]):
        self._class_names = value if value else []

    def predict(self, image: Union[str, np.ndarray, Image.Image]) -> List[Dict]:
        try:
            processed_image = self._prepare_image(image)

            results = self.model.predict(
                processed_image,
                conf=self.confidence_threshold,
                device=self.device,
                verbose=False,
                save=False,
                imgsz=640,
                augment=False,
                agnostic_nms=False,
                max_det=300,
                classes=None,
                retina_masks=False,
                embed=None
            )

            detections = self._process_results(results[0])

            return detections

        except Exception as e:
            raise

    def _prepare_image(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Failed to load image: {image}")
            return img

        elif isinstance(image, Image.Image):
            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            return img_array

        elif isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                if image.shape[2] == 3:
                    return image
                elif image.shape[2] == 4:
                    return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            elif len(image.shape) == 2:
                return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            return image

        else:
            raise TypeError("Supported types: str (path), np.ndarray, PIL.Image")

    def _process_results(self, result) -> List[Dict]:
        detections = []

        if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes

            boxes_xyxy = boxes.xyxy.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()
            class_ids = boxes.cls.cpu().numpy().astype(int)

            for i in range(len(boxes)):
                bbox_xyxy = boxes_xyxy[i]
                confidence = float(confidences[i])
                class_id = int(class_ids[i])

                if confidence < self.confidence_threshold:
                    continue

                if class_id >= len(self.class_names) or class_id < 0:
                    continue

                x1, y1, x2, y2 = bbox_xyxy

                if x2 <= x1 or y2 <= y1:
                    continue

                width = x2 - x1
                height = y2 - y1

                class_name = self.class_names[class_id]

                detection = {
                    "bbox": [float(x1), float(y1), float(width), float(height)],
                    "class": class_name,
                    "score": float(confidence)
                }

                detections.append(detection)

        detections.sort(key=lambda x: x["score"], reverse=True)

        return detections

    def __del__(self):
        if hasattr(self, 'temp_model_file'):
            try:
                os.unlink(self.temp_model_file.name)
            except:
                pass