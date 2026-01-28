"""
Data-Driven Testing Data Loader Module

Provides unified loading of test data from external files (YAML, JSON, CSV).
Normalizes all formats to List[Dict[str, Any]] for pytest parametrization.

Usage:
    from utils.data_loader import load_test_data
    
    # Load from YAML, JSON, or CSV - all return List[Dict]
    test_cases = load_test_data("test_data/login.yaml")
    
    @pytest.mark.parametrize("data", test_cases)
    def test_login(driver, data):
        page = LoginPage(driver)
        page.login(data["username"], data["password"])
        assert page.is_logged_in()
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml
from loguru import logger


class DataLoaderError(Exception):
    """Raised when data loading or parsing fails."""
    pass


class DataLoader:
    """
    Unified loader for test data from YAML, JSON, or CSV files.
    
    Always normalizes output to List[Dict[str, Any]] for consistency.
    Supports root keys in YAML/JSON (e.g., 'tests') for flexible file structure.
    """
    
    SUPPORTED_FORMATS = {".yaml", ".yml", ".json", ".csv"}
    
    @staticmethod
    def load(path: str) -> List[Dict[str, Any]]:
        """
        Load test data from file. Auto-detects format by extension.
        
        Args:
            path: Path to data file (relative or absolute).
                  Supported formats: .yaml, .yml, .json, .csv
        
        Returns:
            List[Dict[str, Any]]: Normalized test data.
                                  Always a list of dicts.
        
        Raises:
            DataLoaderError: If file not found, unsupported format,
                           invalid content, or empty dataset.
        
        Examples:
            # YAML with root key
            data = DataLoader.load("test_data/login.yaml")
            # Content: tests: [{username: user1, password: pass1}, ...]
            
            # JSON array
            data = DataLoader.load("test_data/search.json")
            # Content: [{query: laptop}, {query: phone}]
            
            # CSV
            data = DataLoader.load("test_data/users.csv")
            # Headers become dict keys
        """
        file_path = Path(path)
        
        # Validate file exists
        if not file_path.exists():
            raise DataLoaderError(
                f"Data file not found: {file_path.absolute()}"
            )
        
        # Detect format
        suffix = file_path.suffix.lower()
        if suffix not in DataLoader.SUPPORTED_FORMATS:
            raise DataLoaderError(
                f"Unsupported file format: {suffix}. "
                f"Supported: {DataLoader.SUPPORTED_FORMATS}"
            )
        
        logger.debug(f"Loading test data from: {file_path}")
        
        try:
            if suffix in {".yaml", ".yml"}:
                data = DataLoader._load_yaml(file_path)
            elif suffix == ".json":
                data = DataLoader._load_json(file_path)
            elif suffix == ".csv":
                data = DataLoader._load_csv(file_path)
        except DataLoaderError:
            raise
        except Exception as e:
            raise DataLoaderError(
                f"Error loading {suffix} file {file_path.name}: {str(e)}"
            )
        
        # Validate result
        if not data:
            raise DataLoaderError(
                f"Empty dataset in {file_path.name}. "
                f"Expected non-empty list of test cases."
            )
        
        if not isinstance(data, list):
            raise DataLoaderError(
                f"Invalid data structure in {file_path.name}. "
                f"Expected list of dicts, got {type(data).__name__}"
            )
        
        logger.info(
            f"Successfully loaded {len(data)} test case(s) "
            f"from {file_path.name}"
        )
        return data
    
    @staticmethod
    def _load_yaml(path: Path) -> List[Dict[str, Any]]:
        """
        Load YAML file.
        
        Supports:
        - Direct list: [{ ... }, { ... }]
        - Root key: tests: [{ ... }, { ... }]
        
        Args:
            path: Path to YAML file
        
        Returns:
            List[Dict[str, Any]]
        
        Raises:
            DataLoaderError: If format is invalid
        """
        with open(path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
        
        if content is None:
            raise DataLoaderError("YAML file is empty")
        
        # Handle list directly
        if isinstance(content, list):
            return content
        
        # Handle dict with root key (common pattern: tests, data, cases)
        if isinstance(content, dict):
            # Try common root keys
            for key in ["tests", "data", "cases", "test_cases", "rows"]:
                if key in content:
                    value = content[key]
                    if isinstance(value, list):
                        return value
            
            # If no known root key but dict present, treat as single test case
            logger.warning(
                f"No recognized root key in YAML {path.name}. "
                f"Treating entire dict as single test case."
            )
            return [content]
        
        raise DataLoaderError(
            f"Invalid YAML structure in {path.name}. "
            f"Expected list or dict, got {type(content).__name__}"
        )
    
    @staticmethod
    def _load_json(path: Path) -> List[Dict[str, Any]]:
        """
        Load JSON file.
        
        Supports:
        - Direct list: [{ ... }, { ... }]
        - Root key: { "tests": [{ ... }, { ... }] }
        
        Args:
            path: Path to JSON file
        
        Returns:
            List[Dict[str, Any]]
        
        Raises:
            DataLoaderError: If format is invalid
        """
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        # Handle list directly
        if isinstance(content, list):
            return content
        
        # Handle dict with root key
        if isinstance(content, dict):
            # Try common root keys
            for key in ["tests", "data", "cases", "test_cases", "rows"]:
                if key in content:
                    value = content[key]
                    if isinstance(value, list):
                        return value
            
            # If no known root key but dict present, treat as single test case
            logger.warning(
                f"No recognized root key in JSON {path.name}. "
                f"Treating entire dict as single test case."
            )
            return [content]
        
        raise DataLoaderError(
            f"Invalid JSON structure in {path.name}. "
            f"Expected list or dict, got {type(content).__name__}"
        )
    
    @staticmethod
    def _load_csv(path: Path) -> List[Dict[str, Any]]:
        """
        Load CSV file.
        
        First row is treated as headers.
        Each subsequent row becomes a dict with headers as keys.
        
        Args:
            path: Path to CSV file
        
        Returns:
            List[Dict[str, Any]]
        
        Raises:
            DataLoaderError: If format is invalid or no header row
        """
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames is None:
                raise DataLoaderError(
                    f"CSV file {path.name} has no header row"
                )
            
            rows = list(reader)
        
        if not rows:
            raise DataLoaderError(
                f"CSV file {path.name} has no data rows (only headers)"
            )
        
        return rows


def load_test_data(path: str) -> List[Dict[str, Any]]:
    """
    Load test data from external file (YAML, JSON, or CSV).
    
    Public API for data-driven testing. Auto-detects file format by extension.
    Always returns a list of dicts suitable for pytest parametrization.
    
    Args:
        path: Path to data file.
              Relative paths are resolved from project root.
              Supported formats: .yaml, .yml, .json, .csv
    
    Returns:
        List[Dict[str, Any]]: Test data ready for parametrization.
    
    Raises:
        DataLoaderError: On file not found, invalid format,
                        invalid content, or empty dataset.
    
    Examples:
        >>> # In pytest test
        >>> @pytest.mark.parametrize(
        ...     "user_data",
        ...     load_test_data("test_data/users.yaml")
        ... )
        ... def test_login(driver, user_data):
        ...     page = LoginPage(driver)
        ...     page.login(user_data["username"], user_data["password"])
        ...     assert page.is_logged_in()
    """
    # Resolve relative paths from project root
    file_path = Path(path)
    if not file_path.is_absolute():
        # Try current directory first, then project root
        if not file_path.exists():
            project_root = Path(__file__).parent.parent
            file_path = project_root / path
    
    return DataLoader.load(str(file_path))
