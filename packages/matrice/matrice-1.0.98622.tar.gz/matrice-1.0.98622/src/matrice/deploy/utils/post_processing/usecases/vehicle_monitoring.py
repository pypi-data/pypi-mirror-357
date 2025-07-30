from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

from ..core.base import (
    BaseProcessor,
    ProcessingContext,
    ProcessingResult,
    ConfigProtocol,
    ResultFormat,
)
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    count_objects_by_category,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure,
)


@dataclass
class VehicleMonitoringConfig(BaseConfig):
    """Configuration for vehicle monitoring use case."""

    # Detection settings
    confidence_threshold: float = 0.5

    # Vehicle categories
    vehicle_categories: List[str] = field(
        default_factory=lambda: ["bus", "microbus", "car", "motorbike", "pickup van", "truck"]
    )

    target_vehicle_categories: List[str] = field(
        default_factory=lambda: ["bus", "car", "motorbike", "truck"]
    )

    # Tracking and analytics settings
    enable_tracking: bool = False
    enable_unique_counting: bool = True
    time_window_minutes: int = 60

    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {
            0: "bus",
            1: "microbus",
            2: "car",
            3: "motorbike",
            4: "pickup van",
            5: "truck",
        }
    )

    # Zone configuration
    zone_config: Optional[Dict] = None

    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        if self.time_window_minutes < 1:
            raise ValueError("time_window_minutes must be at least 1")


