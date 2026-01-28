"""
Configuration validation script.
Run this to verify that all configuration files are correctly formatted
and can be loaded successfully.
"""

from config.config_loader import ConfigLoader


def validate_configs():
    """Validate all configuration files."""
    print("=" * 60)
    print("Configuration Validation")
    print("=" * 60)
    
    loader = ConfigLoader()
    
    # Validate config.yaml
    print("\n1. Validating config.yaml...")
    try:
        config = loader.load_config("config")
        print(f"   ✓ Loaded successfully")
        print(f"   - Base URL: {config.get('base_url')}")
        print(f"   - Default timeout: {config.get('default_timeout')}s")
        print(f"   - Headless: {config.get('headless')}")
        print(f"   - Retries: {config.get('retries')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Validate browsers.yaml
    print("\n2. Validating browsers.yaml...")
    try:
        browsers = loader.load_config("browsers")
        print(f"   ✓ Loaded successfully")
        browser_profiles = browsers.get('browsers', {})
        print(f"   - Available profiles: {', '.join(browser_profiles.keys())}")
        print(f"   - Default browser: {browsers.get('default_browser')}")
        
        # Test getting specific browser config
        chrome_config = loader.get_browser_config("chrome_127")
        print(f"   - Chrome 127 config: {chrome_config.get('browserName')} v{chrome_config.get('browserVersion')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Validate reporting.yaml
    print("\n3. Validating reporting.yaml...")
    try:
        reporting = loader.load_config("reporting")
        print(f"   ✓ Loaded successfully")
        print(f"   - Report type: {reporting.get('report_type')}")
        print(f"   - Output path: {reporting.get('output_path')}")
        print(f"   - Include screenshots: {reporting.get('include_screenshots')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test nested key access
    print("\n4. Testing nested key access...")
    try:
        browser_name = loader.get('browsers.chrome_127.browserName', 'browsers')
        print(f"   ✓ Nested access works")
        print(f"   - browsers.chrome_127.browserName = {browser_name}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test default value handling
    print("\n5. Testing default value handling...")
    try:
        missing_value = loader.get('non_existent_key', default='default_value')
        print(f"   ✓ Default value handling works")
        print(f"   - Got default value: {missing_value}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All configuration validations passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    validate_configs()
