"""
Color Detection Use Case for Post-Processing Framework

This module provides color detection capabilities for objects in video streams.
It analyzes the dominant colors of detected objects and provides insights about
color distribution patterns.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import os
import cv2
import numpy as np
from collections import defaultdict

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence, 
    filter_by_categories, 
    apply_category_mapping, 
    match_results_structure,
    extract_major_colors
)


@dataclass
class ColorDetectionConfig(BaseConfig):
    """Configuration for color detection use case."""
    
    # Detection settings
    confidence_threshold: float = 0.5
    
    # Color analysis settings
    top_k_colors: int = 3
    frame_skip: int = 1
    
    # Category settings
    target_categories: Optional[List[str]] = field(default_factory=lambda: ["person", "car", "truck", "motorcycle"])
    
    # Video processing settings
    fps: Optional[float] = None
    bbox_format: str = "auto"
    
    # Category mapping
    index_to_category: Optional[Dict[int, str]] = None
    
    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    def validate(self) -> List[str]:
        """Validate configuration parameters."""
        errors = super().validate()
        
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
            
        if self.top_k_colors <= 0:
            errors.append("top_k_colors must be positive")
            
        if self.frame_skip <= 0:
            errors.append("frame_skip must be positive")
            
        if self.bbox_format not in ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"]:
            errors.append("bbox_format must be one of: auto, xmin_ymin_xmax_ymax, x_y_width_height")
            
        return errors


class ColorDetectionUseCase(BaseProcessor):
    """Color detection processor for analyzing object colors in video streams."""
    
    def __init__(self):
        super().__init__("color_detection")
        self.category = "visual_appearance"
        
    def get_config_schema(self) -> Dict[str, Any]:
        """Get JSON schema for configuration validation."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5},
                "top_k_colors": {"type": "integer", "minimum": 1, "default": 3},
                "frame_skip": {"type": "integer", "minimum": 1, "default": 1},
                "target_categories": {"type": ["array", "null"], "items": {"type": "string"}, "default": ["person", "car", "truck", "motorcycle"]},
                "fps": {"type": ["number", "null"], "minimum": 1.0, "default": None},
                "bbox_format": {"type": "string", "enum": ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"], "default": "auto"},
                "index_to_category": {"type": ["object", "null"], "default": None},
                "alert_config": {"type": ["object", "null"], "default": None}
            },
            "required": ["confidence_threshold", "top_k_colors"],
            "additionalProperties": False
        }
        
    def create_default_config(self, **overrides) -> ColorDetectionConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "top_k_colors": 3,
            "frame_skip": 1,
            "target_categories": ["person", "car", "truck", "motorcycle"],
            "fps": None,
            "bbox_format": "auto",
            "index_to_category": None,
            "alert_config": None
        }
        defaults.update(overrides)
        return ColorDetectionConfig(**defaults)
        
    def process(
        self,
        predictions: List[Dict[str, Any]], 
        config: ConfigProtocol,
        input_bytes: Optional[bytes] = None,
        context: Optional[ProcessingContext] = None
    ) -> ProcessingResult:
        """Process color detection for objects in video."""
        
        # Validate configuration
        if not isinstance(config, ColorDetectionConfig):
            return self.create_error_result("Invalid configuration type", context=context)
            
        context = context or ProcessingContext()
        
        # Validate required inputs
        if not input_bytes:
            return self.create_error_result("input_bytes (video) is required for color detection", context=context)
            
        if not predictions:
            return self.create_error_result("predictions are required for color detection", context=context)
            
        try:
            # Set up processing context
            input_format = match_results_structure(predictions)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            
            # Step 1: Apply confidence filtering
            processed_data = predictions.copy()
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.confidence_threshold)
                self.logger.debug(f"Applied confidence filtering with threshold: {config.confidence_threshold}")
                
            # Step 2: Apply category mapping
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
                
            # Step 3: Filter to target categories
            color_processed_data = processed_data
            if config.target_categories:
                color_processed_data = filter_by_categories(processed_data.copy(), config.target_categories)
                self.logger.debug(f"Applied target category filtering for: {config.target_categories}")
                
            # Step 4: Analyze colors in video
            color_analysis = self._analyze_colors_in_video(
                color_processed_data, 
                input_bytes, 
                config
            )
            
            # Step 5: Calculate summaries
            color_summary = self._calculate_color_summary(color_analysis, config)
            general_summary = self._calculate_general_summary(processed_data, config)
            
            # Step 6: Generate insights
            insights = self._generate_insights(color_summary, config)
            
            # Step 7: Check alerts
            alerts = self._check_alerts(color_summary, config)
            
            # Step 8: Calculate metrics
            metrics = self._calculate_metrics(color_analysis, color_summary, config)
            
            # Step 9: Extract predictions for output
            predictions_output = self._extract_predictions(color_analysis, config)
            
            # Create result
            result = self.create_result(
                data={
                    "color_analysis": color_analysis,
                    "color_summary": color_summary,
                    "general_summary": general_summary,
                    "predictions": predictions_output
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            
            result.insights = insights
            result.alerts = alerts
            result.metrics = metrics
            result.summary = self._generate_summary_text(color_summary, general_summary)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in color detection processing: {str(e)}")
            return self.create_error_result(f"Color detection processing failed: {str(e)}", context=context)
            
    def _analyze_colors_in_video(
        self, 
        predictions: List[Dict[str, Any]], 
        video_bytes: bytes, 
        config: ColorDetectionConfig
    ) -> List[Dict[str, Any]]:
        """Analyze colors of detected objects in video frames, ensuring uniqueness using track_id."""

        # Save video to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(video_bytes)
            video_path = temp_video.name

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Failed to open video file")

            fps = config.fps or cap.get(cv2.CAP_PROP_FPS)
            color_analysis = []
            frame_id = 0
            seen_track_ids = set()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Skip frames based on frame_skip setting
                if frame_id % config.frame_skip != 0:
                    frame_id += 1
                    continue

                frame_key = str(frame_id)
                timestamp = frame_id / fps

                # Check if we have predictions for this frame
                if frame_key not in predictions:
                    frame_id += 1
                    continue

                detections = predictions[frame_key]
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Analyze colors for each detection
                for detection in detections:
                    if detection.get("confidence", 1.0) < config.confidence_threshold:
                        continue

                    bbox = detection.get("bounding_box", detection.get("bbox"))
                    if not bbox:
                        continue

                    track_id = detection.get("track_id")
                    if track_id is None or track_id in seen_track_ids:
                        continue  # Skip if no track_id or already counted

                    seen_track_ids.add(track_id)

                    # Crop the bounding box region
                    crop = self._crop_bbox(rgb_frame, bbox, config.bbox_format)
                    if crop.size == 0:
                        continue

                    # Extract major colors
                    major_colors = extract_major_colors(crop, k=config.top_k_colors)
                    main_color = major_colors[0][0] if major_colors else "unknown"

                    color_record = {
                        "frame_id": frame_key,
                        "timestamp": round(timestamp, 2),
                        "category": detection.get("category", "unknown"),
                        "confidence": round(detection.get("confidence", 0.0), 3),
                        "main_color": main_color,
                        "major_colors": major_colors,
                        "bbox": bbox,
                        "detection_id": detection.get("id", f"det_{len(color_analysis)}"),
                        "track_id": track_id
                    }
                    color_analysis.append(color_record)

                frame_id += 1

            cap.release()
            return color_analysis

        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)


                
    def _crop_bbox(self, image: np.ndarray, bbox: Dict[str, Any], bbox_format: str) -> np.ndarray:
        """Crop bounding box region from image."""
        h, w = image.shape[:2]
        
        # Auto-detect bbox format
        if bbox_format == "auto":
            if "xmin" in bbox:
                bbox_format = "xmin_ymin_xmax_ymax"
            elif "x" in bbox:
                bbox_format = "x_y_width_height"
            else:
                return np.zeros((0, 0, 3), dtype=np.uint8)
                
        # Extract coordinates based on format
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
        
    def _calculate_color_summary(self, color_analysis: List[Dict], config: ColorDetectionConfig) -> Dict[str, Any]:
        """Calculate color distribution summary."""
        
        # Group by category and color
        category_colors = defaultdict(lambda: defaultdict(int))
        total_detections = len(color_analysis)
        
        for record in color_analysis:
            category = record["category"]
            main_color = record["main_color"]
            category_colors[category][main_color] += 1
            
        # Calculate summary statistics
        summary = {
            "total_detections": total_detections,
            "categories": dict(category_colors),
            "color_distribution": {},
            "dominant_colors": {}
        }
        
        # Calculate overall color distribution
        all_colors = defaultdict(int)
        for category_data in category_colors.values():
            for color, count in category_data.items():
                all_colors[color] += count
                
        summary["color_distribution"] = dict(all_colors)
        
        # Find dominant color per category
        for category, colors in category_colors.items():
            if colors:
                dominant_color = max(colors.items(), key=lambda x: x[1])
                summary["dominant_colors"][category] = {
                    "color": dominant_color[0],
                    "count": dominant_color[1],
                    "percentage": round((dominant_color[1] / sum(colors.values())) * 100, 1)
                }
                
        return summary
        
    def _calculate_general_summary(self, processed_data: List[Dict], config: ColorDetectionConfig) -> Dict[str, Any]:
        """Calculate general detection summary."""
        
        # Count objects by category
        category_counts = defaultdict(int)
        total_objects = 0
        
        for frame_data in processed_data.values() if isinstance(processed_data, dict) else []:
            if isinstance(frame_data, list):
                for detection in frame_data:
                    if detection.get("confidence", 1.0) >= config.confidence_threshold:
                        category = detection.get("category", "unknown")
                        category_counts[category] += 1
                        total_objects += 1
                        
        return {
            "total_objects": total_objects,
            "category_counts": dict(category_counts),
            "categories_detected": list(category_counts.keys())
        }
        
    def _generate_insights(self, color_summary: Dict, config: ColorDetectionConfig) -> List[str]:
        """Generate insights from color analysis."""
        insights = []

        total_detections = color_summary.get("total_detections", 0)
        if total_detections == 0:
            insights.append("No objects detected for color analysis.")
            return insights

        categories = color_summary.get("categories", {})
        dominant_colors = color_summary.get("dominant_colors", {})
        color_distribution = color_summary.get("color_distribution", {})

        # Per-category color insights
        for category, colors in categories.items():
            total = sum(colors.values())
            color_details = ", ".join([f"{color}: {count}" for color, count in colors.items()])
            insights.append(f"{category.capitalize()} colors: {color_details} (Total: {total})")

        # Dominant color summary per category
        for category, info in dominant_colors.items():
            insights.append(
                f"{category.capitalize()} is mostly {info['color']} "
                f"({info['count']} detections, {info['percentage']}%)"
            )

        # Color diversity insights
        unique_colors = len(color_distribution)
        if unique_colors > 1:
            insights.append(f"Detected {unique_colors} unique colors across all categories.")

        # Most common color overall
        if color_distribution:
            most_common_color = max(color_distribution.items(), key=lambda x: x[1])
            insights.append(
                f"Most common color overall: {most_common_color[0]} ({most_common_color[1]} detections)"
            )

        return insights

        
    def _check_alerts(self, color_summary: Dict, config: ColorDetectionConfig) -> List[Dict]:
        """Check for alert conditions."""
        alerts = []
        
        if not config.alert_config:
            return alerts
            
        total_detections = color_summary.get("total_detections", 0)
        
        # Count threshold alerts
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_detections >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"Total detections ({total_detections}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total_detections,
                        "threshold": threshold,
                        "timestamp": datetime.now().isoformat()
                    })
                elif category in color_summary.get("categories", {}):
                    category_total = sum(color_summary["categories"][category].values())
                    if category_total >= threshold:
                        alerts.append({
                            "type": "count_threshold",
                            "severity": "warning", 
                            "message": f"{category} detections ({category_total}) exceeds threshold ({threshold})",
                            "category": category,
                            "current_count": category_total,
                            "threshold": threshold,
                            "timestamp": datetime.now().isoformat()
                        })
                        
        return alerts
        
    def _calculate_metrics(self, color_analysis: List[Dict], color_summary: Dict, config: ColorDetectionConfig) -> Dict[str, Any]:
        """Calculate detailed metrics."""
        
        return {
            "total_detections": len(color_analysis),
            "unique_colors": len(color_summary.get("color_distribution", {})),
            "categories_analyzed": len(color_summary.get("categories", {})),
            "average_colors_per_detection": config.top_k_colors,
            "processing_settings": {
                "confidence_threshold": config.confidence_threshold,
                "top_k_colors": config.top_k_colors,
                "frame_skip": config.frame_skip,
                "target_categories": config.target_categories
            }
        }
        
    def _extract_predictions(self, color_analysis: List[Dict], config: ColorDetectionConfig) -> List[Dict]:
        """Extract predictions in standard format."""
        
        predictions = []
        for record in color_analysis:
            prediction = {
                "category": record["category"],
                "confidence": record["confidence"],
                "bbox": record["bbox"],
                "frame_id": record["frame_id"],
                "timestamp": record["timestamp"],
                "main_color": record["main_color"],
                "major_colors": record["major_colors"]
            }
            if "detection_id" in record:
                prediction["id"] = record["detection_id"]
            predictions.append(prediction)
            
        return predictions
        
    def _generate_summary_text(self, color_summary: Dict, general_summary: Dict) -> str:
        """Generate human-readable summary text with per-category color breakdown."""

        total_detections = color_summary.get("total_detections", 0)
        color_distribution = color_summary.get("color_distribution", {})
        categories = color_summary.get("categories", {})

        if total_detections == 0:
            return "No objects detected for color analysis."

        lines = [
            f"Processed {total_detections} total object detections across {len(categories)} categories.",
            f"Identified {len(color_distribution)} unique colors in total."
        ]

        # Add per-category breakdown
        for category, colors in categories.items():
            total = sum(colors.values())
            color_details = ", ".join([f"{color} ({count})" for color, count in colors.items()])
            lines.append(f"{category.capitalize()}: {total} detections → {color_details}")

        return " ".join(lines)
