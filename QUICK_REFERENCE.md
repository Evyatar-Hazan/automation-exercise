# Quick Reference Guide - STEP 2: Core Layer

## Quick Start

### 1. Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 2. Write Your First Test
```python
# tests/test_my_feature.py
from core.base_test import BaseTest

class TestMyFeature(BaseTest):
    def test_example(self, driver):
        driver.goto("https://example.com")
        assert "Example" in driver.title()
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto

# Run specific test
pytest tests/test_my_feature.py::TestMyFeature::test_example
```

## Common Patterns

### Basic Test
```python
from core.base_test import BaseTest

class TestLogin(BaseTest):
    def test_successful_login(self, driver):
        driver.goto("https://example.com/login")
        driver.fill("#username", "user@example.com")
        driver.fill("#password", "password123")
        driver.click("button[type='submit']")
        assert driver.url == "https://example.com/dashboard"
```

### Test with Specific Browser
```python
import pytest
from core.base_test import BaseTest

class TestCrossBrowser(BaseTest):
    @pytest.mark.browser("firefox_latest")
    def test_in_firefox(self, driver):
        driver.goto("https://example.com")
        # Firefox-specific test
```

### Parameterized Tests
```python
import pytest
from core.base_test import BaseTest

class TestMultipleInputs(BaseTest):
    @pytest.mark.parametrize("username,password", [
        ("user1@example.com", "pass1"),
        ("user2@example.com", "pass2"),
    ])
    def test_login_multiple_users(self, driver, username, password):
        driver.goto("https://example.com/login")
        driver.fill("#username", username)
        driver.fill("#password", password)
        driver.click("button[type='submit']")
        assert driver.is_visible(".dashboard")
```

### Test with Setup/Cleanup
```python
import pytest
from core.base_test import BaseTest

class TestWithSetup(BaseTest):
    @pytest.fixture(autouse=True)
    def setup_test_data(self, driver):
        # Setup before each test
        driver.goto("https://example.com/setup")
        # ... setup code
        
        yield
        
        # Cleanup after each test
        driver.goto("https://example.com/cleanup")
        # ... cleanup code
    
    def test_feature_1(self, driver):
        # Test code here
        pass
```

## Playwright Common Operations

### Navigation
```python
# Go to URL
driver.goto("https://example.com")

# Go back
driver.go_back()

# Go forward
driver.go_forward()

# Reload
driver.reload()
```

### Element Interaction
```python
# Click
driver.click("button#submit")

# Fill input
driver.fill("#email", "user@example.com")

# Type (slower, character by character)
driver.type("#search", "search term")

# Check/Uncheck
driver.check("#agree")
driver.uncheck("#newsletter")

# Select option
driver.select_option("#country", "USA")
```

### Element Queries
```python
# Locator
button = driver.locator("button.primary")

# Is visible
driver.is_visible("h1")

# Get text
text = driver.locator("h1").text_content()

# Get attribute
href = driver.locator("a").get_attribute("href")

# Wait for element
driver.wait_for_selector("#loading", state="hidden")

# Count elements
count = driver.locator("li.item").count()
```

### Assertions
```python
# Expect visible
expect(driver.locator("h1")).to_be_visible()

# Expect text
expect(driver.locator("h1")).to_have_text("Welcome")

# Expect URL
expect(driver).to_have_url("https://example.com/dashboard")

# Expect title
expect(driver).to_have_title("Dashboard")
```

### Screenshots
```python
# Full page screenshot
driver.screenshot(path="screenshot.png", full_page=True)

# Element screenshot
driver.locator("#header").screenshot(path="header.png")
```

## Browser Configuration

### Available Browser Profiles (from browsers.yaml)
- `chrome_127` - Chrome/Chromium 127 on Linux
- `chrome_latest` - Latest Chrome/Chromium on Linux
- `firefox_latest` - Latest Firefox on Linux
- `firefox_esr` - Firefox ESR 115 on Linux
- `edge_latest` - Latest Edge on Windows
- `webkit_latest` - Latest WebKit on macOS

### Select Browser in Test
```python
@pytest.mark.browser("firefox_latest")
def test_example(self, driver):
    pass
```

### Select Browser from Command Line
```bash
pytest --browser=firefox_latest
```

## Running Tests

### Basic Execution
```bash
# All tests
pytest

# Specific file
pytest tests/test_login.py

# Specific class
pytest tests/test_login.py::TestLogin

# Specific test
pytest tests/test_login.py::TestLogin::test_successful_login

# Verbose
pytest -v

# Very verbose
pytest -vv
```

### Parallel Execution
```bash
# 4 workers
pytest -n 4

# Auto-detect CPUs
pytest -n auto

# Distribute by file
pytest -n auto --dist loadfile
```

### Markers
```bash
# Run smoke tests
pytest -m smoke

# Run regression tests
pytest -m regression

# Run smoke OR regression
pytest -m "smoke or regression"

# Run NOT smoke
pytest -m "not smoke"
```

### Filtering
```bash
# By keyword
pytest -k "login"

# Multiple keywords
pytest -k "login or logout"

# Exclude
pytest -k "not slow"
```

### Output Options
```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show locals on failure
pytest -l

# Show full traceback
pytest --tb=long

# Show short traceback
pytest --tb=short

# No traceback
pytest --tb=no
```

## Configuration Files

### config.yaml - Framework Settings
```yaml
base_url: "https://example.com"
default_timeout: 10  # seconds
retries: 2
headless: false
screenshot_on_failure: true
```

### browsers.yaml - Browser Profiles
```yaml
browsers:
  chrome_127:
    browserName: "chromium"
    browserVersion: "127.0"
    platformName: "linux"
    headless: false
```

### pytest.ini - Pytest Configuration
```ini
[pytest]
testpaths = tests
markers =
    smoke: Quick smoke tests
    regression: Full regression suite
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'playwright'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
playwright install
```

**Issue**: `playwright._impl._api_types.Error: Executable doesn't exist`
```bash
# Solution: Install Playwright browsers
playwright install
```

**Issue**: Test fails but no screenshot captured
```bash
# Solution: Check config.yaml
screenshot_on_failure: true
screenshot_path: "reports/screenshots"
```

**Issue**: Timeout errors
```bash
# Solution: Increase timeouts in config.yaml
default_timeout: 30  # increase from 10
page_load_timeout: 60  # increase from 30
```

## Next Steps

After mastering the core layer:

1. **Page Object Model**: Create reusable page classes
2. **Test Data Management**: External data files and fixtures
3. **Custom Utilities**: Helper functions for common operations
4. **API Integration**: Combine UI and API testing
5. **CI/CD**: Integrate with Jenkins, GitHub Actions, etc.

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [Core Layer README](core/README.md)
- [Configuration README](config/README.md)
