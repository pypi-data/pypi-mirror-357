"""
PPE compliance detection use case implementation.

This module provides a clean implementation of PPE compliance detection functionality
with counting, insights generation, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    calculate_counting_summary,
    match_results_structure,
    apply_category_mapping
)


@dataclass
class PPEComplianceConfig(BaseConfig):
    """Configuration for PPE compliance detection use case."""
    # Detection settings
    no_hardhat_threshold: float = 0.8
    violation_categories: List[str] = field(default_factory=lambda: [
        "NO-Hardhat", "NO-Safety Vest", "NO-Mask"
    ])
    alert_config: Optional[AlertConfig] = None
    
    # Time window configuration
    time_window_minutes: int = 60
    enable_unique_counting: bool = True
    
    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {
        0: 'NO-Hardhat',
        1: 'NO-Safety Vest',
        2: 'NO-Mask'
    })

    def __post_init__(self):
        if not (0.0 <= self.no_hardhat_threshold <= 1.0):
            raise ValueError("no_hardhat_threshold must be between 0.0 and 1.0")


class PPEComplianceUseCase(BaseProcessor):
    """PPE compliance detection use case with counting and analytics."""
    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "no_hardhat_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.8,
                    "description": "Confidence threshold for NO-Hardhat violations"
                },
                "violation_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["NO-Hardhat", "NO-Safety Vest", "NO-Mask"],
                    "description": "Category names for PPE violations"
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
            "required": ["no_hardhat_threshold"],
            "additionalProperties": False
        }

    def create_default_config(self, **overrides) -> PPEComplianceConfig:
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "no_hardhat_threshold": 0.8,
            "violation_categories": ["NO-Hardhat", "NO-Safety Vest", "NO-Mask"],
            "index_to_category": {0: 'NO-Hardhat', 1: 'NO-Safety Vest', 2: 'NO-Mask'},
        }
        defaults.update(overrides)
        return PPEComplianceConfig(**defaults)

    def process(self, data: Any, config: ConfigProtocol,
                context: Optional[ProcessingContext] = None) -> ProcessingResult:
        start_time = time.time()
        try:
            if not isinstance(config, PPEComplianceConfig):
                return self.create_error_result(
                    "Invalid configuration type for PPE compliance detection",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            if context is None:
                context = ProcessingContext()
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.no_hardhat_threshold = config.no_hardhat_threshold
            self.logger.info(f"Processing PPE compliance detection with format: {input_format.value}")
            processed_data = data
            # Apply category mapping if present
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
            # Apply filter_by_confidence if threshold is set (like in license_plate_detection)
            if config.no_hardhat_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.no_hardhat_threshold)
                self.logger.debug(f"Applied confidence filtering with threshold {config.no_hardhat_threshold}")
            # Now filter for PPE violations
            processed_data = self._filter_ppe_violations(processed_data, config)
            # General counting summary (all detections, not just violations)
            general_counting_summary = calculate_counting_summary(data)
            # PPE violation summary (custom)
            counting_summary = self._count_categories(processed_data, config)
            insights = self._generate_insights(counting_summary, config)
            alerts = self._check_alerts(counting_summary, config)
            metrics = self._calculate_metrics(counting_summary, context, config)
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(counting_summary, alerts)
            
            # Step 9: Generate structured events and tracking stats
            events = self._generate_events(counting_summary, alerts, config)
            tracking_stats = self._generate_tracking_stats(counting_summary, insights, summary, config)
            
            context.mark_completed()
            result = self.create_result(
                data={
                    "ppe_violation_summary": counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_violations": counting_summary.get("total_count", 0),
                    "events": events,
                    "tracking_stats": tracking_stats
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
            self.logger.error(f"Error in PPE compliance processing: {str(e)}")
            return self.create_error_result(
                f"PPE compliance processing failed: {str(e)}",
                error_type="PPEComplianceProcessingError",
                usecase=self.name,
                category=self.category,
                context=context
            )

    def _filter_ppe_violations(self, detections: list, config: PPEComplianceConfig) -> list:
        filtered = []
        for det in detections:
            cat = det.get('category')
            conf = det.get('confidence', 1.0)
            if cat == 'NO-Hardhat' and conf < config.no_hardhat_threshold:
                continue
            if cat in config.violation_categories:
                filtered.append(det)
        return filtered

    def _count_categories(self, detections: list, config: PPEComplianceConfig) -> dict:
        counts = {}
        for det in detections:
            cat = det.get('category', 'unknown')
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [
                {
                    'bounding_box': det.get('bounding_box'),
                    'category': det.get('category')
                } for det in detections
            ]
        }

    def _generate_insights(self, summary: dict, config: PPEComplianceConfig) -> List[str]:
        insights = []
        total = summary.get("total_count", 0)
        per_cat = summary.get("per_category_count", {})
        if total == 0:
            insights.append("EVENT: No PPE violations detected.")
        else:
            insights.append(f"EVENT: {total} PPE violation(s) detected.")
            for cat, count in per_cat.items():
                insights.append(f"CATEGORY: {cat}: {count} violation(s)")
        return insights

    def _check_alerts(self, summary: dict, config: PPEComplianceConfig) -> List[Dict]:
        alerts = []
        if not config.alert_config:
            return alerts
        total = summary.get("total_count", 0)
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"PPE violation count ({total}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total,
                        "threshold": threshold
                    })
        return alerts

    def _calculate_metrics(self, summary: dict, context: ProcessingContext, config: PPEComplianceConfig) -> Dict[str, Any]:
        metrics = {
            "total_violations": summary.get("total_count", 0),
            "processing_time": context.processing_time or 0.0,
            "input_format": getattr(context.input_format, 'value', None),
            "no_hardhat_threshold": config.no_hardhat_threshold
        }
        return metrics

    def _extract_predictions(self, detections: list) -> List[Dict[str, Any]]:
        predictions = []
        for det in detections:
            predictions.append({
                "category": det.get("category", "unknown"),
                "confidence": det.get("confidence", 0.0),
                "bounding_box": det.get("bounding_box", {})
            })
        return predictions

    def _generate_summary(self, summary: dict, alerts: List) -> str:
        total = summary.get("total_count", 0)
        if total == 0:
            return "No PPE violations detected."
        parts = [f"{total} PPE violation(s) detected"]
        if alerts:
            parts.append(f"{len(alerts)} alert(s)")
        return ", ".join(parts)

    def _generate_events(self, counting_summary: Dict, alerts: List, config: PPEComplianceConfig) -> List[Dict]:
        """Generate structured events for the output format."""
        from datetime import datetime, timezone
        
        events = []
        total_violations = counting_summary.get("total_count", 0)
        
        if total_violations > 0:
            # Determine event level based on thresholds
            level = "info"
            intensity = 5.0
            
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 5)
                intensity = min(10.0, (total_violations / threshold) * 10)
                
                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
                else:
                    level = "info"
            else:
                if total_violations > 10:
                    level = "critical"
                    intensity = 9.0
                elif total_violations > 5:
                    level = "warning" 
                    intensity = 7.0
                else:
                    level = "info"
                    intensity = min(10.0, total_violations / 1.0)
            
            # Main PPE compliance event
            event = {
                "type": "ppe_compliance_violation",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "PPE Compliance Monitoring System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: PPE Compliance Violation\nLevel: {level.title()}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')}\nViolations: {total_violations} detected\nIntensity: {intensity:.1f}/10"
            }
            events.append(event)
        
        # Add category-specific events for each violation type
        per_category = counting_summary.get("per_category_count", {})
        for category, count in per_category.items():
            if count > 0:
                category_intensity = min(10.0, count / 3.0)  # Adjusted for PPE violations
                category_level = "info"
                if category_intensity >= 7:
                    category_level = "critical"
                elif category_intensity >= 5:
                    category_level = "warning"
                
                category_event = {
                    "type": "ppe_category_violation",
                    "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                    "level": category_level,
                    "intensity": round(category_intensity, 1),
                    "config": {
                        "min_value": 0,
                        "max_value": 10,
                        "level_settings": {"info": 2, "warning": 5, "critical": 7}
                    },
                    "application_name": "PPE Category Monitoring System",
                    "application_version": "1.2",
                    "location_info": category,
                    "human_text": f"Event: PPE Category Violation\nLevel: {category_level.title()}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')}\nCategory: {category}\nCount: {count} violations"
                }
                events.append(category_event)
        
        # Add alert events
        for alert in alerts:
            alert_event = {
                "type": alert.get("type", "ppe_alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "PPE Alert System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: {alert.get('type', 'PPE Alert').title()}\nLevel: {alert.get('severity', 'warning').title()}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')}\nMessage: {alert.get('message', 'PPE compliance alert triggered')}"
            }
            events.append(alert_event)
        
        return events
    
    def _generate_tracking_stats(self, counting_summary: Dict, insights: List[str], summary: str, config: PPEComplianceConfig) -> List[Dict]:
        """Generate structured tracking stats for the output format."""
        from datetime import datetime, timezone
        
        tracking_stats = []
        total_violations = counting_summary.get("total_count", 0)
        
        if total_violations > 0:
            # Create main tracking stats entry
            tracking_stat = {
                "tracking_start_time": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "all_results_for_tracking": {
                    "total_violations": total_violations,
                    "violation_summary": counting_summary,
                    "violation_rate": (total_violations / config.time_window_minutes * 60) if config.time_window_minutes else 0,
                    "per_category_violations": counting_summary.get("per_category_count", {}),
                    "unique_count": self._count_unique_tracks(counting_summary)
                },
                "human_text": self._generate_human_text_for_tracking(total_violations, counting_summary, insights, summary, config)
            }
            tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, total_violations: int, counting_summary: Dict, insights: List[str], summary: str, config: PPEComplianceConfig) -> str:
        """Generate human-readable text for tracking stats."""
        from datetime import datetime, timezone
        
        text_parts = [
            f"Tracking Start Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            f"PPE Violations Detected: {total_violations}"
        ]
        
        if config.time_window_minutes:
            violation_rate_per_hour = (total_violations / config.time_window_minutes) * 60
            text_parts.append(f"Violation Rate: {violation_rate_per_hour:.1f} violations per hour")
        
        # Add per-category breakdown
        per_category = counting_summary.get("per_category_count", {})
        if per_category:
            text_parts.append("Violation Breakdown:")
            for category, count in per_category.items():
                text_parts.append(f"  {category}: {count} violations")
        
        # Add compliance status assessment
        if total_violations > 10:
            text_parts.append("Compliance Status: Critical - Multiple PPE violations detected")
        elif total_violations > 5:
            text_parts.append("Compliance Status: Warning - Several PPE violations detected")
        elif total_violations > 0:
            text_parts.append("Compliance Status: Caution - PPE violations detected")
        else:
            text_parts.append("Compliance Status: Good - No PPE violations detected")
        
        # Add safety assessment
        if "NO-Hardhat" in per_category and per_category["NO-Hardhat"] > 0:
            text_parts.append("Safety Risk: Head protection violations detected")
        if "NO-Safety Vest" in per_category and per_category["NO-Safety Vest"] > 0:
            text_parts.append("Safety Risk: Visibility violations detected")
        if "NO-Mask" in per_category and per_category["NO-Mask"] > 0:
            text_parts.append("Safety Risk: Respiratory protection violations detected")
        
        # Add key insights
        if insights:
            text_parts.append("Key Safety Insights:")
            for insight in insights[:3]:  # Limit to first 3 insights
                text_parts.append(f"  - {insight}")
        
        return "\n".join(text_parts)
    
    def _count_unique_tracks(self, counting_summary: Dict) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        detections = counting_summary.get("detections", [])
        
        if not detections:
            return None
        
        # Count unique track IDs
        unique_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                unique_tracks.add(track_id)
        
        return len(unique_tracks) if unique_tracks else None