class VehicleMonitoringUseCase(BaseProcessor):
    """Vehicle monitoring use case with counting, zone analysis, and analytics."""

    def __init__(self):
        """Initialize vehicle monitoring use case."""
        super().__init__("vehicle_monitoring")
        self.category = "traffic"

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for vehicle monitoring."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for vehicle detections",
                },
                "enable_tracking": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable tracking for unique vehicle counting",
                },
                "enable_unique_counting": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable unique vehicle counting using tracking",
                },
                "time_window_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 60,
                    "description": "Time window for vehicle counting analysis in minutes",
                },
                "vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["bus", "microbus", "car", "motorbike", "pickup van", "truck"],
                    "description": "Category names that represent vehicles",
                },
                "target_vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["bus", "car", "motorbike", "truck"],
                    "description": "Category names for vehicles of interest",
                },
                "index_to_category": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from category indices to names",
                },
                "zone_config": {
                    "type": "object",
                    "properties": {
                        "zones": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                                "minItems": 3,
                            },
                            "description": "Zone definitions as polygons for traffic monitoring",
                        },
                        "zone_confidence_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "description": "Per-zone confidence thresholds",
                        },
                    },
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for vehicle alerts",
                        },
                        "occupancy_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Zone occupancy thresholds for vehicle alerts",
                        },
                    },
                },
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False,
        }

    def create_default_config(self, **overrides) -> VehicleMonitoringConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "enable_tracking": False,
            "enable_unique_counting": True,
            "time_window_minutes": 60,
            "vehicle_categories": ["bus", "microbus", "car", "motorbike", "pickup van", "truck"],
            "target_vehicle_categories": ["bus", "car", "motorbike", "truck"],
        }
        defaults.update(overrides)
        return VehicleMonitoringConfig(**defaults)

    def process(
        self,
        data: Any,
        config: ConfigProtocol,
        context: Optional[ProcessingContext] = None,
    ) -> ProcessingResult:
        """
        Process vehicle monitoring use case.
        """
        start_time = time.time()

        try:
            if not isinstance(config, VehicleMonitoringConfig):
                return self.create_error_result(
                    "Invalid configuration type for vehicle monitoring",
                    usecase=self.name,
                    category=self.category,
                    context=context,
                )

            if context is None:
                context = ProcessingContext()

            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold

            self.logger.info(
                f"Processing vehicle monitoring with format: {input_format.value}"
            )

            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(
                    processed_data, config.confidence_threshold
                )
                self.logger.debug(
                    f"Applied confidence filtering with threshold {config.confidence_threshold}"
                )

            if config.index_to_category:
                processed_data = apply_category_mapping(
                    processed_data, config.index_to_category
                )
                self.logger.debug("Applied category mapping")

            vehicle_processed_data = processed_data
            if config.vehicle_categories:
                vehicle_processed_data = filter_by_categories(
                    processed_data.copy(), config.vehicle_categories
                )
                self.logger.debug(
                    f"Applied vehicle category filtering for: {config.vehicle_categories}"
                )

            zones = config.zone_config.get("zones") if config.zone_config else None
            vehicle_counting_summary = calculate_counting_summary(
                vehicle_processed_data, zones=zones
            )
            general_counting_summary = calculate_counting_summary(processed_data, zones=zones)

            zone_analysis = {}
            if config.zone_config and config.zone_config.get("zones"):
                zone_analysis = count_objects_in_zones(
                    vehicle_processed_data, config.zone_config.get("zones")
                )
                self.logger.debug(f"Analyzed {len(config.zone_config.get('zones', []))} zones")

            insights = self._generate_insights(vehicle_counting_summary, zone_analysis, config)
            alerts = self._check_alerts(vehicle_counting_summary, zone_analysis, config)
            metrics = self._calculate_metrics(
                vehicle_counting_summary, zone_analysis, config, context
            )
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(vehicle_counting_summary, zone_analysis, alerts)

            context.mark_completed()

            result = self.create_result(
                data={
                    "general_counting_summary": general_counting_summary,
                    "counting_summary": vehicle_counting_summary,
                    "zone_analysis": zone_analysis,
                    "alerts": alerts,
                    "total_vehicles": vehicle_counting_summary.get("total_objects", 0),
                    "zones_count": len(config.zone_config.get("zones", [])) if config.zone_config else 0,
                },
                usecase=self.name,
                category=self.category,
                context=context,
            )

            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics

            if config.confidence_threshold and config.confidence_threshold < 0.3:
                result.add_warning(
                    f"Low confidence threshold ({config.confidence_threshold}) may result in false positives"
                )

            processing_time = context.processing_time or time.time() - start_time
            self.logger.info(f"Vehicle monitoring completed successfully in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Vehicle monitoring failed: {str(e)}", exc_info=True)
            if context:
                context.mark_completed()
            return self.create_error_result(
                str(e),
                error_type=type(e).__name__,
                usecase=self.name,
                category=self.category,
                context=context,
            )

    def _generate_insights(
        self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig
    ) -> List[str]:
        """Generate human-readable insights from vehicle counting results."""
        insights = []

        total_vehicles = counting_summary.get("total_objects", 0)

        if total_vehicles == 0:
            insights.append("EVENT: No vehicles detected in the scene")
            return insights

        insights.append(
            f"EVENT: Detected {total_vehicles} vehicle{'s' if total_vehicles != 1 else ''} in the scene"
        )

        intensity_threshold = None
        if (
            config.alert_config
            and config.alert_config.count_thresholds
            and "all" in config.alert_config.count_thresholds
        ):
            intensity_threshold = config.alert_config.count_thresholds["all"]

        if intensity_threshold is not None:
            percentage = (total_vehicles / intensity_threshold) * 100
            if percentage < 20:
                insights.append(
                    f"INTENSITY: Low traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 50:
                insights.append(
                    f"INTENSITY: Moderate traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 70:
                insights.append(
                    f"INTENSITY: High traffic volume ({percentage:.1f}% of expected capacity)"
                )
            else:
                insights.append(
                    f"INTENSITY: Very high traffic density ({percentage:.1f}% of expected capacity)"
                )
        else:
            if total_vehicles > 15:
                insights.append(
                    f"INTENSITY: High traffic density with {total_vehicles} vehicles detected"
                )
            elif total_vehicles == 1:
                insights.append("INTENSITY: Light traffic conditions")

        if zone_analysis:
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                if zone_total > 0:
                    percentage = (zone_total / total_vehicles) * 100 if total_vehicles > 0 else 0
                    insights.append(
                        f"Zone '{zone_name}': {zone_total} vehicle{'s' if zone_total != 1 else ''} ({percentage:.1f}% of total)"
                    )
                    if zone_total > 10:
                        insights.append(
                            f"⚠️ High traffic density in zone '{zone_name}' with {zone_total} vehicles"
                        )
                    elif zone_total == 1:
                        insights.append(f"Low traffic in zone '{zone_name}'")

        if "by_category" in counting_summary:
            category_counts = counting_summary["by_category"]
            for category, count in category_counts.items():
                if count > 0 and category.lower() in [
                    cat.lower() for cat in config.vehicle_categories
                ]:
                    percentage = (count / total_vehicles) * 100 if total_vehicles > 0 else 0
                    insights.append(
                        f"VEHICLES: {category}: {count} detected ({percentage:.1f}% of total vehicles)"
                    )

        if config.time_window_minutes:
            rate_per_hour = (total_vehicles / config.time_window_minutes) * 60
            insights.append(f"Traffic rate: {rate_per_hour:.1f} vehicles per hour")

        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                insights.append(f"Unique vehicle count: {unique_count}")
                if unique_count != total_vehicles:
                    insights.append(f"Detection efficiency: {unique_count}/{total_vehicles} unique tracks")

        return insights

    def _check_alerts(
        self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig
    ) -> List[Dict]:
        """Check for alert conditions and generate alerts."""
        alerts = []

        if not config.alert_config:
            return alerts

        total_vehicles = counting_summary.get("total_objects", 0)

        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_vehicles >= threshold:
                    alerts.append(
                        {
                            "type": "count_threshold",
                            "severity": "warning",
                            "message": f"Total vehicle count ({total_vehicles}) exceeds threshold ({threshold})",
                            "category": category,
                            "current_count": total_vehicles,
                            "threshold": threshold,
                        }
                    )
                elif category in counting_summary.get("by_category", {}):
                    count = counting_summary["by_category"][category]
                    if count >= threshold:
                        alerts.append(
                            {
                                "type": "count_threshold",
                                "severity": "warning",
                                "message": f"{category} count ({count}) exceeds threshold ({threshold})",
                                "category": category,
                                "current_count": count,
                                "threshold": threshold,
                            }
                        )

        if config.alert_config.occupancy_thresholds:
            for zone_name, threshold in config.alert_config.occupancy_thresholds.items():
                if zone_name in zone_analysis:
                    zone_count = (
                        sum(zone_analysis[zone_name].values())
                        if isinstance(zone_analysis[zone_name], dict)
                        else zone_analysis[zone_name]
                    )
                    if zone_count >= threshold:
                        alerts.append(
                            {
                                "type": "occupancy_threshold",
                                "severity": "warning",
                                "message": f"Zone '{zone_name}' vehicle occupancy ({zone_count}) exceeds threshold ({threshold})",
                                "zone": zone_name,
                                "current_occupancy": zone_count,
                                "threshold": threshold,
                            }
                        )

        return alerts

    def _calculate_metrics(
        self,
        counting_summary: Dict,
        zone_analysis: Dict,
        config: VehicleMonitoringConfig,
        context: ProcessingContext,
    ) -> Dict[str, Any]:
        """Calculate detailed metrics for analytics."""
        total_vehicles = counting_summary.get("total_objects", 0)

        metrics = {
            "total_vehicles": total_vehicles,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "zones_analyzed": len(zone_analysis),
            "detection_rate": 0.0,
            "coverage_percentage": 0.0,
        }

        if config.time_window_minutes and config.time_window_minutes > 0:
            metrics["detection_rate"] = (total_vehicles / config.time_window_minutes) * 60

        if zone_analysis and total_vehicles > 0:
            vehicles_in_zones = sum(
                sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                for zone_counts in zone_analysis.values()
            )
            metrics["coverage_percentage"] = (vehicles_in_zones / total_vehicles) * 100

        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                metrics["unique_vehicles"] = unique_count
                metrics["tracking_efficiency"] = (
                    (unique_count / total_vehicles) * 100 if total_vehicles > 0 else 0
                )

        if zone_analysis:
            zone_metrics = {}
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = (
                    sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                )
                zone_metrics[zone_name] = {
                    "count": zone_total,
                    "percentage": (zone_total / total_vehicles) * 100 if total_vehicles > 0 else 0,
                }
            metrics["zone_metrics"] = zone_metrics

        return metrics

    def _extract_predictions(self, data: Any) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []

        try:
            if isinstance(data, list):
                for item in data:
                    prediction = self._normalize_prediction(item)
                    if prediction:
                        predictions.append(prediction)
            elif isinstance(data, dict):
                for frame_id, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            prediction = self._normalize_prediction(item)
                            if prediction:
                                prediction["frame_id"] = frame_id
                                predictions.append(prediction)

        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")

        return predictions

    def _normalize_prediction(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single prediction item."""
        if not isinstance(item, dict):
            return {}

        return {
            "category": item.get("category", item.get("class", "unknown")),
            "confidence": item.get("confidence", item.get("score", 0.0)),
            "bounding_box": item.get("bounding_box", item.get("bbox", {})),
            "track_id": item.get("track_id"),
        }

    def _get_detections_with_confidence(self, counting_summary: Dict) -> List[Dict]:
        """Extract detection items with confidence scores."""
        return counting_summary.get("detections", [])

    def _count_unique_tracks(self, counting_summary: Dict) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        detections = self._get_detections_with_confidence(counting_summary)

        if not detections:
            return None

        unique_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                unique_tracks.add(track_id)

        return len(unique_tracks) if unique_tracks else None

    def _generate_summary(
        self, counting_summary: Dict, zone_analysis: Dict, alerts: List
    ) -> str:
        """Generate human-readable summary."""
        total_vehicles = counting_summary.get("total_objects", 0)

        if total_vehicles == 0:
            return "No vehicles detected in the scene"

        summary_parts = [
            f"{total_vehicles} vehicle{'s' if total_vehicles != 1 else ''} detected"
        ]

        if zone_analysis:
            zones_with_vehicles = sum(
                1
                for zone_counts in zone_analysis.values()
                if (sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts) > 0
            )
            summary_parts.append(f"across {zones_with_vehicles}/{len(zone_analysis)} zones")

        if alerts:
            alert_count = len(alerts)
            summary_parts.append(f"with {alert_count} alert{'s' if alert_count != 1 else ''}")

        return ", ".join(summary_parts)