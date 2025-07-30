import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union
import torch
from ultralytics import YOLO
import cv2
import numpy as np
from sklearn.model_selection import train_test_split


class Trainer:
    def __init__(
            self,
            model_version: str = "s",
            epochs: int = 20,
            batch_size: int = 8,
            learning_rate: float = 1e-4,
            image_size: Tuple[int, int] = (640, 640),
            use_augmentation: bool = True,
            device: str = "cuda"
    ):
        if model_version not in ["n", "s", "m", "l", "x"]:
            raise ValueError("model_version must be one of: 'n', 's', 'm', 'l', 'x'")

        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
        elif device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model_version = model_version
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.image_size = image_size
        self.use_augmentation = use_augmentation
        self.device = device

        self.model = None
        self.dataset_path = None
        self.class_names = []
        self.temp_dir = None

    def load_dataset(
            self,
            images_dir: str,
            annotations_json: str,
            format: str = "coco"
    ) -> None:
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Images directory not found: {images_dir}")

        if not os.path.exists(annotations_json):
            raise FileNotFoundError(f"Annotations file not found: {annotations_json}")

        self.temp_dir = tempfile.mkdtemp()
        yolo_dataset_path = Path(self.temp_dir) / "dataset"

        if format.lower() == "coco":
            self._convert_coco_to_yolo(images_dir, annotations_json, yolo_dataset_path)
        elif format.lower() == "yolo":
            self._prepare_yolo_dataset(images_dir, annotations_json, yolo_dataset_path)
        else:
            raise ValueError("Supported formats: 'coco', 'yolo'")

        self.dataset_path = yolo_dataset_path

    def _convert_coco_to_yolo(self, images_dir: str, annotations_json: str, output_path: Path) -> None:
        with open(annotations_json, 'r', encoding='utf-8') as f:
            coco_data = json.load(f)

        categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
        self.class_names = [categories[i] for i in sorted(categories.keys())]

        print(f"Found classes: {self.class_names}")

        (output_path / "images" / "train").mkdir(parents=True, exist_ok=True)
        (output_path / "labels" / "train").mkdir(parents=True, exist_ok=True)

        annotations_by_image = {}
        for ann in coco_data['annotations']:
            img_id = ann['image_id']
            if img_id not in annotations_by_image:
                annotations_by_image[img_id] = []
            annotations_by_image[img_id].append(ann)

        for img_info in coco_data['images']:
            img_id = img_info['id']
            img_filename = img_info['file_name']

            src_img_path = Path(images_dir) / img_filename
            if not src_img_path.exists():
                continue

            dst_img_path = output_path / "images" / "train" / img_filename
            shutil.copy2(src_img_path, dst_img_path)

            yolo_annotations = []
            if img_id in annotations_by_image:
                img_width = img_info['width']
                img_height = img_info['height']

                for ann in annotations_by_image[img_id]:
                    bbox = ann['bbox']
                    category_id = ann['category_id']

                    x_center = (bbox[0] + bbox[2] / 2) / img_width
                    y_center = (bbox[1] + bbox[3] / 2) / img_height
                    width = bbox[2] / img_width
                    height = bbox[3] / img_height

                    if category_id in categories:
                        sorted_cat_ids = sorted(categories.keys())
                        class_idx = sorted_cat_ids.index(category_id)

                        yolo_annotations.append(f"{class_idx} {x_center} {y_center} {width} {height}")

            label_filename = Path(img_filename).stem + ".txt"
            label_path = output_path / "labels" / "train" / label_filename

            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_annotations))

        data_yaml = {
            'path': str(output_path),
            'train': 'images/train',
            'val': 'images/train',
            'nc': len(self.class_names),
            'names': self.class_names
        }

        with open(output_path / "data.yaml", 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(data_yaml, f, default_flow_style=False, allow_unicode=True)

        print(f"Created data.yaml with {len(self.class_names)} classes: {self.class_names}")

    def _prepare_yolo_dataset(self, images_dir: str, labels_dir: str, output_path: Path) -> None:
        raise NotImplementedError("YOLO format is not directly supported yet")

    def train(self) -> None:
        if self.dataset_path is None:
            raise ValueError("Load dataset first using load_dataset()")

        model_name = f"yolov8{self.model_version}.pt"
        self.model = YOLO(model_name)

        train_args = {
            'data': str(self.dataset_path / "data.yaml"),
            'epochs': self.epochs,
            'batch': self.batch_size,
            'lr0': self.learning_rate,
            'imgsz': self.image_size[0],
            'device': self.device,
            'augment': self.use_augmentation,
            'verbose': False,
            'save': True,
            'project': 'runs/detect',
            'name': f'game_detection_{self.model_version}',
            'workers': 0
        }

        try:
            results = self.model.train(**train_args)
            return results
        except Exception as e:
            raise

    def evaluate(self) -> dict:
        if self.model is None:
            raise ValueError("Model is not trained. Call train() first")

        try:
            metrics = self.model.val(data=str(self.dataset_path / "data.yaml"))

            results = {
                'mAP50': float(metrics.box.map50),
                'mAP50-95': float(metrics.box.map),
                'precision': float(metrics.box.mp),
                'recall': float(metrics.box.mr)
            }

            return results

        except Exception as e:
            raise

    def save_model(self, output_path: Optional[str] = None) -> bytes:
        if self.model is None:
            raise ValueError("Model is not trained. Call train() first")

        try:
            best_model_path = Path("runs/detect")

            run_dirs = sorted([d for d in best_model_path.iterdir()
                              if d.is_dir() and f"game_detection_{self.model_version}" in d.name])

            if not run_dirs:
                raise FileNotFoundError("Training results directory not found")

            latest_run = run_dirs[-1]
            model_path = latest_run / "weights" / "best.pt"

            if not model_path.exists():
                model_path = latest_run / "weights" / "last.pt"

            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found in {latest_run / 'weights'}")

            print(f"Found model: {model_path}")

            with open(model_path, 'rb') as f:
                model_bytes = f.read()

            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(model_bytes)
                print(f"Model saved to: {output_path}")

            return model_bytes

        except Exception as e:
            print(f"Error saving model: {e}")
            raise

    def __del__(self):
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass