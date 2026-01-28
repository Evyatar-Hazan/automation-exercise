# Browser Matrix Implementation Guide

## Overview

This automation framework now supports a **dynamic browser matrix** that allows tests to run across multiple browsers and versions automatically. The browser matrix is defined in YAML configuration and applied at pytest collection time, enabling:

- ✅ Running the same tests across multiple browsers
- ✅ Testing multiple versions of the same browser
- ✅ Parallel execution with `pytest-xdist` (fully isolated sessions)
- ✅ Zero changes required in test code
- ✅ Full backward compatibility with legacy patterns

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    pytest Collection                        │
│  pytest_generate_tests() hook loads matrix from YAML        │
│  Parametrizes all tests that use 'driver' fixture           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              browser_profile Parameter                       │
│  Each test receives one profile dict from the matrix         │
│  Profile contains: name, browserName, version, headless...  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               driver Fixture                                │
│  Creates isolated browser context for each test             │
│  Uses browser_profile to configure DriverFactory            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DriverFactory                                  │
│  Accepts browser profile dict (not just name)               │
│  Creates isolated Playwright browser instance               │
│  Full cleanup after each test                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration: browsers.yaml

### Matrix Definition

Define browser profiles in `config/browsers.yaml` under the `matrix` section:

```yaml
matrix:
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    platformName: "linux"
    headless: false
    viewport:
      width: 1920
      height: 1080
    args:
      - "--start-maximized"
      - "--disable-blink-features=AutomationControlled"

  - name: chrome_latest
    browserName: "chromium"
    browserVersion: "latest"
    platformName: "linux"
    headless: false
    viewport:
      width: 1920
      height: 1080

  - name: firefox_latest
    browserName: "firefox"
    browserVersion: "latest"
    platformName: "linux"
    headless: false
    viewport:
      width: 1920
      height: 1080
```

**Key Points:**
- `name`: Unique identifier for this profile (used in test parametrization)
- `browserName`: Playwright browser type (`chromium`, `firefox`, `webkit`)
- `browserVersion`: Version string (e.g., `"127.0"`, `"latest"`)
- `headless`: Boolean (defaults to false for visibility)
- `viewport`: Optional viewport configuration
- `args`: Optional browser launch arguments
- All other Playwright-compatible options are supported

### Adding a New Browser Profile

Simply add a new entry to the `matrix` section:

```yaml
matrix:
  # ... existing profiles ...
  
  - name: webkit_latest
    browserName: "webkit"
    browserVersion: "latest"
    platformName: "mac"
    headless: false
    viewport:
      width: 1440
      height: 900
```

After this change, **all tests automatically run on the new browser profile** without code changes.

## Test Implementation

### Basic Test (Browser Matrix Applied Automatically)

```python
from core.base_test import BaseTest

class TestMyFeature(BaseTest):
    def test_login(self, driver):
        """
        This test runs automatically on ALL browsers in the matrix.
        
        With 3 browsers in matrix, this becomes:
        - test_login[chrome_127]
        - test_login[chrome_latest]
        - test_login[firefox_latest]
        """
        driver.goto("https://example.com/login")
        driver.fill("#username", "testuser")
        driver.fill("#password", "password123")
        driver.click("#submit")
        
        assert "Dashboard" in driver.page_title()
```

### Using Page Object Model

```python
from core.base_test import BaseTest
from pages.login_page import LoginPage

class TestAuthentication(BaseTest):
    def test_successful_login(self, driver):
        """Automatically runs on all browsers in matrix."""
        login_page = LoginPage(driver)
        login_page.navigate()
        login_page.login("testuser", "password123")
        
        assert login_page.is_dashboard_visible()
```

### Non-Browser Tests (Not Affected by Matrix)

```python
def test_config_loading():
    """
    This test does NOT use the driver fixture.
    It will NOT be parametrized with the browser matrix.
    It runs only once.
    """
    config_loader = ConfigLoader()
    base_url = config_loader.get('base_url')
    
    assert base_url is not None
```

## Running Tests

### Run All Tests (All Browsers in Matrix)

```bash
pytest tests/

# Output example:
# test_login[chrome_127] PASSED
# test_login[chrome_latest] PASSED
# test_login[firefox_latest] PASSED
# test_signup[chrome_127] PASSED
# ...
```

### Run with Specific Browser

```bash
pytest --browser=chrome_127 tests/

# Only runs tests on chrome_127
# test_login[chrome_127] PASSED
# test_signup[chrome_127] PASSED
# ...
```

