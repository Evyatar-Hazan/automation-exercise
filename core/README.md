# Core Layer

This directory contains the core framework components for driver management and test execution.

## Components

### DriverFactory (`driver_factory.py`)

The `DriverFactory` class is responsible for creating and managing Playwright browser instances with support for:

- **Local Browser Execution**: Launch browsers on the local machine
- **Remote Execution**: Connect to Selenium Grid / Moon (placeholder for future implementation)
- **Browser Configuration**: Load browser profiles from `config/browsers.yaml`
- **Retry Mechanism**: Automatically retry driver creation on failure
- **Isolated Sessions**: Each test gets its own browser instance
- **Timeout Configuration**: Apply default timeouts from `config/config.yaml`
- **Comprehensive Logging**: Track driver lifecycle events

#### Key Features

```python
# Supported browser types
- chromium (Chrome, Edge)
- firefox
- webkit (Safari)

# Configuration sources
- browsers.yaml: Browser profiles and capabilities
- config.yaml: Framework-level settings and timeouts

# Launch options
- Headless/headed mode
- Browser arguments
- Viewport size
- User agent, locale, timezone
- Permissions
```

#### Usage Example

```python
from core.driver_factory import DriverFactory

# Create factory with specific browser
factory = DriverFactory(browser_name='chrome_127', remote=False)

# Get driver with retry mechanism
driver = factory.get_driver(max_retries=3)

# Use driver
driver.goto("https://example.com")
print(driver.title())

# Clean up
factory.quit_driver()
```

### BaseTest (`base_test.py`)

The `BaseTest` class provides a foundation for all test classes with:

- **Pytest Fixtures**: Automatic setup and teardown via `driver` fixture
- **Isolated Sessions**: Each test method gets a fresh browser instance
- **Screenshot on Failure**: Automatically captures screenshots when tests fail
- **Parallel Execution**: Full support for pytest-xdist
- **Browser Selection**: Configure browser via pytest markers
- **Remote Execution**: Enable remote execution via markers
- **Proper Cleanup**: Ensures all resources are released after test execution

#### Key Features

```python
# Fixture scope: function (new driver per test)
# Auto-use: No (must explicitly request 'driver' fixture)
# Parallel safe: Yes (isolated sessions)
# Screenshot: Automatic on failure
# Logging: Comprehensive setup/teardown logs
```

#### Usage Example

**Simple Test:**
```python
from core.base_test import BaseTest

class TestExample(BaseTest):
    def test_page_title(self, driver):
        """Test using default browser from config."""
        driver.goto("https://example.com")
        assert "Example" in driver.title()
```

**Custom Browser:**
```python
import pytest
from core.base_test import BaseTest

class TestWithCustomBrowser(BaseTest):
    
    @pytest.mark.browser("firefox_latest")
    def test_with_firefox(self, driver):
        """Test using Firefox browser."""
        driver.goto("https://example.com")
        assert driver.url == "https://example.com/"
```

**Remote Execution:**
```python
import pytest
from core.base_test import BaseTest

class TestRemote(BaseTest):
    
    @pytest.mark.remote
    @pytest.mark.browser("chrome_127")
    def test_on_grid(self, driver):
        """Test on remote Selenium Grid."""
        driver.goto("https://example.com")
        assert driver.is_visible("h1")
```

## Architecture

### Driver Creation Flow

```
Test Method
    ↓
BaseTest.driver fixture
    ↓
DriverFactory(browser_name, remote)
    ↓
Load browser config from browsers.yaml
    ↓
Load framework config from config.yaml
    ↓
Create Playwright instance
    ↓
Launch browser (local or remote)
    ↓
Create browser context
    ↓
Create page
    ↓
Apply timeouts
    ↓
Return Page to test
```

### Teardown Flow

```
Test Method Completes
    ↓
Check test result
    ↓
If FAILED → Capture screenshot
    ↓
Close page
    ↓
Close context
    ↓
Close browser
    ↓
Stop Playwright
    ↓
Log teardown completion
```

## Configuration Integration

The core layer reads configuration from:

### From `config.yaml`:
- `default_timeout`: Default timeout for operations (seconds)
- `page_load_timeout`: Timeout for page loads (seconds)
- `retries`: Number of retry attempts for driver creation
- `retry_delay`: Delay between retries (seconds)
- `headless`: Default headless mode (boolean)
- `browser_width`: Default browser width (pixels)
- `browser_height`: Default browser height (pixels)
- `screenshot_on_failure`: Enable/disable failure screenshots
- `screenshot_path`: Directory for screenshots
- `grid_url`: URL for remote execution

