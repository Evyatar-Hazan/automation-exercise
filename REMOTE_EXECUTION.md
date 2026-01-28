# Remote Execution Guide (Playwright Grid / Moon)

This guide explains how to use Playwright remote execution (Grid/Moon) with the automation framework.

## Overview

The framework seamlessly supports both **local** and **remote** browser execution. Tests can run identically on local browsers or on a remote Playwright Grid/Moon service without any code changes.

### Key Benefits

- ✅ **Transparent** - Test code unchanged whether running local or remote
- ✅ **Flexible** - Multiple ways to enable remote: CLI, markers, config
- ✅ **Isolated** - Each test gets its own remote session
- ✅ **Parallel** - Compatible with pytest-xdist for parallel remote tests
- ✅ **Reported** - Remote capabilities logged and attached to Allure
- ✅ **Reliable** - Proper error handling and connection validation

## Architecture

```
Test Code (unchanged)
        ↓
    pytest Fixture (driver)
        ↓
    DriverFactory
    ├── Local Mode: Uses Playwright sync API
    └── Remote Mode: Uses CDP to connect to Grid/Moon
        ├── Connects to Grid at remote_url
        ├── Maps capabilities
        ├── Creates browser context
        └── Returns Page for test
        ↓
    Browser (Local or Remote)
```

## Setup

### 1. Install Playwright Grid or Moon

**Option A: Playwright Grid (Microsoft)**
```bash
# https://playwright.dev/docs/api/class-playwrighttesting
npm install -g @playwright/test
playwright api-test --serve
```

**Option B: Moon (Aerokube)**
```bash
# https://aerokube.com/moon/
# Download from: https://aerokube.com/moon/download/
./moon --address 0.0.0.0:4444 --grid-url http://localhost:4444
```

**Option C: Docker (Moon)**
```bash
docker run -d -p 4444:4444 --cap-add=SYS_ADMIN \
  -v /dev/shm:/dev/shm aerokube/moon:latest
```

### 2. Update Configuration (Optional)

Add remote browser profiles to `config/browsers.yaml`:

```yaml
matrix:
  # Local execution
  - name: chrome_127
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
    viewport:
      width: 1920
      height: 1080
    remote: false
    remote_url: null

  # Remote execution
  - name: chrome_127_remote
    browserName: "chromium"
    browserVersion: "127.0"
    headless: false
    viewport:
      width: 1920
      height: 1080
    remote: true
    remote_url: "https://moon.example.com/wd/hub"
```

### 3. Verify Grid is Running

```bash
# Test connection to Grid
curl -s http://localhost:4444/sessions | python -m json.tool
```

## Usage

### Method 1: CLI Flags (Global)

Run **all tests on remote Grid**:

```bash
# Basic
pytest --remote --remote-url=http://localhost:4444

# With specific browser
pytest --browser=chrome_127 --remote --remote-url=http://localhost:4444

# With parallel execution
pytest --remote --remote-url=http://localhost:4444 -n 4
```

### Method 2: Pytest Markers (Test-Level)

Mark **specific tests** to run remotely:

```python
# tests/test_login.py

@pytest.mark.remote
def test_login(driver):
    """This test runs remotely."""
    page = LoginPage(driver)
    page.login("user", "pass")
    assert page.is_logged_in()


def test_homepage(driver):
    """This test runs locally."""
    driver.goto("https://example.com")
    assert "Example" in driver.title
```

Run with:
```bash
pytest --remote-url=http://localhost:4444 tests/test_login.py
```

### Method 3: Markers with URL (Self-Contained)

Include remote URL in the marker:

```python
@pytest.mark.remote("http://localhost:4444")
def test_with_url(driver):
    """Remote URL is included in marker."""
    driver.goto("https://example.com")
    assert driver.url
```

Run without any CLI flags:
```bash
pytest tests/test_file.py
```

### Method 4: Browser Profile Config (Static)

Define remote in `browsers.yaml`:

```yaml
matrix:
  - name: chrome_remote
    browserName: "chromium"
    remote: true
    remote_url: "http://localhost:4444"
    ...
```

Run with:
```bash
pytest --browser=chrome_remote
```

## Capabilities Mapping

Browser profiles are automatically mapped to remote capabilities:

**Profile (YAML):**
```yaml
- name: chrome_127
  browserName: "chromium"
  browserVersion: "127.0"
  headless: false
  viewport:
    width: 1920
    height: 1080
```

**Mapped to Remote Capabilities:**
```json
{
  "browserName": "chromium",
  "browserVersion": "127.0",
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "platformName": "linux"
}
```

The mapping is handled by `RemoteCapabilitiesMapper` in `DriverFactory`.

## Examples

### Example 1: Run All Tests Remotely

```bash
# Start Moon (or your Grid)
docker run -d -p 4444:4444 aerokube/moon:latest

# Run tests
pytest --remote --remote-url=http://localhost:4444

# Output:
# test_core_demo.py::TestCoreFramework::test_driver_initialization[chrome_127] PASSED
# test_core_demo.py::TestCoreFramework::test_driver_initialization[firefox_latest] PASSED
# ...
```

### Example 2: Mix Local and Remote Tests

```python
# tests/test_mixed.py

class TestLocal:
    def test_local_browser(self, driver):
        """Runs on local browser."""
        driver.goto("https://example.com")
        assert driver.title

class TestRemote:
    @pytest.mark.remote
    def test_remote_browser(self, driver):
        """Runs on remote Grid."""
        driver.goto("https://example.com")
        assert driver.title
```

Run:
```bash
pytest --remote-url=http://localhost:4444
# Local tests run locally
# Remote tests run on Grid
```

### Example 3: Parallel Remote Execution

```bash
# Run 4 tests in parallel on remote Grid
pytest --remote --remote-url=http://localhost:4444 -n 4

# Run 8 tests in parallel (auto)
pytest --remote --remote-url=http://localhost:4444 -n auto
```

### Example 4: Remote with Specific Browser

```bash
# Create remote Firefox profile in browsers.yaml:
# - name: firefox_remote
#   browserName: "firefox"
#   remote: true
#   remote_url: "http://localhost:4444"

pytest --browser=firefox_remote
```

## Logging and Debugging

### View Remote Execution Logs

Logs are written to the console and to files in `logs/`:

```bash
# Check real-time logs
tail -f logs/*.log

# Look for these messages:
# "Remote execution enabled via --remote CLI flag"
# "Connecting to remote Grid/Moon at: http://localhost:4444"
# "Remote Session Info:"
```

### Check Allure Report

Remote session info is attached to Allure reports:

```bash
# Run tests with Allure results
pytest --remote --remote-url=http://localhost:4444 --alluredir=reports/allure-results

# Generate report
allure serve reports/allure-results

# In Allure: Check "Remote Session Info" attachment
```

### Enable Debug Logging

Set `log_level` to `DEBUG` in `config/config.yaml`:

```yaml
log_level: DEBUG
```

Or use environment variable:
```bash
export LOG_LEVEL=DEBUG
pytest --remote --remote-url=http://localhost:4444
```

## Common Issues

### Issue 1: Connection Refused

**Error:** `Failed to establish remote connection to http://localhost:4444`

**Solution:**
```bash
# Verify Grid is running
curl http://localhost:4444/sessions

# Check Grid logs
# Restart Grid if needed
```

### Issue 2: Capability Mismatch

**Error:** `No available capabilities that match the request`

**Solution:**
- Verify browser version is available in Grid
- Check Grid configuration supports the requested browser
- Try a different browserVersion (e.g., "latest" instead of specific version)

### Issue 3: Timeout on Remote Connection

**Error:** `Timeout establishing connection to remote Grid`

**Solution:**
```bash
# Check network connectivity
ping your-grid-host

# Verify remote_url is correct
# Increase timeout in config.yaml if needed
default_timeout: 30
```