### Parallel Execution

```bash
# Requires pytest-xdist: pip install pytest-xdist
pytest -n auto tests/

# Launches parallel workers
# Each worker gets isolated browser sessions
# No state sharing between workers
```

### Verbose Output (See Browser Info)

```bash
pytest -v tests/

# Shows browser matrix parametrization:
# test_login[chrome_127] PASSED
# test_login[chrome_latest] PASSED
# test_login[firefox_latest] PASSED
```

## ConfigLoader API

### Load Browser Matrix

```python
from config.config_loader import ConfigLoader

loader = ConfigLoader()

# Get all browser profiles from matrix
profiles = loader.get_browser_matrix()
# Returns: [
#   {'name': 'chrome_127', 'browserName': 'chromium', ...},
#   {'name': 'chrome_latest', 'browserName': 'chromium', ...},
#   ...
# ]

# Get single browser config by name (legacy support)
profile = loader.get_browser_config('chrome_127')
# Returns: {'browserName': 'chromium', 'browserVersion': '127.0', ...}
```

## DriverFactory API

### Create Driver with Profile Dictionary

```python
from core.driver_factory import DriverFactory

# Using profile dictionary (preferred)
profile = {'name': 'chrome_127', 'browserName': 'chromium', ...}
factory = DriverFactory(browser_profile=profile)
driver = factory.get_driver()

# Using profile name (backward compatible)
factory = DriverFactory(browser_profile='chrome_127')
driver = factory.get_driver()

# Using default browser
factory = DriverFactory()
driver = factory.get_driver()
```

## Advanced: How pytest_generate_tests Works

The magic happens in the `pytest_generate_tests()` hook in `core/conftest.py`:

1. **Collection Time**: pytest calls `pytest_generate_tests()` for each test
2. **Matrix Loading**: Hook loads `get_browser_matrix()` from ConfigLoader
3. **CLI Override Check**: If `--browser` specified, filters matrix
4. **Parametrization**: Calls `metafunc.parametrize()` with matrix profiles
5. **Test Expansion**: One test becomes N tests (N = matrix size)

```python
def pytest_generate_tests(metafunc):
    """
    Called during test collection for each test function.
    Only parametrizes tests that use 'browser_profile' fixture.
    """
    if 'browser_profile' not in metafunc.fixturenames:
        return  # Not a browser test, skip
    
    # Load matrix from YAML
    matrix = config_loader.get_browser_matrix()
    
    # Apply --browser CLI override if specified
    if browser_override:
        matrix = [p for p in matrix if p['name'] == browser_override]
    
    # Parametrize test with each profile
    profile_ids = [p['name'] for p in matrix]
    metafunc.parametrize('browser_profile', matrix, ids=profile_ids)
```

## Backward Compatibility

### Legacy Browser Names Still Work

```python
# Old way (still works)
factory = DriverFactory(browser_name='chrome_127')

# New way (recommended)
factory = DriverFactory(browser_profile='chrome_127')

# New way with dict
factory = DriverFactory(browser_profile={...})
```

### Legacy browsers.yaml Section Supported

If your YAML has a legacy `browsers:` section without `matrix:`, the framework automatically converts it:

```yaml
# Legacy format (still supported)
browsers:
  chrome_127:
    browserName: "chromium"
    browserVersion: "127.0"
    ...
  firefox_latest:
    browserName: "firefox"
    ...

# Is automatically converted to matrix format internally
```

## Isolation & Safety

### Each Test Gets Fresh Browser

```
┌─ Test 1 ──────────┐    ┌─ Test 2 ──────────┐    ┌─ Test 3 ──────────┐
│  Browser 1        │    │  Browser 1        │    │  Browser 1        │
│  Context 1        │    │  Context 2        │    │  Context 3        │
│  Page 1           │    │  Page 2           │    │  Page 3           │
│  (Closed after)   │    │  (Closed after)   │    │  (Closed after)   │
└───────────────────┘    └───────────────────┘    └───────────────────┘
```

### Parallel Execution Safety

- Each pytest worker gets isolated browser sessions
- No shared browser instances
- No race conditions in reporting
- Screenshot capture includes browser profile name
- Reports organized per-run timestamp

## Reporting & Screenshots

### Screenshot Filenames

Screenshots are captured with browser context:

```
/reports/20260128_163453/
├── chrome_127_test_login_20260128_163500.png
├── firefox_latest_test_login_20260128_163502.png
└── ...
```