### From `browsers.yaml`:
- `browsers.<profile_name>.browserName`: Browser type
- `browsers.<profile_name>.browserVersion`: Browser version
- `browsers.<profile_name>.platformName`: Operating system
- `browsers.<profile_name>.headless`: Headless mode override
- `browsers.<profile_name>.viewport`: Window dimensions
- `browsers.<profile_name>.args`: Browser launch arguments
- `browsers.<profile_name>.preferences`: Browser preferences
- `default_browser`: Default browser profile to use

## Parallel Execution

The framework fully supports parallel test execution with pytest-xdist:

```bash
# Run tests in parallel with 4 workers
pytest -n 4

# Auto-detect number of CPUs
pytest -n auto

# Run specific test file in parallel
pytest tests/test_example.py -n auto
```

### How It Works

1. **Isolated Sessions**: Each test gets its own `DriverFactory` and browser instance
2. **No Shared State**: Browser contexts are not shared between tests
3. **Thread-Safe Logging**: Loguru handles concurrent logging
4. **Independent Cleanup**: Each test cleans up its own resources

## Best Practices

### 1. Always Use the Fixture

```python
# ✓ Good
def test_example(self, driver):
    driver.goto("https://example.com")

# ✗ Bad - Don't create driver manually in tests
def test_example(self):
    factory = DriverFactory()
    driver = factory.get_driver()
```

### 2. Let Fixtures Handle Cleanup

```python
# ✓ Good - Fixture handles cleanup automatically
def test_example(self, driver):
    driver.goto("https://example.com")
    # No need to quit driver

# ✗ Bad - Don't quit driver manually
def test_example(self, driver):
    driver.goto("https://example.com")
    driver.close()  # Don't do this
```

### 3. Use Markers for Browser Selection

```python
# ✓ Good - Use markers
@pytest.mark.browser("firefox_latest")
def test_with_firefox(self, driver):
    pass

# ✗ Bad - Don't hardcode in test
def test_bad(self, driver):
    factory = DriverFactory("firefox_latest")  # Don't do this
```

### 4. Organize Tests in Classes

```python
# ✓ Good - Organized and readable
class TestLoginFeature(BaseTest):
    def test_valid_login(self, driver):
        pass
    
    def test_invalid_login(self, driver):
        pass
```

## Error Handling

The framework includes comprehensive error handling:

1. **Driver Creation Failures**: Automatically retries with configurable attempts
2. **Cleanup Errors**: Logs warnings but doesn't fail the test
3. **Screenshot Errors**: Logs error but doesn't block teardown
4. **Configuration Errors**: Raises clear exceptions with helpful messages

## Logging

All driver operations are logged using `loguru`:

```
INFO  | Setting up test: test_example
INFO  | Browser: chrome_127, Remote: False
INFO  | Creating local browser instance...
INFO  | Browser launched successfully: chromium
INFO  | Browser context created
INFO  | Page created successfully
INFO  | ✓ Driver setup completed for test: test_example
INFO  | Tearing down test: test_example
INFO  | ✓ Driver teardown completed for test: test_example
```

## Testing the Core Layer

To verify the core layer is working:

```bash
# Run the example test
pytest tests/test_example.py -v

# Run with specific browser
pytest tests/test_example.py --browser=firefox_latest -v

# Run in parallel
pytest tests/ -n auto -v
```

## Next Steps

After implementing the core layer, you can:

1. Create page object models in `pages/`
2. Implement test utilities in `utils/`
3. Write actual test cases in `tests/`
4. Add custom fixtures and helpers
5. Integrate with CI/CD pipelines

## Troubleshooting

### Browser Not Found
- Run `playwright install` to download browsers
- Check browser name in `browsers.yaml`

### Timeout Errors
- Adjust timeouts in `config.yaml`
- Check network connectivity
- Verify page load performance

### Screenshot Not Captured
- Check `screenshot_on_failure` in `config.yaml`
- Verify `screenshot_path` directory permissions
- Review logs for screenshot errors

### Parallel Execution Issues
- Each test should be independent
- Don't share data between tests
- Use unique test data per test
