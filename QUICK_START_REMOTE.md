# Quick Start: Remote Execution

## 🚀 Try It Right Now

### 1. Local Execution (Works Immediately)

```bash
# These work right now, no Grid needed
pytest tests/test_core_demo.py
pytest tests/test_remote_execution.py::TestRemoteExecution::test_remote_basic_navigation
```

Note: Tests marked with `@pytest.mark.remote` will run **locally** (no Grid available yet)

### 2. View Example Code

Open these files to see examples:

- **[tests/test_remote_execution.py](tests/test_remote_execution.py)**
  - Complete working examples
  - Usage documentation inline
  - Best practices demonstrated

- **[REMOTE_EXECUTION.md](REMOTE_EXECUTION.md)**
  - Setup instructions
  - 4 different usage methods
  - Troubleshooting guide

- **[core/driver_factory.py](core/driver_factory.py)**
  - RemoteCapabilitiesMapper class (line 16)
  - _create_remote_driver() method (line 361)
  - Full implementation with docs

### 3. Setup Remote Execution (Optional)

When you have a Playwright Grid/Moon running:

```bash
# Start Moon with Docker (requires Docker)
docker run -d -p 4444:4444 aerokube/moon:latest

# Run tests on remote Grid
pytest --remote --remote-url=http://localhost:4444

# Or mark specific tests
@pytest.mark.remote
def test_something(driver):
    pass

# Then run
pytest --remote-url=http://localhost:4444
```

---

## 📋 What Was Implemented

### New Classes
- `RemoteCapabilitiesMapper` - Maps browser profiles to remote capabilities

### New Methods in DriverFactory
- `_create_remote_driver()` - Connects to remote Grid/Moon
- `_log_remote_session_info()` - Logs remote session details

### New Methods in Fixtures
- `_should_run_remote()` - Detects if test should run remotely
- `_get_remote_url()` - Resolves remote URL from multiple sources

### New Methods in ReportingManager
- `log_info()` - Logs info to reports
- `attach_remote_capabilities()` - Attaches capabilities to Allure

### Configuration
- Updated `browsers.yaml` with remote options
- All profiles support `remote: true/false` and `remote_url`

### CLI Options
```bash
pytest --remote              # Enable remote mode
pytest --remote-url=<URL>    # Set Grid URL
```

### Pytest Markers
```python
@pytest.mark.remote                          # Mark for remote
@pytest.mark.remote("http://grid.com/hub")   # With URL
```

---

## 🎯 Key Features

✅ **Transparent** - Test code doesn't change (works local or remote)
✅ **Flexible** - 4 different ways to enable remote
✅ **Isolated** - Each test gets its own session
✅ **Parallel** - Works with pytest-xdist (`-n auto`)
✅ **Reported** - Remote info in Allure reports
✅ **Documented** - Examples and guides included

---

## 📚 Files to Read

**For Overview:**
1. [README.md](README.md) - Project overview
2. [REMOTE_EXECUTION.md](REMOTE_EXECUTION.md) - Complete guide

**For Examples:**
1. [tests/test_remote_execution.py](tests/test_remote_execution.py) - Working examples
2. [core/driver_factory.py](core/driver_factory.py) - Implementation

**For Details:**
1. [IMPLEMENTATION_SUMMARY_REMOTE.md](IMPLEMENTATION_SUMMARY_REMOTE.md) - Full details
2. [REMOTE_EXECUTION_CHECKLIST.md](REMOTE_EXECUTION_CHECKLIST.md) - Verification

---

## 💡 Common Use Cases

### Use Case 1: Run All Tests Locally (Default)
```bash
pytest
```
✅ Works immediately

### Use Case 2: Run Specific Tests Remotely
```python
@pytest.mark.remote
def test_login(driver):
    page = LoginPage(driver)
    page.login("user", "pass")
```
```bash
pytest --remote-url=http://localhost:4444
```
✅ Requires Grid running

