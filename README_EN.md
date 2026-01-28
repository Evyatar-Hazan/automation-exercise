# Automation Framework Exercise

A robust, scalable test automation framework built with **Python**, **Playwright**, and **Pytest**. Designed for stability, flexibility, and ease of maintenance using the Page Object Model (POM) design pattern.

> [!NOTE]
> **Requirements Status**: ✅ **100% Implemented**. This project meets all specified requirements including Playwright, Python, Allure Reports, Selenium Grid/Moon support, OOP/POM design, Data-Driven Testing, and parallel execution.

## 🚀 Key Features

*   **Modern Tech Stack**: Python 3.10+, Playwright, Pytest.
*   **Page Object Model (POM)**: Modular and reusable components.
*   **Dynamic Browser Matrix**: Run tests across multiple browsers (Chrome, Firefox, Edge, WebKit) and versions (latest, specific) without changing test code.
*   **Data-Driven Testing**: Externalize test data supports YAML, JSON, and CSV formats.
*   **Remote Execution**: Seamless support for Selenium Grid, Moon, or Dockerized execution via CDP.
*   **Parallel Execution**: Fast execution using `pytest-xdist`.
*   **Robust Reporting**: Integrated **Allure Reports** with screenshots, logs, and failure analysis.
*   **Smart Locators**: Advanced locator strategy with multiple fallback mechanisms.
*   **Configuration Management**: Centralized configuration using YAML.

## 🏗️ Project Structure

```
automation-exercise/
├── config/                 # Configuration files
│   ├── config.yaml         # Main settings (Base URL, timeouts)
│   ├── browsers.yaml       # Browser matrix definition
│   └── reporting.yaml      # Reporting config
├── core/                   # Core framework logic
│   ├── driver_factory.py   # Browser creation & remote connection
│   ├── base_page.py        # Base POM class
│   └── locator_strategy.py # Smart locator fallback logic
├── pages/                  # Page Objects (POM)
├── tests/                  # Test scripts
├── test_data/              # Data files for data-driven testing
│   ├── login.yaml          # YAML examples
│   ├── users.csv           # CSV examples
│   └── search.json         # JSON examples
├── utils/                  # Utilities (DataLoader, etc.)
├── reporting/              # Reporting abstraction layer
├── reports/                # Test Execution Reports (Timestamped)
├── logs/                   # Execution logs
├── conftest.py             # Pytest fixtures and hooks
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Project dependencies
```

## 🌐 Browser Matrix & Architecture

The framework uses a **dynamic browser matrix** defined in `config/browsers.yaml`. Tests are automatically prioritized at collection time to run across all configured browsers.

### Architecture
```
YAML Matrix (browsers.yaml) → pytest_generate_tests() → Test Parametrization → Isolated Drivers
```

### Configuration (`config/browsers.yaml`)
```yaml
matrix:
  - name: chrome_latest
    browserName: chromium
    browserVersion: latest
    headless: false

  - name: firefox_latest
    browserName: firefox
    browserVersion: latest
```

## ☁️ Remote Execution (Grid / Moon)

Run tests seamlessly on local browsers or remote grids (Selenium Grid 4, Moon, BrowserStack, etc.).

### Architecture
The `DriverFactory` automatically maps browser profiles to W3C capabilities and connects via CDP or WebDriver API.

### Usage
**Method 1: CLI Flags**
```bash
pytest --remote --remote-url="http://localhost:4444/wd/hub"
```

**Method 2: Configuration**
Set `remote: true` in `config/browsers.yaml` profiles.

### Docker Setup (Example)
Run Moon (Lightweight Selenium Grid):
```bash
docker run -d -p 4444:4444 aerokube/moon:latest
```

## 💾 Data-Driven Testing

Separates test logic from data. Supports **YAML**, **JSON**, and **CSV**.

### Usage Example
```python
from utils.data_loader import load_test_data

@pytest.mark.parametrize("data", load_test_data("test_data/login.yaml"))
def test_login(driver, data):
    page.login(data["username"], data["password"])
    assert page.is_logged_in()
```

### file Formats
*   **YAML**: Recommended for structured data.
*   **JSON**: Good for complex hierarchical data.
*   **CSV**: Best for large datasets (headers become keys).

## 🎯 Smart Locators (Multi-Locator Strategy)

The framework uses a robust fallback mechanism for element identification. Define multiple locators for each element; if one fails, the next is tried automatically.

### Usage
```python
# In Page Object
SEARCH_INPUT = [
    {'type': 'id', 'value': 'search_query_top'},          # 1. Try ID
    {'type': 'css', 'value': '#search_query_top'},        # 2. Try CSS
    {'type': 'xpath', 'value': '//input[@name="search"]'} # 3. Try XPath
]

# In Test/Page Method
self.type(self.SEARCH_INPUT, "Laptop", "Search Field")
```
*   **Automatic Fallback**: Sequentially tries locators.
*   **Logging**: Records which locator succeeded/failed.
*   **Failure**: Captures screenshot if all locators fail.

## 📋 Prerequisites

*   **Python 3.10+** installed.
*   **Java (JDK 8+)**: Required for Allure Report generation.
*   **Allure Commandline**: Installed and added to system PATH.

## ⚙️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd automation-exercise
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

## 🏃 Running Tests

### 1. Local Execution (Default)
Run all tests on the default browser.
```bash
pytest
```

### 2. Parallel Execution
Run tests in parallel to reduce execution time.
```bash
pytest -n auto             # Auto-detect number of CPUs
pytest -n 4                # Run with 4 workers
```

### 3. Specific Browser Execution
Run tests on a specific browser profile from the matrix.
```bash
pytest --browser=chrome_latest
pytest --browser=firefox_latest
```

### 4. Remote Execution
```bash
pytest --remote --remote-url="http://localhost:4444/wd/hub"
```

## 📊 Reporting

The project uses **Allure Reports**.

1.  **Run tests** (Results saved to `reports/<timestamp>/allure-results`).
2.  **Generate Report**:
    ```bash
    # Serve directly
    allure serve reports/latest/allure-results
    ```

### Advanced Reporting
You can log custom steps and screenshots using the `ReportingManager`:
```python
from reporting.manager import ReportingManager
ReportingManager.reporter().log_step("Custom step info")
ReportingManager.reporter().attach_screenshot("Evidence", "/path/to/img.png")
```

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Tests not running on all browsers** | Ensure `browsers.yaml` has a correct `matrix` section. |
| **Grid connection failed** | Check if Docker container is running (`docker ps`) and port 4444 is open. |
| **Data loader error** | Verify file exists in `test_data/` and has valid syntax (YAML/JSON). |
| **Allure command not found** | Install Allure commandline tool and add to PATH. |

## 🤝 Contribution

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Project Maintainer - Evyatar Hazan
