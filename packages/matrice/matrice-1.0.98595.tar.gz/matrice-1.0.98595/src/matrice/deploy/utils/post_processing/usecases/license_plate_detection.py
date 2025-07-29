"""
License plate detection use case implementation.

This module provides a clean implementation of license plate detection functionality
with counting, insights generation, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    apply_category_mapping,
    calculate_counting_summary,
    match_results_structure
)


@dataclass
class LicensePlateConfig(BaseConfig):
    """Configuration for license plate detection use case."""
    
    # Detection settings
    confidence_threshold: float = 0.5
    
    # Category settings
    license_plate_categories: List[str] = field(default_factory=lambda: ["License_Plate", "license_plate"])
    target_vehicle_categories: List[str] = field(default_factory=lambda: ["cars", "car", "vehicle", "motorcycle", "truck"])
    
    # Alert configuration
    alert_config: Optional[AlertConfig] = None
    
    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {
        0: 'License_Plate',
        1: 'cars',
        2: 'motorcycle', 
        3: 'truck'
    })
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")


class LicensePlateUseCase(BaseProcessor):
    """License plate detection use case with counting and analytics."""
    
    def __init__(self):
        """Initialize license plate detection use case."""
        super().__init__("license_plate_detection")
        self.category = "vehicle"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for license plate detection."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for detections"
                },

                "license_plate_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["License_Plate", "license_plate"],
                    "description": "Category names that represent license plates"
                },
                "target_vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["cars", "car", "vehicle", "motorcycle", "truck"],
                    "description": "Category names for vehicles of interest"
                },
                "index_to_category": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from category indices to names"
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for alerts"
                        }
                    }
                }
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False
        }
    
    def create_default_config(self, **overrides) -> LicensePlateConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "license_plate_categories": ["License_Plate", "license_plate"],
            "target_vehicle_categories": ["cars", "car", "vehicle", "motorcycle", "truck"],
        }
        defaults.update(overrides)
        return LicensePlateConfig(**defaults)
    
    def process(self, data: Any, config: ConfigProtocol, 
                context: Optional[ProcessingContext] = None) -> ProcessingResult:
        '''
        Process license plate detection use case.
        '''
        start_time = time.time()
        
        try:
            if not isinstance(config, LicensePlateConfig):
                return self.create_error_result(
                    "Invalid configuration type for license plate detection",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            
            if context is None:
                context = ProcessingContext()
            
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            
            self.logger.info(f"Processing license plate detection with format: {input_format.value}")
            
            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.confidence_threshold)
                self.logger.debug(f"Applied confidence filtering with threshold {config.confidence_threshold}")
            
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
            
            license_counting_summary = self._calculate_license_plate_summary(processed_data, config)
            general_counting_summary = calculate_counting_summary(processed_data)
            
            insights = self._generate_insights(license_counting_summary, general_counting_summary, config)
            alerts = self._check_alerts(license_counting_summary, config)
            metrics = self._calculate_metrics(license_counting_summary, general_counting_summary, config, context)
            predictions = self._extract_predictions(processed_data, config)
            summary = self._generate_summary(license_counting_summary, general_counting_summary, alerts)
            
            context.mark_completed()
            
            result = self.create_result(
                data={
                    "license_plate_summary": license_counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_license_plates": license_counting_summary.get("total_objects", 0),
                    "total_vehicles": general_counting_summary.get("total_objects", 0)
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in license plate processing: {str(e)}")
            return self.create_error_result(
                f"License plate processing failed: {str(e)}",
                error_type="LicensePlateProcessingError",
                usecase=self.name,
                category=self.category,
                context=context
            )
    
    def _calculate_license_plate_summary(self, data: Any, config: LicensePlateConfig) -> Dict[str, Any]:
        '''Calculate summary for license plates only.'''
        if isinstance(data, list):
            license_detections = [
                det for det in data 
                if det.get("category", "").lower() in [cat.lower() for cat in config.license_plate_categories]
            ]
            
            return {
                "total_objects": len(license_detections),
                "by_category": {"License_Plate": len(license_detections)},
                "detections": license_detections
            }
        return {"total_objects": 0, "by_category": {}, "detections": []}
    
    def _generate_insights(self, license_summary: Dict, general_summary: Dict, 
                          config: LicensePlateConfig) -> List[str]:
        '''Generate human-readable insights from detection results.'''
        insights = []
        
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = general_summary.get("total_objects", 0)
        
        if total_plates == 0:
            insights.append("EVENT: No license plates detected in the scene")
            if total_vehicles > 0:
                insights.append(f"ANALYSIS: {total_vehicles} vehicles detected but no readable license plates")
        else:
            insights.append(f"EVENT: Detected {total_plates} license plate{'s' if total_plates != 1 else ''}")
            
            if total_vehicles > 0:
                detection_rate = (total_plates / total_vehicles) * 100
                insights.append(f"DETECTION_RATE: {detection_rate:.1f}% license plate visibility ({total_plates}/{total_vehicles} vehicles)")
                
                if detection_rate < 50:
                    insights.append("QUALITY: Low license plate visibility - consider improving camera angle or resolution")
                elif detection_rate > 80:
                    insights.append("QUALITY: Excellent license plate visibility")
        
        intensity_threshold = None
        if (config.alert_config and 
            config.alert_config.count_thresholds and 
            "license_plate" in config.alert_config.count_thresholds):
            intensity_threshold = config.alert_config.count_thresholds["license_plate"]
        elif (config.alert_config and 
              config.alert_config.count_thresholds and 
              "all" in config.alert_config.count_thresholds):
            intensity_threshold = config.alert_config.count_thresholds["all"]
        
        if intensity_threshold is not None:
            percentage = (total_plates / intensity_threshold) * 100
            
            if percentage < 20:
                insights.append(f"INTENSITY: Low traffic volume ({percentage:.1f}% of expected capacity)")
            elif percentage <= 50:
                insights.append(f"INTENSITY: Moderate traffic volume ({percentage:.1f}% of expected capacity)")
            elif percentage <= 70:
                insights.append(f"INTENSITY:  High traffic volume ({percentage:.1f}% of expected capacity)")
            else:
                insights.append(f"INTENSITY:  Very high traffic density ({percentage:.1f}% of expected capacity)")
        else:
            if total_plates > 10:
                insights.append(f"INTENSITY:  High traffic density with {total_plates} license plates detected")
            elif total_plates == 1:
                insights.append("INTENSITY: Light traffic conditions")
        
        if "by_category" in general_summary:
            category_counts = general_summary["by_category"]
            for category, count in category_counts.items():
                if count > 0 and category.lower() in [cat.lower() for cat in config.target_vehicle_categories]:
                    percentage = (count / total_vehicles) * 100 if total_vehicles > 0 else 0
                    insights.append(f"VEHICLES: {category}: {count} detected ({percentage:.1f}% of total vehicles)")
        
        return insights
    
    def _check_alerts(self, license_summary: Dict, config: LicensePlateConfig) -> List[Dict]:
        '''Check for alert conditions and generate alerts.'''
        alerts = []
        
        if not config.alert_config:
            return alerts
        
        total_plates = license_summary.get("total_objects", 0)
        
        # Count threshold alerts
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category in ["license_plate", "all"] and total_plates >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"License plate count ({total_plates}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total_plates,
                        "threshold": threshold
                    })
        
        return alerts
    
    def _calculate_metrics(self, license_summary: Dict, general_summary: Dict, 
                          config: LicensePlateConfig, context: ProcessingContext) -> Dict[str, Any]:
        '''Calculate detailed metrics for analytics.'''
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = general_summary.get("total_objects", 0)
        
        metrics = {
            "total_license_plates": total_plates,
            "total_vehicles": total_vehicles,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "detection_rate_percentage": 0.0,
            "license_plate_visibility": "unknown"
        }
        
        if total_vehicles > 0:
            detection_rate = (total_plates / total_vehicles) * 100
            metrics["detection_rate_percentage"] = detection_rate
            
            if detection_rate < 30:
                metrics["license_plate_visibility"] = "poor"
            elif detection_rate < 60:
                metrics["license_plate_visibility"] = "fair" 
            elif detection_rate < 85:
                metrics["license_plate_visibility"] = "good"
            else:
                metrics["license_plate_visibility"] = "excellent"
        
        return metrics
    
    def _extract_predictions(self, data: Any, config: LicensePlateConfig) -> List[Dict[str, Any]]:
        '''Extract predictions from processed data for API compatibility.'''
        predictions = []
        
        try:
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        prediction = {
                            "category": item.get("category", item.get("class", "unknown")),
                            "confidence": item.get("confidence", item.get("score", 0.0)),
                            "bounding_box": item.get("bounding_box", item.get("bbox", {}))
                        }
                        predictions.append(prediction)
        
        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")
        
        return predictions
    
    def _generate_summary(self, license_summary: Dict, general_summary: Dict, alerts: List) -> str:
        '''Generate human-readable summary.'''
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = general_summary.get("total_objects", 0)
        
        if total_plates == 0 and total_vehicles == 0:
            return "No vehicles or license plates detected"
        
        summary_parts = []
        
        if total_plates > 0:
            summary_parts.append(f"{total_plates} license plate{'s' if total_plates != 1 else ''} detected")
        
        if total_vehicles > 0:
            summary_parts.append(f"{total_vehicles} vehicle{'s' if total_vehicles != 1 else ''} detected")
        
        if alerts:
            alert_count = len(alerts)
            summary_parts.append(f"{alert_count} alert{'s' if alert_count != 1 else ''}")
        
        return ", ".join(summary_parts)
