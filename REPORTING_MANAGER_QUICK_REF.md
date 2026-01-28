# 🎯 ReportingManager Quick Reference

## For Test Developers

### Basic Usage (No Changes Required)

Your tests work exactly as before - no imports or changes needed:

```python
from core.base_test import BaseTest
from pages.my_page import MyPage

class TestMyFeature(BaseTest):
    def test_something(self, driver):
        page = MyPage(driver)
        page.do_something()
        assert page.verify_result()
        # Reporting happens automatically ✅
```

Screenshots are attached to Allure reports automatically on failure.

---

## For Framework Developers

### Add Reporting from Custom Code

If you're building utilities, helpers, or custom page methods:

```python
from reporting.manager import ReportingManager

# Log a test step
ReportingManager.reporter().log_step("Custom action: Logging in")

# Attach a screenshot
ReportingManager.reporter().attach_screenshot(
    name="Login form",
    path="/path/to/screenshot.png"
)

# Attach debug info
ReportingManager.reporter().attach_text(
    name="Test Context",
    content="User: john.doe@example.com"
)

# Attach exception details
try:
    some_operation()
except Exception as e:
    ReportingManager.reporter().attach_exception(
        name="Operation Failed",
        exception=e
    )
```

### API Reference

```python
from reporting.manager import ReportingManager

# Initialize (done in pytest_configure automatically)
ReportingManager.init("allure")

# Get reporter instance
reporter = ReportingManager.reporter()

# Check if initialized
if ReportingManager.is_initialized():
    reporter.log_step("Ready")

# Reset (for testing)
ReportingManager.reset()
```

### Reporter Methods

```python
reporter = ReportingManager.reporter()

# Log a step
reporter.log_step(message: str) -> None
# Example: reporter.log_step("Click login button")

# Attach screenshot
reporter.attach_screenshot(name: str, path: str) -> None
# Example: reporter.attach_screenshot("Login page", "reports/login.png")

# Attach text
reporter.attach_text(name: str, content: str) -> None
# Example: reporter.attach_text("Log output", "Test logs here...")

# Attach exception
reporter.attach_exception(name: str, exception: Exception) -> None
# Example: reporter.attach_exception("Test error", exc)
```

---

## Architecture

### Reporting Module Structure

```
reporting/
├── __init__.py           # Exports ReportingManager
├── reporter.py           # Abstract interface (no Allure)
├── allure_reporter.py    # Allure implementation (ONLY place with allure imports)
└── manager.py            # Facade & singleton
```

### Key Properties

| Property | Value |
|----------|-------|
| Allure Imports | ✅ Only in `reporting/allure_reporter.py` |
| Test Changes | ❌ None required |
| Configuration | `config/config.yaml` → `reporter: "allure"` |
| Initialization | `core/conftest.py` → `pytest_configure` hook |

---

## Configuration

### Set Reporter Type

In `config/config.yaml`:

```yaml
# Reporting settings
reporter: "allure"  # Current: allure (Future: extent, report_portal)
```

The reporter type is read during pytest session startup and used to initialize ReportingManager.

---

## ✅ Rules

### ✅ DO

- ✅ Use `ReportingManager.reporter()` for custom reporting
- ✅ Call `reporter.log_step()` for major test actions
- ✅ Call `reporter.attach_screenshot()` for visual evidence
- ✅ Keep reporter initialization automatic (in conftest.py)

### ❌ DON'T

- ❌ Import `allure` directly (except in `reporting/allure_reporter.py`)
- ❌ Use `allure.attach()` or `allure.step()` in test code
- ❌ Modify reporter initialization in tests
- ❌ Hardcode reporter type in test code

---

## Examples

### Example 1: Custom Page Method with Reporting

```python
# pages/login_page.py
from reporting.manager import ReportingManager

class LoginPage(BasePage):
    LOGIN_BTN = [{'type': 'id', 'value': 'login-btn'}]
    
    def login_with_reporting(self, username: str, password: str):
        """Login and report to Allure"""
        reporter = ReportingManager.reporter()
        
        reporter.log_step(f"Login with user: {username}")
        self.type(self.USERNAME, username, "Username")
        
        reporter.log_step("Enter password")
        self.type(self.PASSWORD, password, "Password")
        
        reporter.log_step("Click login button")
        self.click(self.LOGIN_BTN, "Login Button")
```

### Example 2: Test with Custom Reporting

```python
# tests/test_login.py
from core.base_test import BaseTest
from reporting.manager import ReportingManager

class TestLogin(BaseTest):
    def test_successful_login(self, driver):
        page = LoginPage(driver)
        reporter = ReportingManager.reporter()
        
        reporter.log_step("Navigate to login page")
        page.navigate_to("https://example.com/login")
        
        reporter.log_step("Perform login")
        page.login_with_reporting("john@example.com", "password123")
        
        reporter.log_step("Verify successful login")
        assert page.is_logged_in()
        reporter.log_step("✓ Login successful")
```

### Example 3: Error Handling with Reporting

```python
# Custom test utility
def safe_screenshot(driver, name: str):
    """Take screenshot and attach to report"""
    try:
        path = f"reports/screenshots/{name}.png"
        driver.screenshot(path=path, full_page=True)
        
        if ReportingManager.is_initialized():
            ReportingManager.reporter().attach_screenshot(name, path)
        
        return path
    except Exception as e:
        if ReportingManager.is_initialized():
            ReportingManager.reporter().attach_exception(
                "Screenshot failed",
                e
            )
        raise
```

---

## Troubleshooting

### Issue: "ReportingManager not initialized"

**Cause**: `ReportingManager.reporter()` called before `pytest_configure`

**Solution**: Wrap in check:
```python
if ReportingManager.is_initialized():
    ReportingManager.reporter().log_step("Test action")
```

### Issue: Screenshots not appearing in Allure report

**Cause**: File path doesn't exist

**Solution**: Ensure path is correct and file exists:
```python
from pathlib import Path

path = Path("reports/screenshot.png")
if path.exists():
    ReportingManager.reporter().attach_screenshot("Screenshot", str(path))
```

### Issue: "allure-pytest package not found"

**Cause**: Allure not installed

**Solution**: Install requirements:
```bash
pip install -r requirements.txt
```

---

## Design Patterns

- **Abstract Factory**: Reporter interface with concrete implementations
- **Facade**: ReportingManager hides reporting complexity
- **Singleton**: Single reporter instance per session
- **Dependency Inversion**: Code depends on Reporter interface, not concrete class

---

## Future Extensions

When adding a new reporter (e.g., Extent Reports):

1. Create `reporting/extent_reporter.py` implementing Reporter interface
2. Add case to `ReportingManager.init()`
3. Update `config.yaml`: `reporter: "extent"`
4. ✅ All tests work without changes!

```python
# reporting/extent_reporter.py
from reporting.reporter import Reporter

class ExtentReporter(Reporter):
    def __init__(self):
        import extent_api
        self.extent = extent_api
    
    def log_step(self, message: str) -> None:
        self.extent.log(message)
    
    # ... implement other methods
```

That's it! 🚀

---

## Summary

| Feature | Status |
|---------|--------|
| Allure Integration | ✅ Working |
| Extensible Design | ✅ Ready |
| Test Changes | ❌ None required |
| Code Quality | ✅ Production-ready |
| Type Hints | ✅ Complete |
| Documentation | ✅ Comprehensive |
