# 🏗️ Project Architecture & Framework Features

## Table of Contents
1. [Project Structure](#project-structure)
2. [Framework Components](#framework-components)
3. [Step 4: Locator Strategy](#step-4-locator-strategy)
4. [Step 3: BaseTest + Fixtures](#step-3-basetest--fixtures)
5. [Configuration System](#configuration-system)
6. [Running Tests](#running-tests)
7. [Features Summary](#features-summary)

---

## Project Structure

```
automation-exercise/
├── conftest.py                          # Root pytest config (delegates to core.conftest)
├── pytest.ini                            # pytest configuration
├── README.md
├── QUICK_REFERENCE.md
├── STEP4_IMPLEMENTATION_SUMMARY.md
├── LOCATOR_STRATEGY_QUICK_REF.py
│
├── config/
│   ├── __init__.py
│   ├── config.yaml                      # Main framework configuration
│   ├── browsers.yaml                    # Browser profiles
│   ├── reporting.yaml                   # Reporting configuration
│   ├── config_loader.py                 # YAML configuration loader
│   └── README.md
│
├── core/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures & hooks
│   ├── base_test.py                     # Marker base class for all tests
│   ├── driver_factory.py                # Playwright browser factory
│   ├── base_page.py                     # Base page with LocatorUtility
│   ├── locator_strategy.py              # Multi-locator fallback mechanism
│   ├── LOCATOR_STRATEGY_README.md       # Detailed locator documentation
│   └── README.md
│
├── pages/
│   ├── example_page.py                  # Example page object
│   └── automation_store_page.py         # Real page object with multi-locators
│
├── tests/
│   ├── __init__.py
│   ├── test_core_demo.py
│   ├── test_locator_demo.py             # Locator fallback demonstration
│   └── test_step3_base_test.py          # Clean fixture-driven tests
│
├── logs/                                 # Auto-generated
│   └── pytest.log
│
├── reports/                              # Auto-generated per test run
│   ├── run_20260128_154520/
│   │   ├── allure-results/              # Allure report data
│   │   ├── *.png                        # Screenshots on failure
│   │   └── logs/
│   │
│   ├── run_20260128_160145/
│   │   ├── allure-results/
│   │   └── *.png
│   │
│   └── ... (more runs)
│
├── utils/
├── __pycache__/
└── requirements.txt
```

---

## Framework Components

### 1. Configuration System (config/)

#### ConfigLoader (`config/config_loader.py`)
- Loads YAML configuration files
- Caches loaded configs for performance
- Provides `get()`, `get_all()`, and `get_browser_config()` methods
- Handles missing files and invalid YAML gracefully

#### Configuration Files

**config/config.yaml** - Main settings:
```yaml
base_url: "https://automationteststore.com"
default_timeout: 10
page_load_timeout: 30
element_timeout: 5
screenshot_on_failure: true
screenshot_path: "reports/screenshots"
headless: false
browser_width: 1920
browser_height: 1080
```

**config/browsers.yaml** - Browser profiles:
```yaml
chrome_127:
  browserName: chromium
  version: "127"
firefox_latest:
  browserName: firefox
  headless: false
```

**config/reporting.yaml** - Reporting settings

### 2. Driver Factory (core/driver_factory.py)

**DriverFactory class** - Creates and manages Playwright browsers:
- ✅ Creates isolated browser instances
- ✅ Supports Playwright sync API
- ✅ Configurable browser profiles (from browsers.yaml)
- ✅ Handles browser context and page creation
- ✅ Automatic cleanup on teardown
- ✅ Supports local and remote execution

**Usage:**
```python
from core.driver_factory import DriverFactory

factory = DriverFactory(browser_name="chrome_127", remote=False)
page = factory.get_driver()
# ... use page ...
factory.quit_driver()
```

---

## Step 4: Locator Strategy

### Overview
Multi-locator fallback system allowing each UI element to have multiple locators (XPath, CSS, etc.) that are tried sequentially.

### Components

#### LocatorUtility (`core/locator_strategy.py`)
**Methods:**
- `find_element(locators, element_name)` - Finds element with fallback
- `click_element(locators, element_name)` - Clicks element with fallback
- `type_text(locators, text, element_name)` - Types text with fallback
- `get_text(locators, element_name)` - Gets text with fallback
- `is_visible(locators, element_name)` - Checks visibility with fallback

**Supported Locator Types:**
```python
{'type': 'xpath', 'value': '//button[@id="submit"]'}
{'type': 'css', 'value': '#submit'}
{'type': 'id', 'value': 'submit-btn'}
{'type': 'text', 'value': 'Submit'}
{'type': 'role', 'value': 'button'}
```

**Fallback Flow:**
```
Try Locator 1 → FAIL → Log
Try Locator 2 → FAIL → Log
Try Locator 3 → SUCCESS → Return Element

If ALL fail → Screenshot + Exception
```

#### BasePage (`core/base_page.py`)
**Features:**
- ✅ Integrates LocatorUtility internally
- ✅ Uses timeout from config (element_timeout)
- ✅ Provides clean API for page objects:
  - `click(locators, element_name)`
  - `type(locators, text, element_name)`
  - `get_text(locators, element_name)`
  - `is_visible(locators, element_name)`
  - `find_element(locators, element_name)`
  - `navigate_to(url)`
  - `get_title()`, `get_url()`

**Logging:**
- Each locator attempt logged
- Success/failure tracking
- Detailed error messages on total failure

#### Page Objects

**Example: AutomationStorePage** (`pages/automation_store_page.py`)
```python
class AutomationStorePage(BasePage):
    SEARCH_INPUT = [
        {'type': 'xpath', 'value': '//input[@id="WRONG_ID"]'},  # Fails
        {'type': 'css', 'value': '#filter_keyword'}              # Succeeds
    ]
    
    def enter_search_text(self, text: str):
        self.type(self.SEARCH_INPUT, text, "Search Input")
```

**Test Usage:**
```python
page = AutomationStorePage(driver)
page.enter_search_text("Hair Care")
# Framework handles fallback automatically
```

#### Test Examples

**test_locator_demo.py** - Demonstrates:
- ✅ Fallback from bad to good locator
- ✅ Multiple elements with fallback
- ✅ Exception when all locators fail
- ✅ Page object pattern

**test_step3_base_test.py** - Shows:
- ✅ Clean test pattern (no setup/teardown)
- ✅ Fixture-driven approach
- ✅ Multiple interactions in single test

---

## Step 3: BaseTest + Fixtures

### Architecture

**conftest.py Hierarchy:**
```
/conftest.py (root)
  ↓ delegates via pytest_plugins
core/conftest.py (actual fixtures & hooks)
```

### Fixtures

#### driver fixture (function scope)
**Provides:** Fresh Playwright Page instance
**Lifecycle:**
1. Creates DriverFactory with browser config
2. Creates Page via factory.get_driver()
3. Yields to test
4. Captures screenshot on failure
5. Cleans up browser/context/page

**Usage in tests:**
```python
class TestExample(BaseTest):
    def test_something(self, driver):
        driver.goto("https://example.com")
        assert driver.title() == "Example"
```

#### config fixture (session scope)
**Provides:** Loaded configuration dictionary
**Usage:**
```python
def test_example(config):
    timeout = config.get('element_timeout', 5)
```

### Hooks & Setup

#### pytest_configure
- **Creates timestamped reports directory:** `reports/run_YYYYMMDD_HHMMSS/`
- **Registers pytest markers:**
  - `@pytest.mark.browser("firefox_latest")`
  - `@pytest.mark.remote`
- **Sets Allure report directory** to timestamped folder
- **Creates allure-results/ subdirectory**

#### pytest_runtest_makereport
- Captures test execution result
- Detects test failure
- Triggers screenshot capture

#### setup_test_environment (session scope)
- Logs test session start/end
- Creates required directories once per run

### BaseTest Class (`core/base_test.py`)
```python
class BaseTest:
    pass  # Marker class for all tests
```

**Purpose:**
- Indicates test inherits from framework
- Anchor point for future helper methods
- Convention for test organization

---

## Configuration System

### Loading Config

```python
from config.config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load_config("config")
browser_config = loader.get_browser_config("chrome_127")
timeout = loader.get("element_timeout", default=5)
```

### Setting Timeouts

In **config/config.yaml**:
```yaml
default_timeout: 10      # General timeout
page_load_timeout: 30    # Page load
element_timeout: 5       # Element operations (LocatorUtility)
```

LocatorUtility uses `element_timeout` automatically.

---

## Running Tests

### Basic Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_locator_demo.py

# Run specific test
pytest tests/test_locator_demo.py::TestLocatorFallbackDemo::test_fallback_with_intentional_bad_locator

# Verbose output
pytest -v

# With detailed output and logging
pytest -v -s

# Specific browser
pytest --browser=firefox_latest

# Remote execution
pytest --remote
```

### Output

Each run creates:
```
reports/run_20260128_154520/
├── allure-results/           ← Allure report data
│   ├── 000018f0-f5f3-44c5-result.json
│   ├── 002db407-07a6-407f-attachment.txt
│   └── ... (one per test)
├── email_field_20260128_154520.png
├── search_button_20260128_154521.png
└── ... (failures only)
```

### Allure Reports

```bash
# Generate HTML report
allure serve reports/run_20260128_154520/allure-results/

# Generate HTML in directory
allure generate reports/run_20260128_154520/allure-results/ -o reports/allure-html/
```

---

## Features Summary

### ✅ Core Features

#### Driver Management
- ✅ Playwright-based (async-safe)
- ✅ Browser profile support
- ✅ Automatic cleanup
- ✅ Parallel execution ready

#### Configuration Management
- ✅ YAML-based configuration
- ✅ Multiple config files
- ✅ Caching for performance
- ✅ Default value support

#### Test Fixtures
- ✅ Function-scoped driver
- ✅ Session-scoped config
- ✅ No setup/teardown in tests
- ✅ Automatic failure handling

#### Locator Strategy
- ✅ Multi-locator fallback
- ✅ Sequential attempt tracking
- ✅ Detailed logging
- ✅ Screenshot on total failure
- ✅ 5 locator types supported

#### Page Object Pattern
- ✅ BasePage integration
- ✅ Encapsulated locators
- ✅ Clean API methods
- ✅ Reusable across tests

#### Reporting & Logging
- ✅ Per-run timestamped directories
- ✅ Allure integration
- ✅ Screenshot capture on failure
- ✅ Detailed pytest logging
- ✅ Loguru integration

#### Parallel Execution
- ✅ pytest-xdist compatible
- ✅ Isolated browser sessions
- ✅ Per-run report directories
- ✅ No global state

### ⚙️ Framework Defaults

| Setting | Value | Configurable |
|---------|-------|--------------|
| Default Timeout | 10 sec | Yes |
| Element Timeout | 5 sec | Yes |
| Page Load Timeout | 30 sec | Yes |
| Screenshot on Failure | true | Yes |
| Headless Mode | false | Yes |
| Browser Width | 1920px | Yes |
| Browser Height | 1080px | Yes |

---

## Best Practices

### 1. Test Structure
```python
from core.base_test import BaseTest
from pages.your_page import YourPage

class TestYourFeature(BaseTest):
    def test_something(self, driver):
        page = YourPage(driver)
        page.perform_action()
        assert page.verify_result()
```

### 2. Locator Definition
```python
class YourPage(BasePage):
    # More specific → Less specific
    BUTTON = [
        {'type': 'id', 'value': 'submit'},
        {'type': 'css', 'value': 'button.submit'},
        {'type': 'xpath', 'value': '//button[text()="Submit"]'}
    ]
```

### 3. Configuration Usage
```python
# Use config from fixture
def test_example(config, driver):
    timeout = config.get('element_timeout', 5)
    # Use timeout...
```

### 4. Markers
```python
@pytest.mark.browser("firefox_latest")
def test_firefox_specific(self, driver):
    pass

@pytest.mark.remote
def test_on_grid(self, driver):
    pass
```

---

## Debugging

### View Logs
```bash
# Real-time logs
pytest -v -s

# Check log file
tail -f logs/pytest.log
```

### View Allure Report
```bash
# Open in browser
allure serve reports/run_20260128_154520/allure-results/
```

### Check Screenshots
```bash
# View failure screenshots
ls reports/run_20260128_154520/*.png
```

### Locator Debugging
```
[DEBUG] Search Input [Locator 1/2]: Attempting XPATH: //input[@id="wrong"]
[DEBUG] Search Input [Locator 1/2]: ✗ FAILED - Element not visible
[DEBUG] Search Input [Locator 2/2]: Attempting CSS: #filter_keyword
[INFO]  Search Input [Locator 2/2]: ✓ SUCCESS with CSS: #filter_keyword
```

---

## Extension Points

### Adding New Page Objects
```python
# pages/my_page.py
from core.base_page import BasePage

class MyPage(BasePage):
    ELEMENT = [
        {'type': 'css', 'value': '#element'}
    ]
    
    def my_method(self):
        self.click(self.ELEMENT, "Element Name")
```

### Adding Helper Methods to BaseTest
```python
# core/base_test.py
class BaseTest:
    def assert_text(self, locators, expected_text):
        text = self.locator_util.get_text(locators)
        assert text == expected_text
```

### Adding Custom Fixtures
```python
# core/conftest.py
@pytest.fixture
def api_client():
    client = APIClient()
    yield client
    client.close()
```

---

## Summary

This framework provides:
1. **Clean test code** - No setup/teardown logic
2. **Robust element location** - Multi-locator fallback
3. **Organized architecture** - Clear separation of concerns
4. **Production-ready** - Logging, reporting, screenshots
5. **Scalable** - Parallel execution support
6. **Maintainable** - Configuration-driven, page object pattern

**Total Components:**
- ✅ 3 pytest fixtures
- ✅ 4 pytest hooks
- ✅ 2 page object examples
- ✅ 2 test suites
- ✅ 5 locator types
- ✅ 8 core methods
- ✅ 100% integration with existing framework
