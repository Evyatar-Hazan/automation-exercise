"""
Configuration package for the automation framework.
Provides centralized configuration management.
"""

from config.config_loader import ConfigLoader, get_config_loader

__all__ = ['ConfigLoader', 'get_config_loader']
