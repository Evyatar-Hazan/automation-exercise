# Locator Strategy - Multi-Locator Fallback Mechanism

## Overview

The Locator Strategy provides a robust element identification system with automatic fallback support. Each UI element can have multiple locators (XPath, CSS, etc.) that are tried sequentially until one succeeds.

## Key Features

- **Multiple Locators Per Element**: Define 2+ locators for each element
- **Automatic Fallback**: Tries locators sequentially until one works
- **Detailed Logging**: Logs each attempt and which locator succeeded
- **Screenshot on Total Failure**: Captures screenshot when all locators fail
- **Test Transparency**: Tests remain unaware of which locator succeeded
- **Playwright Integration**: Full support for Playwright Page objects

## Architecture

```
┌─────────────┐
│   Test      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  BasePage   │ ← Uses LocatorUtility
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ LocatorUtility│ ← Handles fallback logic
└──────────────┘
```

## Usage

### 1. Define Locators with Fallback

```python
# In page object
SEARCH_INPUT = [
    {'type': 'xpath', 'value': '//input[@id="search"]'},
    {'type': 'css', 'value': '#search'},
    {'type': 'css', 'value': 'input.search-field'}
]
```

### 2. Use in Page Objects

```python
from core.base_page import BasePage

class HomePage(BasePage):
    SEARCH_BUTTON = [
        {'type': 'xpath', 'value': '//button[@id="search-btn"]'},
        {'type': 'css', 'value': '#search-btn'}
    ]
    
    def click_search(self):
        self.click(self.SEARCH_BUTTON, "Search Button")
```

### 3. Use in Tests

```python
from core.base_test import BaseTest

class TestSearch(BaseTest):
    def test_search_functionality(self, driver):
        page = HomePage(driver)
        page.click_search()  # Automatic fallback handled
```

## Locator Types Supported

| Type   | Example                                    |
|--------|--------------------------------------------|
| xpath  | `{'type': 'xpath', 'value': '//button'}`   |
| css    | `{'type': 'css', 'value': '#submit'}`      |
| id     | `{'type': 'id', 'value': 'submit-btn'}`    |
| text   | `{'type': 'text', 'value': 'Submit'}`      |
| role   | `{'type': 'role', 'value': 'button'}`      |

## How It Works

### Fallback Flow

```
Element with locators: [Locator1, Locator2, Locator3]

1. Try Locator1 → FAIL → Log failure
2. Try Locator2 → FAIL → Log failure  
3. Try Locator3 → SUCCESS → Log success, return element

Test continues, unaware which locator worked
```

### When All Fail

```
1. Try all locators → All FAIL
2. Log comprehensive error with all attempts
3. Capture screenshot (via BaseTest)
4. Raise exception with detailed message
```

## Log Output Examples

### Successful Fallback
```
[DEBUG] Search Input [Locator 1/2]: Attempting XPATH: //input[@id="wrong_id"]
[DEBUG] Search Input [Locator 1/2]: ✗ FAILED - Element not visible within timeout
[DEBUG] Search Input [Locator 2/2]: Attempting CSS: #filter_keyword
[INFO]  Search Input [Locator 2/2]: ✓ SUCCESS with CSS: #filter_keyword
```

### All Locators Fail
```
[DEBUG] Submit Button [Locator 1/3]: Attempting XPATH: //button[@id="btn1"]
[DEBUG] Submit Button [Locator 1/3]: ✗ FAILED - Element not visible
[DEBUG] Submit Button [Locator 2/3]: Attempting CSS: #btn2
[DEBUG] Submit Button [Locator 2/3]: ✗ FAILED - Element not visible
[DEBUG] Submit Button [Locator 3/3]: Attempting CSS: .btn3
[DEBUG] Submit Button [Locator 3/3]: ✗ FAILED - Element not visible
[ERROR] Submit Button: All 3 locator(s) failed:
  1. XPATH: //button[@id="btn1"] - Element not visible
  2. CSS: #btn2 - Element not visible
  3. CSS: .btn3 - Element not visible
```

## API Reference

### BasePage Methods

#### `click(locators, element_name)`
Click element with fallback.

```python
self.click(
    [{'type': 'xpath', 'value': '//button[@id="submit"]'},
     {'type': 'css', 'value': '#submit'}],
    "Submit Button"
)
```

#### `type(locators, text, element_name, clear_first=True)`
Type text with fallback.