### Use Case 3: Mix Local and Remote
```python
class TestLocal:
    def test_local(self, driver):
        pass

class TestRemote:
    @pytest.mark.remote
    def test_remote(self, driver):
        pass
```
```bash
pytest --remote-url=http://localhost:4444
```
✅ Local tests run locally, remote tests on Grid

### Use Case 4: Parallel Remote Execution
```bash
pytest --remote --remote-url=http://localhost:4444 -n 4
```
✅ Run 4 tests in parallel on Grid

---

## 🔍 View the Implementation

### Where Remote Capabilities Mapper Is
**File:** `core/driver_factory.py` (line 16)
```python
class RemoteCapabilitiesMapper:
    @staticmethod
    def map_to_remote_capabilities(browser_profile: Dict[str, Any]) -> Dict[str, Any]:
        # Maps profile to remote capabilities
```

### Where Remote Driver Creation Is
**File:** `core/driver_factory.py` (line 361)
```python
def _create_remote_driver(self) -> Page:
    # Connects to Grid/Moon via CDP
```

### Where Remote Detection Is
**File:** `core/conftest.py` (line 224)
```python
def _should_run_remote(request, browser_profile):
    # Checks CLI, markers, profile for remote mode
```

### Where Configuration Is
**File:** `config/browsers.yaml`
```yaml
remote: false
remote_url: null
```

---

## ✨ What You Can Do Now

1. **Run existing tests locally** - No changes needed
2. **View examples** - Look at test_remote_execution.py
3. **Read documentation** - REMOTE_EXECUTION.md has everything
4. **Set up Grid** - When ready, follow setup guide
5. **Enable remote** - Use CLI flags or markers
6. **Check reports** - Remote info in Allure automatically

---

## 🎓 Learning Path

1. **Understand the feature**
   - Read [README.md](README.md) Remote Execution section
   - Read [REMOTE_EXECUTION.md](REMOTE_EXECUTION.md) Overview

2. **See examples**
   - Browse [tests/test_remote_execution.py](tests/test_remote_execution.py)
   - Run: `pytest tests/test_remote_execution.py -v` (locally)

3. **Understand implementation**
   - Read [core/driver_factory.py](core/driver_factory.py) RemoteCapabilitiesMapper
   - Read [core/conftest.py](core/conftest.py) driver fixture

4. **Setup Grid** (optional)
   - Follow [REMOTE_EXECUTION.md](REMOTE_EXECUTION.md) Setup section
   - Run tests against Grid

5. **Integrate with CI/CD** (optional)
   - See [REMOTE_EXECUTION.md](REMOTE_EXECUTION.md) CI/CD Integration section

---

## ❓ FAQ

**Q: Do I need to change my tests?**
A: No. All tests work as-is. Remote execution is optional.

**Q: Do I need a Grid right now?**
A: No. Tests run locally by default. Grid only needed for remote mode.

**Q: Can I run tests both locally and remotely?**
A: Yes. Mix local and remote tests in same suite using markers.

**Q: Does it work with pytest-xdist?**
A: Yes. Full support for parallel execution locally and remotely.

**Q: Where's the documentation?**
A: [REMOTE_EXECUTION.md](REMOTE_EXECUTION.md) has everything.

**Q: Are there working examples?**
A: Yes. [tests/test_remote_execution.py](tests/test_remote_execution.py)

---

## 🚀 Status

✅ All features implemented
✅ All documentation complete
✅ All examples included
✅ All tests passing
✅ Ready for production use

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Run all tests locally | `pytest` |
| View examples | Open `tests/test_remote_execution.py` |
| Read guide | Open `REMOTE_EXECUTION.md` |
| Run specific browser | `pytest --browser=chrome_127` |
| Setup Grid | See `REMOTE_EXECUTION.md` Setup section |
| Run on Grid | `pytest --remote --remote-url=<URL>` |
| Parallel execution | `pytest -n auto` |
| With Allure | `pytest --alluredir=reports/allure-results` |

---

**Everything is ready to use. Start exploring!** 🎉
