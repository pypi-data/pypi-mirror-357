from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import os
import json
import cv2
import numpy as np
from collections import defaultdict

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ResultFormat, ConfigProtocol
from ..core.config import BaseConfig
from ..utils import filter_by_confidence, filter_by_categories, apply_category_mapping, match_results_structure
from .color_map_utils import extract_major_colors


@dataclass
class VideoColorConfig(BaseConfig):
    top_k_colors: int = 3
    min_confidence: float = 0.5
    fps: Optional[float] = None
    frame_skip: int = 1
    target_categories: Optional[List[str]] = None
    bbox_format: str = "auto"
    index_to_category: Optional[Dict[int, str]] = None

    def validate(self) -> List[str]:
        errors = super().validate()

        if self.top_k_colors <= 0:
            errors.append("top_k_colors must be positive")

        if self.frame_skip <= 0:
            errors.append("frame_skip must be positive")

        if self.bbox_format not in ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"]:
            errors.append("bbox_format is invalid")

        return errors



class VideoColorClassificationUseCase(BaseProcessor):
    def __init__(self):
        super().__init__("video_color_classification")
        self.category = "visual_appearance"

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "top_k_colors": {"type": "integer", "minimum": 1, "default": 3},
                "min_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
                "fps": {"type": ["number", "null"], "minimum": 1.0, "default": None},
                "frame_skip": {"type": "integer", "minimum": 1, "default": 1},
                "target_categories": {"type": ["array", "null"], "items": {"type": "string"}, "default": None},
                "bbox_format": {"type": "string", "enum": ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"], "default": "auto"},
                "index_to_category": {"type": ["object", "null"], "default": None}  # Add schema for new field
            },
            "required": ["top_k_colors", "min_confidence"],
            "additionalProperties": False
        }

    def create_default_config(self, **overrides) -> VideoColorConfig:
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "top_k_colors": 3,
            "min_confidence": 0.5,
            "fps": None,
            "frame_skip": 1,
            "target_categories": None,
            "bbox_format": "auto",
            "index_to_category": None  # Add default value
        }
        defaults.update(overrides)
        return VideoColorConfig(**defaults)

    def process(self, predictions: List[Dict[str, Any]], config: ConfigProtocol, input_bytes: Optional[bytes] = None,
                context: Optional[ProcessingContext] = None) -> ProcessingResult:
        if not isinstance(config, VideoColorConfig):
            return self.create_error_result("Invalid configuration type", context=context)

        context = context or ProcessingContext()

        if not input_bytes or not predictions:
            return self.create_error_result("Missing required input (input_bytes or predictions)", context=context)

        input_format = match_results_structure(predictions)
        context.input_format = input_format
        context.confidence_threshold = config.min_confidence

        if config.min_confidence is not None:
            predictions = filter_by_confidence(predictions, config.min_confidence)

        if config.index_to_category:
            predictions = apply_category_mapping(predictions, config.index_to_category)

        if config.target_categories:
            predictions = filter_by_categories(predictions, config.target_categories)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(input_bytes)
            video_path = temp_video.name

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Failed to open video")

            fps = config.fps or cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            detailed_results = []
            summary_results: Dict[str, Dict[str, List[float]]] = {}
            frame_id = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_id % config.frame_skip != 0:
                    frame_id += 1
                    continue

                frame_key = str(frame_id)
                timestamp = frame_id / fps
                if frame_key not in predictions:
                    frame_id += 1
                    continue

                detections = predictions[frame_key]
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                for det in detections:
                    if det.get("confidence", 1.0) < config.min_confidence:
                        continue
                    bbox = det.get("bounding_box", det.get("bbox"))
                    if not bbox:
                        continue
                    crop = self._crop_bbox(rgb_frame, bbox, config.bbox_format)
                    if crop.size == 0:
                        continue
                    major_colors = extract_major_colors(crop, k=config.top_k_colors)
                    main_color = major_colors[0][0] if major_colors else "unknown"
                    record = {
                        "frame_id": frame_key,
                        "timestamp": round(timestamp, 2),
                        "category": det.get("category", "unknown"),
                        "confidence": round(det.get("confidence", 0.0), 3),
                        "main_color": main_color,
                        "major_colors": major_colors,
                        "bbox": bbox
                    }
                    detailed_results.append(record)
                    cat = record["category"]
                    summary_results.setdefault(cat, {})
                    summary_results[cat].setdefault(main_color, []).append(timestamp)

                frame_id += 1
            cap.release()

            insights = self._generate_insights(summary_results)
            metrics = self._calculate_metrics(detailed_results, summary_results)
            summary = self._generate_summary(detailed_results, summary_results)

            result = self.create_result(
                data={
                    "detailed_results": detailed_results,
                    "summary_results": summary_results
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            result.insights = insights
            result.metrics = metrics
            result.summary = summary
            return result

        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    def _crop_bbox(self, image: np.ndarray, bbox: Dict[str, Any], bbox_format: str) -> np.ndarray:
        h, w = image.shape[:2]
        if bbox_format == "auto":
            if "xmin" in bbox:
                bbox_format = "xmin_ymin_xmax_ymax"
            elif "x" in bbox:
                bbox_format = "x_y_width_height"
            else:
                return np.zeros((0, 0, 3), dtype=np.uint8)

        if bbox_format == "xmin_ymin_xmax_ymax":
            xmin = max(0, int(bbox["xmin"]))
            ymin = max(0, int(bbox["ymin"]))
            xmax = min(w, int(bbox["xmax"]))
            ymax = min(h, int(bbox["ymax"]))
        elif bbox_format == "x_y_width_height":
            xmin = max(0, int(bbox["x"]))
            ymin = max(0, int(bbox["y"]))
            xmax = min(w, int(bbox["x"] + bbox["width"]))
            ymax = min(h, int(bbox["y"] + bbox["height"]))
        else:
            return np.zeros((0, 0, 3), dtype=np.uint8)

        return image[ymin:ymax, xmin:xmax]

    def _generate_insights(self, summary: Dict[str, Dict[str, List[float]]]) -> List[str]:
        insights = []
        for cat, color_map in summary.items():
            total = sum(len(v) for v in color_map.values())
            if not total:
                continue
            top_color = max(color_map.items(), key=lambda kv: len(kv[1]))[0]
            insights.append(f"{cat} objects are predominantly {top_color} ({len(color_map[top_color])} occurrences)")
        return insights

    def _generate_summary(self, detailed: List[Dict], summary: Dict[str, Dict[str, List[float]]]) -> str:
        total = len(detailed)
        if total == 0:
            return "No valid detections found."
        return f"Processed {total} detections across {len(summary)} categories."

    def _calculate_metrics(self, detailed: List[Dict], summary: Dict[str, Dict[str, List[float]]]) -> Dict[str, Any]:
        return {
            "total_detections": len(detailed),
            "categories": list(summary.keys()),
            "color_variants": sum(len(v) for v in summary.values())
        }