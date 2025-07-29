"""
Use case implementations for post-processing.

This module contains all available use case processors for different
post-processing scenarios.
"""

from .people_counting import PeopleCountingUseCase
from .customer_service import CustomerServiceUseCase
from .advanced_customer_service import AdvancedCustomerServiceUseCase
from .basic_counting_tracking import BasicCountingTrackingUseCase
from .license_plate_detection import LicensePlateUseCase
from .color_mapper import VideoColorClassificationUseCase
from .ppe_compliance import PPEComplianceUseCase

__all__ = [
    'PeopleCountingUseCase',
    'CustomerServiceUseCase',
    'AdvancedCustomerServiceUseCase',
    'BasicCountingTrackingUseCase',
    'LicensePlateUseCase',
    'VideoColorClassificationUseCase',
    'PPEComplianceUseCase'
]