# Configuration Layer

This directory contains the configuration layer for the automation framework. All configuration is managed through YAML files and accessed via the `ConfigLoader` class.

## Files

### config.yaml
General framework configuration including:
- Application URLs (base_url, grid_url)
- Timeouts (default, page_load, element)
- Retry settings
- Browser dimensions
- Logging configuration
- Test execution settings

### browsers.yaml
Browser profiles for test execution:
- **chrome_127**: Chrome/Chromium v127 on Linux
- **chrome_latest**: Latest Chrome/Chromium on Linux
- **firefox_latest**: Latest Firefox on Linux
- **firefox_esr**: Firefox ESR v115 on Linux
- **edge_latest**: Latest Edge on Windows
- **webkit_latest**: Latest WebKit on macOS

Each profile includes browser name, version, platform, viewport size, and browser-specific arguments/preferences.

### reporting.yaml
Test reporting configuration:
- Report types (Allure, HTML, JUnit)
- Output paths for different report types
- Screenshot settings (format, quality, attachment)
- Video recording options
- Trace collection settings
- Performance metrics thresholds
- Environment information for reports

## Usage

### Basic Usage

```python
from config.config_loader import ConfigLoader

# Initialize the loader
loader = ConfigLoader()

# Get values from config.yaml (default)
base_url = loader.get('base_url')
timeout = loader.get('default_timeout')

# Get values from other config files
report_type = loader.get('report_type', config_name='reporting')
```

### Working with Browser Configurations

```python
from config.config_loader import ConfigLoader

loader = ConfigLoader()

# Get specific browser configuration
chrome_config = loader.get_browser_config('chrome_127')
print(chrome_config['browserName'])  # 'chromium'
print(chrome_config['browserVersion'])  # '127.0'

# Get default browser
default_browser = loader.get_default_browser()  # 'chrome_127'
```

### Nested Key Access

```python
# Use dot notation for nested keys
browser_name = loader.get('browsers.chrome_127.browserName', 'browsers')
viewport_width = loader.get('browsers.firefox_latest.viewport.width', 'browsers')
```

### Default Values

```python
# Provide default value if key doesn't exist
timeout = loader.get('missing_key', default=10)
```

### Getting All Configuration

```python
# Get entire configuration as dictionary
all_config = loader.get_all('config')
all_browsers = loader.get_all('browsers')
all_reporting = loader.get_all('reporting')
```

### Singleton Pattern

```python
# Use singleton for global access
from config import get_config_loader

loader = get_config_loader()
base_url = loader.get('base_url')
```

## ConfigLoader Features

- **YAML Loading**: Parses and loads YAML configuration files
- **Caching**: Caches loaded configurations for performance
- **Error Handling**: Graceful handling of missing files and keys
- **Default Values**: Supports default values for missing keys
- **Nested Access**: Dot notation for accessing nested configuration values
- **Type Safety**: Returns proper Python types (dict, list, str, int, bool)
- **Logging**: Comprehensive logging using loguru
- **Singleton Support**: Global instance available via `get_config_loader()`

## Configuration Validation

To validate all configuration files:

```bash
python validate_config.py
```

This script checks:
- YAML syntax validity
- Required keys presence
- Data type correctness
- Nested key access functionality
- Default value handling

## Best Practices

1. **Don't hardcode values**: Always use ConfigLoader to access configuration
2. **Use defaults**: Provide sensible defaults when getting configuration values
3. **Environment-specific configs**: Consider using different YAML files for different environments
4. **Type checking**: Validate configuration value types in your code
5. **Documentation**: Keep this README updated when adding new configuration options

## Future Enhancements

- Environment variable substitution in YAML files
- Configuration schema validation
- Multiple environment support (dev, staging, prod)
- Encrypted configuration values for secrets
- Dynamic configuration reload
