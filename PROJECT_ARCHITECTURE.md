# 🏗️ Project Architecture & Framework Features

## Table of Contents
1. [Project Structure](#project-structure)
2. [Framework Components](#framework-components)
3. [Step 7: Data-Driven Testing](#step-7-data-driven-testing) ⭐ NEW
4. [Step 6: Dynamic Browser Matrix](#step-6-dynamic-browser-matrix)
5. [Step 5: Reporting System](#step-5-reporting-system)
6. [Step 4: Locator Strategy](#step-4-locator-strategy)
7. [Step 3: BaseTest + Fixtures](#step-3-basetest--fixtures)
8. [Configuration System](#configuration-system)
9. [Running Tests](#running-tests)
10. [Features Summary](#features-summary)

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
├── reporting/                            # 🆕 NEW: Reporting abstraction layer
│   ├── __init__.py
│   ├── reporter.py                      # Abstract Reporter interface
│   ├── allure_reporter.py               # Allure implementation
│   └── manager.py                       # ReportingManager (facade/singleton)
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
│   ├── __init__.py
│   └── data_loader.py                   # Data-Driven Testing module
│
├── test_data/                            # 🆕 NEW: Test data files
│   ├── login.yaml                        # Login credentials (YAML)
│   ├── search.json                       # Search queries (JSON)
│   ├── users.csv                         # User records (CSV)
│   └── product_filters.yaml              # Filter configurations (YAML)
│
├── __pycache__/
└── requirements.txt
```

---

## Framework Components

### 0. Data-Driven Testing (Step 7) ⭐ NEW

#### Overview
Data-Driven Testing layer enables loading test inputs from external files (YAML, JSON, CSV) and running multiple test scenarios through pytest parametrization. Test data is completely separated from test logic.

#### Architecture

**Data Flow:**
```
Test Data File (YAML/JSON/CSV)
    ↓
load_test_data(path)
    ↓
DataLoader (auto-detect format)
    ↓
Normalize → List[Dict[str, Any]]
    ↓
@pytest.mark.parametrize
    ↓
Multiple test executions (one per data row)
```

#### Core Components

**DataLoader** (`utils/data_loader.py`)
- Auto-detects file format by extension (`.yaml`, `.yml`, `.json`, `.csv`)
- Normalizes all formats to `List[Dict[str, Any]]`
- Supports root keys in YAML/JSON: `tests`, `data`, `cases`, `test_cases`, `rows`
- Custom exception: `DataLoaderError` with clear messages

```python
from utils.data_loader import load_test_data

# Load any format - same return type
yaml_data = load_test_data("test_data/login.yaml")    # List[Dict]
json_data = load_test_data("test_data/search.json")   # List[Dict]
csv_data = load_test_data("test_data/users.csv")      # List[Dict]
```

**Supported Formats:**

1. **YAML** (Preferred)
```yaml
tests:
  - username: user1
    password: pass1
    expected_role: admin
  - username: user2
    password: pass2
    expected_role: user
```

2. **JSON**
```json
{
  "tests": [
    { "username": "user1", "password": "pass1", "expected_role": "admin" },
    { "username": "user2", "password": "pass2", "expected_role": "user" }
  ]
}
```

3. **CSV** (Headers → Dict Keys)
```csv
username,password,expected_role
user1,pass1,admin
user2,pass2,user
```

#### Integration with pytest

**Direct Parametrization (Recommended):**
```python
from utils.data_loader import load_test_data
import pytest

class TestLoginDataDriven(BaseTest):
    
    @pytest.mark.parametrize(
        "login_data",
        load_test_data("test_data/login.yaml"),
        ids=lambda d: d["username"]
    )
    def test_login(self, driver, login_data):
        """Parametrized test runs for each data row"""
        page = LoginPage(driver)
        page.login(login_data["username"], login_data["password"])
        
        if login_data.get("expected_role"):
            assert page.get_user_role() == login_data["expected_role"]
```

**Generated Test Variants:**
```
test_login[user1] [chrome_127] PASSED
test_login[user1] [chrome_latest] PASSED
test_login[user1] [firefox_latest] PASSED
test_login[user2] [chrome_127] PASSED
test_login[user2] [chrome_latest] PASSED
test_login[user2] [firefox_latest] PASSED

6 tests generated from 1 method × 2 data rows × 3 browsers
```

**Optional Fixture Wrapper:**
```python
@pytest.fixture(params=load_test_data("test_data/login.yaml"))
def login_data(request):
    return request.param

def test_login_with_fixture(driver, login_data):
    """Alternative pattern - useful for complex setup/teardown"""
    page = LoginPage(driver)
    page.login(login_data["username"], login_data["password"])
```

#### Error Handling

Custom `DataLoaderError` exception with clear messages:

```python
from utils.data_loader import load_test_data, DataLoaderError

try:
    data = load_test_data("test_data/missing.yaml")
except DataLoaderError as e:
    # "Data file not found: /abs/path/test_data/missing.yaml"
    # "Unsupported file format: .txt"
    # "Empty dataset in login.yaml"
    # "Invalid data structure in search.json"
    print(f"Error: {e}")
```

#### Logging Integration

All data loading is logged via loguru:
- `DEBUG`: File loading start
- `INFO`: Successful load with test case count
- `WARNING`: Ambiguous data structure

```
[DEBUG] Loading test data from: test_data/login.yaml
[INFO] Successfully loaded 5 test case(s) from login.yaml
```

#### Features

✅ **Format Flexibility** - Switch YAML ↔ JSON ↔ CSV without changing tests  
✅ **Automatic Root Key Detection** - Recognizes `tests`, `data`, `cases`, etc.  
✅ **CSV Type Handling** - Headers converted to dict keys  
✅ **pytest Integration** - Direct parametrization & custom IDs  
✅ **Browser Matrix Support** - Combines with browser matrix automatically  
✅ **Error Handling** - Clear validation and error messages  
✅ **Logging** - Full integration with loguru  
✅ **Backward Compatible** - Opt-in per test, no breaking changes  

#### Sample Test Data Files

- `test_data/login.yaml` - 5 login scenarios with roles
- `test_data/search.json` - 4 search queries with expected result counts
- `test_data/users.csv` - 5 user accounts with multiple fields
- `test_data/product_filters.yaml` - 5 filter configurations

#### Documentation

See detailed documentation in:
- [GETTING_STARTED_DATA_DRIVEN.md](GETTING_STARTED_DATA_DRIVEN.md) - 5-minute quick start
- [DATA_DRIVEN_TESTING_QUICK_REF.md](DATA_DRIVEN_TESTING_QUICK_REF.md) - Quick reference
- [DATA_DRIVEN_TESTING.md](DATA_DRIVEN_TESTING.md) - Complete guide (400+ lines)
- [DATA_DRIVEN_EXAMPLES.py](DATA_DRIVEN_EXAMPLES.py) - 10 copy-paste code examples

---

### 1. Dynamic Browser Matrix (Step 6)

#### Overview
Fully dynamic browser matrix system that enables running the same tests across multiple browsers/versions without any test code changes. Tests are automatically parametrized at pytest collection time.

#### Key Architecture

**Collection-Time Parametrization:**
```
pytest_generate_tests() hook (core/conftest.py)
    ↓
Load matrix from config/browsers.yaml
    ↓
Parametrize tests with profile dictionaries
    ↓
One test → Multiple variants: test_name[chrome_127], test_name[chrome_latest], test_name[firefox_latest]
    ↓
Each variant gets isolated browser_profile fixture
    ↓
DriverFactory creates separate browser per variant
```

**Configuration-Driven:**
```yaml
# config/browsers.yaml
matrix:
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
    viewport: {width: 1920, height: 1080}
  
  - name: chrome_latest
    browserName: "chromium"
    browserVersion: "latest"
    headless: false
  
  - name: firefox_latest
    browserName: "firefox"
    browserVersion: "latest"
    headless: false
```

#### Components

**ConfigLoader** (`config/config_loader.py`)
- New method: `get_browser_matrix() -> List[Dict[str, Any]]`
- Loads `matrix:` section from browsers.yaml
- Fallback support for legacy `browsers:` dictionary format
- Caching for performance (matrix loaded once per collection)

```python
config_loader = ConfigLoader()
matrix = config_loader.get_browser_matrix()
# Returns: [
#   {'name': 'chrome_127', 'browserName': 'chromium', 'browserVersion': '127.0', ...},
#   {'name': 'chrome_latest', 'browserName': 'chromium', 'browserVersion': 'latest', ...},
#   {'name': 'firefox_latest', 'browserName': 'firefox', 'browserVersion': 'latest', ...}
# ]
```

**DriverFactory** (`core/driver_factory.py`)
- Refactored `__init__()` to accept `Union[str, Dict[str, Any]]` browser_profile
- Handles dictionary input (preferred from parametrization)
- Supports string input for backward compatibility
- Extracts config from profile dict at initialization

```python
# New: Accept profile dict (from pytest parametrization)
factory = DriverFactory(browser_profile={
    'name': 'chrome_127',
    'browserName': 'chromium',
    'browserVersion': '127.0',
    'headless': False
})

# Still works: Legacy string input (backward compat)
factory = DriverFactory(browser_profile='chrome_127')
```

**pytest_generate_tests Hook** (`core/conftest.py`)
- Collection-time hook that parametrizes tests
- Loads browser matrix only once, caches it
- Supports CLI override: `pytest --browser=chrome_127`
- Filters matrix when override specified

```python
def pytest_generate_tests(metafunc):
    """Collection-time parametrization hook"""
    if 'browser_profile' not in metafunc.fixturenames:
        return
    
    # Load matrix once per collection
    global _BROWSER_MATRIX
    if _BROWSER_MATRIX is None:
        config_loader = ConfigLoader()
        _BROWSER_MATRIX = config_loader.get_browser_matrix()
    
    # Handle CLI override: pytest --browser=chrome_127
    browser_override = metafunc.config.getoption("--browser", default=None)
    if browser_override:
        matrix_to_use = [p for p in _BROWSER_MATRIX if p.get('name') == browser_override]
    else:
        matrix_to_use = _BROWSER_MATRIX
    
    # Parametrize with profile dicts and names as IDs
    profile_ids = [p.get('name') for p in enumerate(matrix_to_use)]
    metafunc.parametrize('browser_profile', matrix_to_use, ids=profile_ids, scope='function')
```

**browser_profile Fixture** (`core/conftest.py`)
- New fixture that receives parametrized profile dictionaries
- No scope specification (test-level by default)
- Provides dict to driver fixture

```python
@pytest.fixture(scope="function")
def browser_profile(request) -> Dict[str, Any]:
    """Receives parametrized browser profile dict"""
    return request.param
```

**driver Fixture** (`core/conftest.py`)
- Refactored to accept `browser_profile` parameter
- Creates DriverFactory with profile dict
- Ensures isolated browser per test variant
- Full cleanup after test

```python
@pytest.fixture(scope="function")
def driver(browser_profile: Dict[str, Any]) -> Generator[Page, None, None]:
    """Function-scoped fixture receives parametrized browser_profile"""
    factory = DriverFactory(browser_profile=browser_profile, remote=False)
    page_instance = factory.get_driver()
    yield page_instance
    factory.quit_driver()
```

#### Test Execution Flow

**Before:**
```
test_login() → Runs once → Uses first browser
test_logout() → Runs once → Uses first browser
```

**After:**
```
pytest_generate_tests() [Collection Time]
    ↓
Test 1: test_login[chrome_127]
Test 2: test_login[chrome_latest]
Test 3: test_login[firefox_latest]
Test 4: test_logout[chrome_127]
Test 5: test_logout[chrome_latest]
Test 6: test_logout[firefox_latest]

pytest --collect-only output:
6 tests collected (2 tests × 3 browsers)
```

**Isolation:**
- Each variant: New browser instance
- Each variant: New browser context
- Each variant: New page object
- Full cleanup after each variant
- No shared state between variants

#### Usage Examples

**Simple Test (No Changes Needed):**
```python
class TestLoginFlow(BaseTest):
    def test_login_with_valid_credentials(self, driver):
        """Automatically runs on all 3 browsers in matrix"""
        driver.goto("https://example.com/login")
        # No browser-specific logic needed
        # Framework handles everything
        
    def test_logout(self, driver):
        """Also automatically runs on all 3 browsers"""
        # ... test code ...
```

**Pytest Output:**
```
test_login_with_valid_credentials[chrome_127] PASSED
test_login_with_valid_credentials[chrome_latest] PASSED
test_login_with_valid_credentials[firefox_latest] PASSED
test_logout[chrome_127] PASSED
test_logout[chrome_latest] PASSED
test_logout[firefox_latest] PASSED

6 passed in 2.34s
```

**CLI Override (Single Browser):**
```bash
# Run only on Chrome 127
pytest tests/ --browser=chrome_127

# Output:
# test_login_with_valid_credentials[chrome_127] PASSED
# test_logout[chrome_127] PASSED
# 2 passed in 0.45s
```

**Parallel Execution:**
```bash
# Run all browser variants in parallel (pytest-xdist)
pytest tests/ -n auto

# pytest-xdist distributes:
# Worker 1: test_login[chrome_127]
# Worker 2: test_login[chrome_latest]
# Worker 3: test_login[firefox_latest]
# Worker 1: test_logout[chrome_127] (after first test)
# ...
```

#### Adding New Browsers

**Step 1: Edit config/browsers.yaml**
```yaml
matrix:
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
  
  - name: chrome_latest
    browserName: "chromium"
    browserVersion: "latest"
  
  - name: firefox_latest
    browserName: "firefox"
    browserVersion: "latest"
  
  - name: webkit_latest  # NEW
    browserName: "webkit"
    browserVersion: "latest"
```

**Step 2: Run Tests**
```bash
pytest tests/
# Automatically runs on 4 browsers now!
# No test code changes required
```

**Available Browser Types:**
- `chromium` (Chrome, Edge, Opera)
- `firefox` (Firefox)
- `webkit` (Safari)

#### Features

✅ **Zero Test Changes** - Same test runs on all browsers automatically
✅ **YAML Configuration** - Add/remove browsers via config only
✅ **Parallel Execution** - pytest-xdist compatible, linear scaling
✅ **Full Isolation** - Each browser variant has completely separate instance
✅ **Flexible Profiles** - Each browser can have different settings (headless, viewport, etc.)
✅ **CLI Override** - `--browser=name` filters to specific browser
✅ **Performance** - Matrix loaded once at collection, negligible overhead
✅ **Backward Compatible** - Legacy string parameters still work
✅ **Legacy Format Support** - Old YAML `browsers:` section still works

#### Architecture Diagram

```
config/browsers.yaml (YAML matrix definition)
        ↓
ConfigLoader.get_browser_matrix() (loads & caches)
        ↓
pytest_generate_tests() (collection-time)
        ↓
Parametrize tests with profile dicts
        ↓
browser_profile fixture (receives parametrized dict)
        ↓
driver fixture (passes to DriverFactory)
        ↓
DriverFactory.__init__(browser_profile=dict)
        ↓
Playwright browser created with profile settings
        ↓
Test executes on specific browser variant
        ↓
Cleanup (browser.close(), context.close())
```

#### Known Patterns

**What Tests Should NOT Do:**
❌ Don't hardcode browser type in test
❌ Don't use @pytest.mark.browser() decorator (removed, automatic now)
❌ Don't create DriverFactory directly (use driver fixture)
❌ Don't access browser_profile dict directly (it's for framework use)

**What Tests SHOULD Do:**
✅ Use `driver` fixture parameter
✅ Keep test logic browser-agnostic
✅ Define browser behavior in config/browsers.yaml
✅ Use ConfigLoader if accessing browser config

---

### 2. Reporting System (reporting/)

#### Overview
Abstraction layer for test reporting that enables easy switching between Allure, Extent Reports, Report Portal, etc. without changing test code.

#### Architecture

**Reporter Interface** (`reporting/reporter.py`)
- Abstract base class defining the contract for all reporters
- Methods:
  - `log_step(message: str)` - Log test steps
  - `attach_screenshot(name: str, path: str)` - Attach images
  - `attach_text(name: str, content: str)` - Attach text/logs
  - `attach_exception(name: str, exception: Exception)` - Attach errors

**AllureReporter** (`reporting/allure_reporter.py`)
- Implements Reporter interface using Allure Python API
- Only file containing direct Allure imports
- Wraps Allure-specific logic cleanly

**ReportingManager** (`reporting/manager.py`)
- Facade providing single access point for reporters
- Singleton pattern for safe initialization
- Methods:
  - `init(reporter_type: str)` - Initialize during pytest_configure
  - `reporter() -> Reporter` - Get active reporter instance
  - `is_initialized() -> bool` - Check initialization status
  - `reset()` - Reset for testing/switching reporters

#### Usage

**In pytest hooks:**
```python
def pytest_configure(config):
    from reporting.manager import ReportingManager
    ReportingManager.init("allure")
```

**In tests/pages (optional custom reporting):**
```python
from reporting.manager import ReportingManager

ReportingManager.reporter().log_step("Click login button")
ReportingManager.reporter().attach_screenshot("Login page", "path/to/image.png")
```

#### Key Features
- ✅ Allure working seamlessly now
- ✅ Easy extension to other reporters (Extent, Report Portal)
- ✅ Zero changes to tests when switching reporters
- ✅ No Allure imports outside `reporting/` module
- ✅ Configuration-driven reporter type

---

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

**config/browsers.yaml** - Browser profiles (with new matrix format):
```yaml
# 🆕 NEW: Dynamic browser matrix for parametrization
matrix:
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
    viewport: {width: 1920, height: 1080}
    args: ["--disable-blink-features=AutomationControlled"]
  
  - name: chrome_latest
    browserName: "chromium"
    browserVersion: "latest"
    headless: false
  
  - name: firefox_latest
    browserName: "firefox"
    browserVersion: "latest"
    headless: false

# Legacy format still supported for backward compatibility
browsers:
  chrome_127:
    browserName: chromium
    version: "127"
  firefox_latest:
    browserName: firefox
```

**config/reporting.yaml** - Reporting settings

### 2. Driver Factory (core/driver_factory.py)

**DriverFactory class** - Creates and manages Playwright browsers:
- ✅ Creates isolated browser instances
- ✅ Supports Playwright sync API
- ✅ **NEW: Accepts Union[str, Dict[str, Any]] browser_profile** (profile dict from parametrization)
- ✅ Configurable browser profiles (from browsers.yaml)
- ✅ Handles browser context and page creation
- ✅ Automatic cleanup on teardown
- ✅ Supports local and remote execution

**Usage:**
```python
from core.driver_factory import DriverFactory

# NEW: From pytest parametrization (recommended)
profile_dict = {'name': 'chrome_127', 'browserName': 'chromium', 'browserVersion': '127.0', ...}
factory = DriverFactory(browser_profile=profile_dict, remote=False)

# Legacy: By profile name (still supported)
factory = DriverFactory(browser_profile="chrome_127", remote=False)

page = factory.get_driver()
# ... use page ...
factory.quit_driver()
```

---

---

### 3. Locator Strategy (core/locator_strategy.py)
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

## Step 4: BaseTest + Fixtures

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

## Step 3: BaseTest + Fixtures

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
# 🆕 NEW: Run all tests on all browsers in matrix (default behavior)
pytest

# Run specific test file (on all browsers)
pytest tests/test_core_demo.py

# Run specific test class (on all browsers)
pytest tests/test_core_demo.py::TestCoreFramework

# Verbose output (shows parametrization variants)
pytest -v

# With detailed output and logging
pytest -v -s

# 🆕 NEW: Run on specific browser only (matrix override)
pytest tests/ --browser=chrome_127

# 🆕 NEW: Run on all browsers, list what will run
pytest tests/ --collect-only

# 🆕 NEW: Run on all browsers in parallel (pytest-xdist)
pytest tests/ -n auto

# Remote execution
pytest --remote
```

### Output Examples

**Standard Run (All Browsers):**
```bash
$ pytest tests/ -v
collected 6 items

tests/test_core_demo.py::TestCoreFramework::test_driver_initialization[chrome_127] PASSED
tests/test_core_demo.py::TestCoreFramework::test_driver_initialization[chrome_latest] PASSED
tests/test_core_demo.py::TestCoreFramework::test_driver_initialization[firefox_latest] PASSED
tests/test_core_demo.py::TestCoreFramework::test_config_fixture[chrome_127] PASSED
tests/test_core_demo.py::TestCoreFramework::test_config_fixture[chrome_latest] PASSED
tests/test_core_demo.py::TestCoreFramework::test_config_fixture[firefox_latest] PASSED

6 passed in 2.34s
```

**With --browser Override:**
```bash
$ pytest tests/ --browser=chrome_127 -v
collected 2 items

tests/test_core_demo.py::TestCoreFramework::test_driver_initialization[chrome_127] PASSED
tests/test_core_demo.py::TestCoreFramework::test_config_fixture[chrome_127] PASSED

2 passed in 0.45s
```

**With --collect-only (Preview):**
```bash
$ pytest tests/ --collect-only
collected 6 items

<Function test_driver_initialization[chrome_127]>
<Function test_driver_initialization[chrome_latest]>
<Function test_driver_initialization[firefox_latest]>
<Function test_config_fixture[chrome_127]>
<Function test_config_fixture[chrome_latest]>
<Function test_config_fixture[firefox_latest]>
```

### Output

Each run creates:
```
reports/run_20260128_154520/
├── allure-results/           ← Allure report data (one per test variant)
│   ├── 000018f0-f5f3-44c5-result.json
│   ├── 002db407-07a6-407f-attachment.txt
│   └── ... (6 test results when running all browsers)
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
- ✅ Allure integration (via ReportingManager)
- ✅ Screenshot capture on failure
- ✅ Detailed pytest logging
- ✅ Loguru integration
- ✅ **NEW: Extensible ReportingManager (Allure, Extent, Report Portal ready)**

#### Reporting Abstraction
- ✅ Abstract Reporter interface
- ✅ AllureReporter implementation
- ✅ ReportingManager facade
- ✅ Configuration-driven reporter type
- ✅ Zero test changes when switching reporters

#### Data-Driven Testing ⭐ NEW (Step 7)
- ✅ YAML, JSON, CSV data file support
- ✅ Auto-detect format by extension
- ✅ Automatic root key detection (tests, data, cases, etc.)
- ✅ Unified API: `load_test_data(path) -> List[Dict]`
- ✅ pytest parametrization integration
- ✅ Custom test ID generation
- ✅ Optional fixture wrapper support
- ✅ Clear error handling (DataLoaderError)
- ✅ Full loguru logging integration
- ✅ Zero test code changes for format switching
- ✅ Scales from 1 to 1000+ datasets
- ✅ Works seamlessly with browser matrix (data × browsers)
- ✅ 100% backward compatible (opt-in per test)

#### Dynamic Browser Matrix ⭐ (Step 6)
- ✅ YAML-based matrix configuration (browsers.yaml:matrix)
- ✅ Collection-time parametrization via pytest_generate_tests hook
- ✅ Zero test code changes (same test runs on all browsers)
- ✅ Full browser isolation (each variant has separate instance)
- ✅ CLI override support (`--browser=profile_name`)
- ✅ Flexible profile dicts (different settings per browser)
- ✅ Backward compatible (legacy string parameters work)
- ✅ pytest-xdist ready (parallel execution support)
- ✅ Easy extension (add browser in YAML, tests auto-adapt)

#### Parallel Execution
- ✅ pytest-xdist compatible
- ✅ Isolated browser sessions
- ✅ Per-run report directories
- ✅ No global state
- ✅ **NEW: Browser matrix parametrization for linear scaling**

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
7. **Extensible Reporting** - Easy switching between Allure, Extent, Report Portal without code changes
8. **Dynamic Browser Matrix** ⭐ NEW - Automatic test parametrization across multiple browsers/versions with zero test code changes

**Total Components:**
- ✅ 1 browser matrix parametrization system (pytest_generate_tests hook, ConfigLoader.get_browser_matrix())
- ✅ 1 reporting abstraction module (Reporter, AllureReporter, ReportingManager)
- ✅ 3 pytest fixtures (driver, config, browser_profile)
- ✅ 5 pytest hooks (pytest_generate_tests, pytest_configure, pytest_runtest_makereport, setup_test_environment, etc.)
- ✅ 2 page object examples
- ✅ 2 test suites
- ✅ 5 locator types
- ✅ 8 core methods
- ✅ 100% integration with existing framework