```python
self.type(
    [{'type': 'css', 'value': '#email'}],
    "test@example.com",
    "Email Field"
)
```

#### `get_text(locators, element_name)`
Get element text with fallback.

```python
text = self.get_text(
    [{'type': 'css', 'value': '.message'}],
    "Success Message"
)
```

#### `is_visible(locators, element_name)`
Check visibility with fallback.

```python
is_shown = self.is_visible(
    [{'type': 'css', 'value': '#dialog'}],
    "Dialog Box"
)
```

#### `find_element(locators, element_name)`
Get Playwright Locator for custom operations.

```python
element = self.find_element(
    [{'type': 'css', 'value': '#custom'}],
    "Custom Element"
)
element.hover()
```

## Integration with Existing Framework

### DriverFactory
- LocatorUtility accepts Playwright Page from driver fixture
- Fully compatible with browser configuration

### BaseTest
- Screenshots captured automatically on failure
- Works with existing test fixtures
- Supports parallel execution

### ConfigLoader
- Uses `element_timeout` from config.yaml
- Inherits all framework settings

## Best Practices

1. **Order Locators by Stability**
   ```python
   # More specific → Less specific
   [{'type': 'id', 'value': 'submit'},
    {'type': 'css', 'value': 'button.submit'},
    {'type': 'xpath', 'value': '//button[text()="Submit"]'}]
   ```

2. **Meaningful Element Names**
   ```python
   # Good
   self.click(locators, "Login Button")
   
   # Bad
   self.click(locators, "Element")
   ```

3. **Page Object Pattern**
   ```python
   # Encapsulate locators in page objects
   class LoginPage(BasePage):
       EMAIL_INPUT = [...]
       
       def enter_email(self, email):
           self.type(self.EMAIL_INPUT, email, "Email Input")
   ```

4. **Avoid Over-Definition**
   ```python
   # Don't define 10 locators for one element
   # 2-3 fallback locators is optimal
   ```

## Running Tests

```bash
# Run locator demo tests
pytest tests/test_locator_demo.py -v

# Run with detailed logs
pytest tests/test_locator_demo.py -v -s

# Run specific test
pytest tests/test_locator_demo.py::TestLocatorFallbackDemo::test_fallback_with_intentional_bad_locator -v
```

## Troubleshooting

### Issue: All Locators Failing
- Check element visibility/timing
- Verify locator syntax
- Increase timeout in config.yaml
- Check logs for specific error messages

### Issue: Wrong Locator Succeeding
- Review locator specificity
- Ensure first locator is most stable
- Check for duplicate elements on page

### Issue: Slow Execution
- Reduce number of fallback locators
- Optimize timeout values
- Use more specific locators first

## Configuration

```yaml
# config/config.yaml
element_timeout: 5  # Timeout for each locator attempt (seconds)
screenshot_on_failure: true  # Capture screenshot when all locators fail
```

## Example: Complete Test Flow

```python
# pages/login_page.py
from core.base_page import BasePage

class LoginPage(BasePage):
    EMAIL_INPUT = [
        {'type': 'xpath', 'value': '//input[@name="email"]'},
        {'type': 'css', 'value': '#email'}
    ]
    
    PASSWORD_INPUT = [
        {'type': 'css', 'value': '#password'},
        {'type': 'xpath', 'value': '//input[@type="password"]'}
    ]
    
    LOGIN_BUTTON = [
        {'type': 'css', 'value': 'button[type="submit"]'},
        {'type': 'text', 'value': 'Login'}
    ]
    
    def login(self, email, password):
        self.type(self.EMAIL_INPUT, email, "Email")
        self.type(self.PASSWORD_INPUT, password, "Password")
        self.click(self.LOGIN_BUTTON, "Login Button")

# tests/test_login.py
from core.base_test import BaseTest
from pages.login_page import LoginPage

class TestLogin(BaseTest):
    def test_successful_login(self, driver):
        driver.goto("https://example.com/login")
        page = LoginPage(driver)
        
        page.login("user@example.com", "password123")
        
        assert "dashboard" in driver.url
```

## Benefits

✓ **Resilient Tests**: Tests don't break when locators change  
✓ **Easy Debugging**: Logs show exactly which locator failed/succeeded  
✓ **Clean Test Code**: Tests unaware of fallback complexity  
✓ **Reduced Maintenance**: Update locators without changing test logic  
✓ **Production Ready**: Integrated with existing framework components