### Logs

Logs show browser matrix information:

```
2026-01-28 16:47:54.357 | INFO | config.config_loader:get_browser_matrix:259 
  - Loaded browser matrix with 3 profiles

2026-01-28 16:47:54.357 | INFO | core.conftest:pytest_generate_tests:85 
  - Loaded browser matrix with 3 profiles: ['chrome_127', 'chrome_latest', 'firefox_latest']

2026-01-28 16:47:54.359 | DEBUG | core.conftest:pytest_generate_tests:126 
  - Parametrized test_driver_initialization with 3 browser profiles
```

## Troubleshooting

### Tests Not Parametrized

**Problem:** Tests show `test_name` instead of `test_name[browser_name]`

**Solution:** Ensure test method has `driver` parameter:
```python
def test_something(self, driver):  # ✓ Will be parametrized
def test_something(self):          # ✗ Will NOT be parametrized
```

### Browser Profile Not Found

**Problem:** Error "Browser profile 'chrome_xyz' not found in matrix"

**Solution:** Check `config/browsers.yaml`:
```bash
grep "chrome_xyz" config/browsers.yaml  # Should show profile name
```

### CLI Override Not Working

**Problem:** `pytest --browser=chrome_127` still runs all browsers

**Solution:** Ensure browser name exactly matches matrix entry:
```yaml
matrix:
  - name: chrome_127  # Must match exactly
```

## Migration Guide: From Old Pattern

### Old Way (No Longer Recommended)

```python
@pytest.mark.browser("firefox_latest")
def test_login(self, driver):
    """Only runs on Firefox."""
```

### New Way (Automatic for All Browsers)

```python
def test_login(self, driver):
    """Automatically runs on all browsers in matrix."""
```

To run on specific browser:
```bash
pytest --browser=firefox_latest tests/test_file.py
```

## Best Practices

✅ **DO:**
- Add tests using `driver` fixture (automatically matrix-enabled)
- Define browser profiles in `config/browsers.yaml:matrix`
- Use `--browser` CLI arg to filter during development
- Use Page Object Model for maintainability

❌ **DON'T:**
- Hardcode browser names in tests
- Use conditional logic like `if browser == "chrome"`
- Create manual loops over browsers
- Share browser instances between tests

## Example: Multi-Browser Test Suite

```python
# config/browsers.yaml
matrix:
  - name: chrome_stable
    browserName: "chromium"
    browserVersion: "latest"
    headless: false
  
  - name: firefox_latest
    browserName: "firefox"
    browserVersion: "latest"
    headless: true
  
  - name: webkit_latest
    browserName: "webkit"
    browserVersion: "latest"
    headless: false

---

# tests/test_checkout.py
from core.base_test import BaseTest
from pages.store_page import StorePage
from pages.checkout_page import CheckoutPage

class TestCheckout(BaseTest):
    def test_add_to_cart(self, driver):
        """Runs on: chrome_stable, firefox_latest, webkit_latest"""
        page = StorePage(driver)
        page.navigate()
        page.search("shoes")
        page.select_first_result()
        page.add_to_cart()
        
        assert page.cart_count() == 1
    
    def test_checkout_flow(self, driver):
        """Runs on: chrome_stable, firefox_latest, webkit_latest"""
        page = StorePage(driver)
        page.navigate()
        page.add_sample_item()
        
        checkout = CheckoutPage(driver)
        checkout.proceed_to_checkout()
        checkout.fill_shipping("123 Main St")
        checkout.select_payment("credit_card")
        checkout.submit_order()
        
        assert checkout.is_confirmation_visible()

# Running: pytest tests/test_checkout.py
# Result:
#   test_add_to_cart[chrome_stable] PASSED
#   test_add_to_cart[firefox_latest] PASSED
#   test_add_to_cart[webkit_latest] PASSED
#   test_checkout_flow[chrome_stable] PASSED
#   test_checkout_flow[firefox_latest] PASSED
#   test_checkout_flow[webkit_latest] PASSED
```

## Summary

The browser matrix implementation provides a clean, YAML-driven approach to multi-browser testing:

1. **Define once** in `config/browsers.yaml:matrix`
2. **Tests parametrize automatically** at collection time
3. **Zero test code changes** needed
4. **Full isolation** between browser sessions
5. **Parallel execution** ready with `pytest-xdist`
6. **Backward compatible** with existing patterns

Your tests are now browser-agnostic and configuration-driven! 🎉
