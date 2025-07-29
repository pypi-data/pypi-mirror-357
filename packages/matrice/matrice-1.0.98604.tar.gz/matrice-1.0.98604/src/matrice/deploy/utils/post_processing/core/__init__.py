"""
Core components for the post-processing system.

This package contains the fundamental building blocks for post-processing operations:
- Base classes and interfaces
- Configuration management system
"""

# Base classes and interfaces
from .base import (
    ProcessingResult,
    ProcessingContext,
    ProcessingStatus,
    ResultFormat,
    BaseProcessor,
    BaseUseCase,
    ProcessorRegistry,
    registry,
    ConfigProtocol
)

# Configuration system
from .config import (
    BaseConfig,
    PeopleCountingConfig,
    CustomerServiceConfig,
    ZoneConfig,
    TrackingConfig,
    AlertConfig,
    ConfigManager,
    config_manager,
    ConfigValidationError
)

__all__ = [
    # Base classes and interfaces
    'ProcessingResult',
    'ProcessingContext', 
    'ProcessingStatus',
    'ResultFormat',
    'BaseProcessor',
    'BaseUseCase',
    'ProcessorRegistry',
    'registry',
    'ConfigProtocol',
    
    # Configuration system
    'BaseConfig',
    'PeopleCountingConfig',
    'CustomerServiceConfig',
    'ZoneConfig',
    'TrackingConfig',
    'AlertConfig',
    'ConfigManager',
    'config_manager',
    'ConfigValidationError'
] 