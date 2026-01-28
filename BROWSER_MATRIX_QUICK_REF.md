# Browser Matrix - Quick Reference

## TL;DR

Add browsers to `config/browsers.yaml:matrix`, tests automatically run on all of them.

```yaml
# config/browsers.yaml
matrix:
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
    viewport: {width: 1920, height: 1080}
```

Tests automatically parametrize:
```python
def test_login(self, driver):
    """Automatically runs: test_login[chrome_127], test_login[chrome_latest], ..."""
```

## Common Commands

```bash
# Run all browsers
pytest tests/

# Run specific browser
pytest --browser=chrome_127 tests/

# Parallel execution
pytest -n auto tests/

# Verbose (see browser parametrization)
pytest -v tests/

# Collect only (see which tests will run)
pytest --collect-only tests/
```

## Writing Tests

### ✅ DO (Browser-agnostic)
```python
from core.base_test import BaseTest

class TestMyFeature(BaseTest):
    def test_login(self, driver):
        """Automatically runs on all browsers"""
        driver.goto("https://example.com")
        # ... test code ...
```

### ❌ DON'T (Hardcoded browser logic)
```python
def test_login(self, driver):
    if browser == "chrome":
        driver.goto("https://example.com")
    else:
        driver.goto("https://example.com/firefox")  # ❌ NO!
```

## Adding New Browser

1. Edit `config/browsers.yaml`
2. Add to `matrix:` section:

```yaml
matrix:
  # ... existing browsers ...
  - name: webkit_latest
    browserName: "webkit"
    browserVersion: "latest"
    headless: false
```

3. **Done!** All tests automatically run on new browser

## Using Page Objects

```python
from pages.store_page import StorePage

def test_search(self, driver):
    """Works with Page Object Model"""
    page = StorePage(driver)
    page.navigate()
    page.search("laptop")
    assert page.results_visible()
```

## Configuration Access

```python
def test_feature(self, driver):
    # Get config values
    base_url = self.config_loader.get('base_url')
    browser_name = self.config_loader.get('browser_name')
```

## Accessing Browser Profile Info

```python
def test_with_profile_info(self, browser_profile):
    """Access current browser profile"""
    profile_name = browser_profile.get('name')  # e.g., 'chrome_127'
    browser_type = browser_profile.get('browserName')  # e.g., 'chromium'
```

## Standalone Tests (No Driver)

```python
def test_config():
    """NOT parametrized (no driver fixture)"""
    config = ConfigLoader()
    base_url = config.get('base_url')
    assert base_url is not None
```

## Debug: Which Browser is Running?

```bash
# Verbose output shows browser
pytest -v tests/test_login.py

# Output:
# test_login[chrome_127] PASSED
# test_login[firefox_latest] PASSED
```

## Debug: Check Available Browsers

```bash
grep "name:" config/browsers.yaml
```

## Debug: Collect Tests to See Parametrization

```bash
pytest --collect-only tests/test_login.py
```

## Fallback: Run Single Browser

```bash
pytest --browser=chrome_127 tests/
```

## Key Concepts

| Concept | Explanation |
|---------|-------------|
| **matrix** | List of browser profiles in `browsers.yaml` |
| **profile** | Dict with name, browserName, version, etc. |
| **browser_profile fixture** | Receives profile from parametrization |
| **driver fixture** | Creates isolated browser for each test |
| **pytest_generate_tests** | Parametrizes tests at collection time |
| **--browser** | CLI flag to filter matrix |

## Migration from Old Pattern

### Old Way (❌ Not Recommended)
```python
@pytest.mark.browser("firefox_latest")
def test_feature(self, driver):
    """Only runs on Firefox"""
```

### New Way (✅ Automatic)
```python
def test_feature(self, driver):
    """Automatically runs on all browsers in matrix"""
```

Override:
```bash
pytest --browser=firefox_latest tests/
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests not parametrized | Add `driver` parameter to test |
| `--browser` not working | Check exact browser name in `browsers.yaml` |
| Need specific browser | Use `pytest --browser=chrome_127` |
| Browser not found | Add to `matrix:` section in `browsers.yaml` |

## Architecture in One Picture

```
YAML Matrix → pytest_generate_tests() → Test Parametrization → Isolated Drivers
  (data)           (collection hook)         (test variants)      (execution)
```

## Performance

- **Collection:** ~0.01s (cached matrix)
- **Per Test:** Negligible (driver lifecycle same)
- **Parallel:** Linear scaling with `-n auto`

## Files to Know

| File | Purpose |
|------|---------|
| `config/browsers.yaml` | Browser profile definitions |
| `config/config_loader.py` | Loads matrix from YAML |
| `core/driver_factory.py` | Creates isolated browsers |
| `core/conftest.py` | pytest_generate_tests hook |
| `core/base_test.py` | Base test class |

## One More Thing

Every test that requests the `driver` fixture automatically runs on all browsers in the matrix. **Zero test code changes required.**

Change the matrix → tests automatically adapt. 🎉

---

For detailed guide, see: `BROWSER_MATRIX_GUIDE.md`
