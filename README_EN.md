# Automation Framework Exercise

A robust, scalable test automation framework built with **Python**, **Playwright**, and **Pytest**. Designed for stability, flexibility, and ease of maintenance using the Page Object Model (POM) design pattern.

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
├── config/                 # Configuration files (config.yaml, browsers.yaml)
├── core/                   # Core framework logic (DriverFactory, BasePage, BaseTest)
├── pages/                  # Page Objects (POM)
├── tests/                  # Test scripts
├── test_data/              # Data files for data-driven testing (yaml, json, csv)
├── utils/                  # Utilities (DataLoader, etc.)
├── reporting/              # Reporting layer
├── reports/                # Test Execution Reports
├── logs/                   # Execution logs
├── conftest.py             # Pytest fixtures and hooks
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Project dependencies
```

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

2.  **Create and activate a virtual environment** (Optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright Browsers**:
    ```bash
    playwright install
    ```

## 🏃 Running Tests

The framework supports multiple execution modes suitable for local development, CI/CD, and grid environments.

### 1. Local Execution (Default)
Run all tests on the default browser (configured in `config/browsers.yaml`).
```bash
pytest
```

### 2. Parallel Execution
Run tests in parallel to reduce execution time (requires `pytest-xdist`).
```bash
pytest -n auto             # Auto-detect number of CPUs
pytest -n 4                # Run with 4 workers
```

### 3. Specific Browser Execution
Run tests on a specific browser profile defined in `config/browsers.yaml`.
```bash
pytest --browser=chrome_latest
pytest --browser=firefox_latest
pytest --browser=edge_latest
```

### 4. Remote / Grid Execution
Run tests on a remote Selenium Grid or Moon instance.
```bash
# Using CLI arguments
pytest --remote --remote-url="http://localhost:4444/wd/hub"

# Using Remote Marker (in code)
# @pytest.mark.remote(url="http://grid-box:4444")
```
*Note: Ensure your Grid/Moon instance is running and accessible.*

### 5. Tagged Execution
Run specific tests based on markers (defined in `pytest.ini`).
```bash
pytest -m smoke            # Run smoke tests
pytest -m regression       # Run regression suite
pytest -m ui               # Run UI tests
```

## 📊 Reporting

The project uses **Allure Reports** for rich visualization of test results.

1.  **Run tests** (Results are saved to `reports/<timestamp>/allure-results`):
    ```bash
    pytest
    ```

2.  **Generate and View Report**:
    ```bash
    # Serve directly
    allure serve reports/latest/allure-results

    # OR Generate static report
    allure generate reports/latest/allure-results -o reports/allure-report --clean
    allure open reports/allure-report
    ```

## 🔧 Configuration

*   **Global Settings**: `config/config.yaml` (Base URL, Timeouts, Retry logic, Reporting).
*   **Browser Profiles**: `config/browsers.yaml` (Define browsers, versions, viewports, capabilities).

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
