"""
Configuration Loader Module
Provides centralized configuration management for the automation framework.
Loads and manages YAML configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from loguru import logger


class ConfigLoader:
    """
    Configuration loader class for managing YAML configuration files.
    
    This class provides methods to load and access configuration values
    from YAML files with graceful error handling and default value support.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the ConfigLoader.
        
        Args:
            config_dir: Path to the configuration directory. 
                       Defaults to 'config' folder in project root.
        """
        if config_dir is None:
            # Get project root (parent of config directory)
            project_root = Path(__file__).parent.parent
            self.config_dir = project_root / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # Cache for loaded configurations
        self._config_cache: Dict[str, Dict] = {}
        
        logger.info(f"ConfigLoader initialized with config directory: {self.config_dir}")
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML file and return its contents as a dictionary.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing the YAML file contents
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file is invalid
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            logger.error(f"Configuration file not found: {file_path}")
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                logger.debug(f"Successfully loaded configuration from: {filename}")
                return config_data if config_data is not None else {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {e}")
            raise
    
    def load_config(self, config_name: str = "config") -> Dict[str, Any]:
        """
        Load a configuration file by name.
        
        Args:
            config_name: Name of the config file without extension
                        (e.g., 'config', 'browsers', 'reporting')
            
        Returns:
            Dictionary containing the configuration data
        """
        # Check cache first
        if config_name in self._config_cache:
            logger.debug(f"Returning cached configuration: {config_name}")
            return self._config_cache[config_name]
        
        # Load from file
        filename = f"{config_name}.yaml"
        config_data = self._load_yaml_file(filename)
        
        # Cache the loaded configuration
        self._config_cache[config_name] = config_data
        logger.info(f"Configuration '{config_name}' loaded and cached")
        
        return config_data
    
    def get(self, key: str, config_name: str = "config", 
            default: Any = None) -> Any:
        """
        Get a configuration value by key with optional default.
        
        Supports nested keys using dot notation (e.g., 'browsers.chrome_127.browserName')
        
        Args:
            key: Configuration key to retrieve (supports dot notation for nested keys)
            config_name: Name of the configuration file to search in
            default: Default value to return if key is not found
            
        Returns:
            The configuration value or default if not found
            
        Example:
            >>> config_loader = ConfigLoader()
            >>> base_url = config_loader.get('base_url', default='http://localhost')
            >>> browser = config_loader.get('browsers.chrome_127', 'browsers')
        """
        try:
            config_data = self.load_config(config_name)
            
            # Handle nested keys using dot notation
            if '.' in key:
                keys = key.split('.')
                value = config_data
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        logger.warning(
                            f"Key '{key}' not found in {config_name}.yaml, "
                            f"returning default: {default}"
                        )
                        return default
                return value
            else:
                # Simple key lookup
                value = config_data.get(key, default)
                if value == default and key not in config_data:
                    logger.warning(
                        f"Key '{key}' not found in {config_name}.yaml, "
                        f"returning default: {default}"
                    )
                return value
                
        except Exception as e:
            logger.error(
                f"Error getting key '{key}' from {config_name}: {e}, "
                f"returning default: {default}"
            )
            return default
    
    def get_all(self, config_name: str = "config") -> Dict[str, Any]:
        """
        Get all configuration values from a config file.
        
        Args:
            config_name: Name of the configuration file
            
        Returns:
            Complete configuration dictionary
        """
        return self.load_config(config_name)
    
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """
        Force reload a configuration file, bypassing the cache.
        
        Args:
            config_name: Name of the configuration to reload
            
        Returns:
            Reloaded configuration dictionary
        """
        if config_name in self._config_cache:
            logger.info(f"Clearing cache for configuration: {config_name}")
            del self._config_cache[config_name]
        
        return self.load_config(config_name)
    
    def clear_cache(self) -> None:
        """Clear all cached configurations."""
        self._config_cache.clear()
        logger.info("Configuration cache cleared")
    
    def get_browser_config(self, browser_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific browser profile.
        
        Args:
            browser_name: Name of the browser profile (e.g., 'chrome_127')
            
        Returns:
            Browser configuration dictionary
            
        Raises:
            ValueError: If browser profile is not found
        """
        browsers = self.load_config("browsers")
        
        if "browsers" not in browsers:
            logger.error("'browsers' key not found in browsers.yaml")
            raise ValueError("Invalid browsers configuration structure")
        
        browser_profiles = browsers["browsers"]
        
        if browser_name not in browser_profiles:
            available = ", ".join(browser_profiles.keys())
            logger.error(
                f"Browser profile '{browser_name}' not found. "
                f"Available profiles: {available}"
            )
            raise ValueError(
                f"Browser profile '{browser_name}' not found. "
                f"Available: {available}"
            )
        
        logger.debug(f"Retrieved browser configuration for: {browser_name}")
        return browser_profiles[browser_name]
    
    def get_default_browser(self) -> str:
        """
        Get the default browser profile name.
        
        Returns:
            Name of the default browser profile
        """
        return self.get("default_browser", "browsers", default="chrome_127")
    
    def get_browser_matrix(self) -> list[Dict[str, Any]]:
        """
        Get the browser matrix configuration.
        
        Returns:
            List of browser profile dictionaries from the matrix section
            
        Raises:
            ValueError: If matrix is not properly configured
        """
        try:
            browsers_config = self.load_config("browsers")
            
            # Check if matrix section exists
            if "matrix" not in browsers_config:
                logger.warning(
                    "No 'matrix' section found in browsers.yaml. "
                    "Falling back to legacy browsers section."
                )
                # Fallback: return list of legacy browser profiles
                return self._get_legacy_browser_matrix(browsers_config)
            
            matrix = browsers_config["matrix"]
            
            if not isinstance(matrix, list) or len(matrix) == 0:
                logger.error("Browser matrix must be a non-empty list")
                raise ValueError("Browser matrix must be a non-empty list")
            
            logger.info(f"Loaded browser matrix with {len(matrix)} profiles")
            return matrix
        
        except Exception as e:
            logger.error(f"Failed to load browser matrix: {e}")
            raise
    
    def _get_legacy_browser_matrix(self, browsers_config: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Convert legacy browsers section to matrix format for backward compatibility.
        
        Args:
            browsers_config: The loaded browsers configuration
            
        Returns:
            List of browser profiles in matrix format
            
        Raises:
            ValueError: If browsers section is not properly configured
        """
        if "browsers" not in browsers_config:
            logger.error(
                "'matrix' not found and 'browsers' section is also missing "
                "from browsers.yaml"
            )
            raise ValueError("Invalid browsers configuration: missing both 'matrix' and 'browsers'")
        
        browser_profiles = browsers_config["browsers"]
        if not isinstance(browser_profiles, dict) or len(browser_profiles) == 0:
            logger.error("Legacy 'browsers' section must be a non-empty dictionary")
            raise ValueError("Invalid legacy browsers configuration")
        
        # Convert dict of profiles to list format for backward compatibility
        matrix = []
        for profile_name, profile_config in browser_profiles.items():
            profile_entry = {"name": profile_name}
            profile_entry.update(profile_config)
            matrix.append(profile_entry)
        
        logger.info(
            f"Converted {len(matrix)} legacy browser profiles to matrix format"
        )
        return matrix


# Singleton instance for global access
_config_loader_instance: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """
    Get or create the singleton ConfigLoader instance.
    
    Returns:
        ConfigLoader instance
    """
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader()
    return _config_loader_instance