### Issue 4: Tests Pass Locally but Fail Remotely

**Possible causes:**
- Different browser versions
- Viewport size differences
- Timezone or locale settings
- Network latency

**Solutions:**
- Use explicit waits instead of implicit
- Check viewport is properly set in browser profile
- Verify Grid browser capabilities match profile

## Performance Tips

1. **Reuse Grid Connection**: Tests in same session share browser context
2. **Parallel Execution**: Use pytest-xdist for faster remote execution
3. **Connection Pool**: Grid maintains connection pool - more workers = faster
4. **Viewport**: Match viewport to your target devices

```bash
# Fast parallel remote execution
pytest --remote --remote-url=http://localhost:4444 -n auto
```

## Best Practices

### ✅ DO

- ✅ Use CLI flags for CI/CD integration
- ✅ Use markers for test-specific remote needs
- ✅ Run parallel tests on remote Grid
- ✅ Monitor Grid logs during test execution
- ✅ Verify Grid is responsive before running tests
- ✅ Use explicit waits for better reliability
- ✅ Handle network timeouts gracefully

### ❌ DON'T

- ❌ Hardcode Grid URLs in test code (use config or markers)
- ❌ Share browser instances between tests
- ❌ Run too many parallel workers (tune for Grid capacity)
- ❌ Use relative timeouts - make them explicit
- ❌ Assume Grid behavior matches local Playwright exactly

## Advanced Configuration

### Custom Grid Parameters

Add grid-specific options to browser profile:

```yaml
- name: chrome_with_vnc
  browserName: "chromium"
  remote: true
  remote_url: "http://localhost:4444"
  remote_options:
    enableVNC: true
    enableVideo: false
    sessionTimeout: "5m"
```

### Environment-Specific Configuration

Create different browser profiles for each environment:

```yaml
# Production Grid
- name: chrome_prod
  browserName: "chromium"
  remote: true
  remote_url: "https://grid.prod.example.com/wd/hub"

# Staging Grid
- name: chrome_staging
  browserName: "chromium"
  remote: true
  remote_url: "http://grid.staging.example.com:4444"
```

Run with:
```bash
pytest --browser=chrome_prod     # Production
pytest --browser=chrome_staging  # Staging
```

### Multi-Grid Configuration

Use environment variables to switch Grids:

```python
# In conftest.py or config
import os

remote_url = os.getenv(
    'GRID_URL',
    'http://localhost:4444'
)
```

Run with:
```bash
GRID_URL=https://prod-grid.com pytest --remote --browser=chrome_127
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/remote-tests.yml
name: Remote Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      moon:
        image: aerokube/moon:latest
        ports:
          - 4444:4444

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      
      - name: Run remote tests
        run: pytest --remote --remote-url=http://localhost:4444 --alluredir=reports/allure-results
      
      - name: Publish Allure report
        uses: actions/upload-artifact@v2
        with:
          name: allure-report
          path: reports/allure-results
```

## Troubleshooting

### View Remote Session ID

Add this to your test:

```python
def test_with_session_id(driver):
    # Session ID is logged in DriverFactory
    driver.goto("https://example.com")
```

Check logs for:
```
Remote Session Info: {"session_id": "...", "browser_name": "chromium", ...}
```

### Test Report

Check Allure report for remote session info:
1. Open Allure report
2. Click on test
3. Check attachments section
4. Look for "Remote Capabilities" and "Remote Session Info"

## See Also

- [README.md](README.md) - Main project documentation
- [tests/test_remote_execution.py](tests/test_remote_execution.py) - Complete examples
- [core/driver_factory.py](core/driver_factory.py) - DriverFactory implementation
- [config/browsers.yaml](config/browsers.yaml) - Browser configuration
- [Playwright Grid Documentation](https://playwright.dev/docs/api/class-playwrighttesting)
- [Moon Documentation](https://aerokube.com/moon/)
