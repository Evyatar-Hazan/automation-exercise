# Data-Driven Testing Implementation

This document explains the Data-Driven Testing layer for the automation framework.

---

## Overview

The framework now supports **Data-Driven Testing** through external data files (YAML, JSON, CSV). This allows test parameters to be:

- **Separated from test logic** — data files are pure data, not mixed with code
- **Easily maintained** — add new test cases by editing data files only
- **Scaled easily** — run the same test against 100 datasets without test code changes
- **Switched formats** — convert from YAML to JSON without modifying tests

---

## Folder Structure

```
automation-exercise/
├── utils/
│   ├── __init__.py
│   └── data_loader.py          ← Core data loading module
├── test_data/                   ← All test data files
│   ├── login.yaml               ← Login credentials
│   ├── search.json              ← Search queries
│   ├── users.csv                ← User accounts
│   └── product_filters.yaml     ← Filter configurations
├── tests/
│   └── test_data_driven_examples.py  ← Example usage patterns
└── ...
```

### Test Data Files

Store all test data in `test_data/` directory:

- **login.yaml** — Login credentials for authentication tests
- **search.json** — Search queries and product filters
- **users.csv** — User account data for creation/registration tests
- **product_filters.yaml** — Product filter combinations

---

## Module: `utils/data_loader.py`

### Public API

#### `load_test_data(path: str) -> List[Dict[str, Any]]`

Loads test data from external files and returns a list of dicts for pytest parametrization.

**Parameters:**
- `path` (str): File path (relative to project root or absolute)
  - Supported formats: `.yaml`, `.yml`, `.json`, `.csv`

**Returns:**
- `List[Dict[str, Any]]`: Test data ready for parametrization

**Raises:**
- `DataLoaderError`: On file not found, unsupported format, invalid content, or empty dataset

**Examples:**

```python
# Load from YAML
data = load_test_data("test_data/login.yaml")
# Returns: [
#   {"username": "user1@example.com", "password": "password123", "expected_role": "customer"},
#   {"username": "user2@example.com", "password": "password456", "expected_role": "admin"},
#   ...
# ]

# Load from JSON
data = load_test_data("test_data/search.json")
# Returns: [
#   {"query": "laptop", "min_results": 5, "category": "electronics"},
#   {"query": "phone", "min_results": 5, "category": "electronics"},
#   ...
# ]

# Load from CSV
data = load_test_data("test_data/users.csv")
# Returns: [
#   {"username": "john_doe", "password": "Pass@1234", "email": "john.doe@example.com", ...},
#   {"username": "jane_smith", "password": "Secure#5678", "email": "jane.smith@example.com", ...},
#   ...
# ]
```

---

## File Formats

### YAML Format

**File:** `test_data/login.yaml`

```yaml
tests:
  - username: user1@example.com
    password: password123
    expected_role: customer

  - username: user2@example.com
    password: password456
    expected_role: admin

  - username: locked_out_user
    password: wrong_password
    expected_role: null
```

**Features:**
- `tests` root key is recognized (optional — can be direct list)
- Supports nested dicts and multiple data types
- Comments with `#`
- Clean, human-readable format

**Recognized root keys:** `tests`, `data`, `cases`, `test_cases`, `rows`

### JSON Format

**File:** `test_data/search.json`

```json
{
  "tests": [
    {
      "query": "laptop",
      "min_results": 5,
      "category": "electronics"
    },
    {
      "query": "phone",
      "min_results": 5,
      "category": "electronics"
    }
  ]
}
```

**Features:**
- `tests` root key is recognized (optional — can be direct list)
- Supports complex nested structures
- Standard JSON array support

**Recognized root keys:** `tests`, `data`, `cases`, `test_cases`, `rows`

### CSV Format

**File:** `test_data/users.csv`

```csv
username,password,email,first_name,last_name,role
john_doe,Pass@1234,john.doe@example.com,John,Doe,customer
jane_smith,Secure#5678,jane.smith@example.com,Jane,Smith,admin
bob_wilson,MyPassword99,bob.wilson@example.com,Bob,Wilson,customer
```

**Features:**
- First row is treated as headers → become dict keys
- Each row becomes a dict
- Simple, spreadsheet-friendly format
- Ideal for large datasets

**Important:** CSV values are always strings. Convert to appropriate types in test code if needed.

```python
min_price = int(filter_config["min_price"])
rating = float(user_data["rating"])
```

---

## Usage Patterns

### Pattern 1: Direct Parametrization (Recommended)

This is the **preferred pattern**. It's explicit, clean, and integrates seamlessly with pytest.

```python
import pytest
from utils.data_loader import load_test_data

@pytest.mark.parametrize(
    "login_data",
    load_test_data("test_data/login.yaml"),
    ids=lambda d: f"{d['username']}"  # Optional: custom test IDs
)
def test_login(driver, login_data):
    username = login_data["username"]
    password = login_data["password"]
    
    # Use login_data to drive test
    ...
```

**Benefits:**
- Explicit parametrization in test signature
- Custom test IDs for clarity in pytest output
- Direct access to data via parameter
- No hidden fixture logic

**Example pytest output:**

```
test_login[user1@example.com] PASSED
test_login[user2@example.com] PASSED
test_login[standard_user] PASSED
test_login[locked_out_user] PASSED
```

### Pattern 2: Fixture Wrapper (Optional)

Use fixtures for more complex setup/teardown or data transformations.

```python
import pytest
from utils.data_loader import load_test_data

@pytest.fixture(params=load_test_data("test_data/users.csv"))
def user_fixture(request):
    """Fixture automatically parametrizes with CSV data."""
    return request.param

def test_user_creation(driver, user_fixture):
    """Fixture injects each test case automatically."""
    username = user_fixture["username"]
    ...
```

**When to use fixtures:**
- Complex setup/teardown per test case
- Data transformations needed
- Reusing same data across multiple tests

---

## Real-World Example

### Test File: `test_product_search.py`

```python
import pytest
from utils.data_loader import load_test_data
from pages.search_page import SearchPage
from core.base_test import BaseTest

class TestProductSearch(BaseTest):
    
    @pytest.mark.parametrize(
        "search_params",
        load_test_data("test_data/search.json"),
        ids=lambda d: f"{d['query']}"
    )
    def test_search_returns_results(self, driver, search_params):
        """Test that each search query returns expected number of results."""
        
        page = SearchPage(driver)
        page.navigate()
        
        results = page.search(search_params["query"])
        
        min_results = search_params.get("min_results", 1)
        assert len(results) >= min_results, \
            f"Expected at least {min_results} results for '{search_params['query']}', "
            f"but got {len(results)}"
        
        if "category" in search_params:
            page.assert_all_results_in_category(search_params["category"])
```

### Test Data: `test_data/search.json`

```json
{
  "tests": [
    { "query": "laptop", "min_results": 5, "category": "electronics" },
    { "query": "phone", "min_results": 5, "category": "electronics" },
    { "query": "t-shirt", "min_results": 3, "category": "clothing" }
  ]
}
```

### Test Execution

```bash
# Run all search tests (3 scenarios)
pytest tests/test_product_search.py::TestProductSearch::test_search_returns_results -v

# Output:
# test_search_returns_results[laptop] PASSED
# test_search_returns_results[phone] PASSED
# test_search_returns_results[t-shirt] PASSED

# Run specific scenario
pytest 'tests/test_product_search.py::TestProductSearch::test_search_returns_results[laptop]' -v
```

---

## Error Handling

The data loader raises `DataLoaderError` with clear messages on failure.

```python
from utils.data_loader import load_test_data, DataLoaderError

try:
    data = load_test_data("test_data/missing.yaml")
except DataLoaderError as e:
    print(f"Failed to load data: {e}")
    # Output: "Failed to load data: Data file not found: /abs/path/test_data/missing.yaml"
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Data file not found: ...` | File doesn't exist | Check path and file name |
| `Unsupported file format: .txt` | Wrong file extension | Use `.yaml`, `.json`, or `.csv` |
| `Empty dataset in ...` | File is empty or has only headers | Add test data to file |
| `Invalid data structure in ...` | File content is not a list/dict | Fix file structure |
| `CSV file ... has no header row` | CSV missing first row | Add header row to CSV |
| `Error loading json file: ...` | JSON syntax error | Fix JSON syntax |

---

## Validation & Best Practices

### 1. Data Structure Validation

Validate required keys exist in test data:

```python
def test_login(driver, login_data):
    # Validate required keys
    required = ["username", "password"]
    for key in required:
        assert key in login_data, f"Missing required field: {key}"
    
    # Use with confidence
    page.login(login_data["username"], login_data["password"])
```

### 2. Type Conversion

CSV values are strings. Convert to appropriate types:

```python
@pytest.mark.parametrize("filter_data", load_test_data("test_data/filters.csv"))
def test_price_filter(driver, filter_data):
    min_price = int(filter_data["min_price"])      # CSV → int
    max_price = int(filter_data["max_price"])      # CSV → int
    expected = int(filter_data["expected_count"])  # CSV → int
    
    page.filter_by_price(min_price, max_price)
    assert len(page.get_results()) == expected
```

### 3. Logging & Debugging

Enable detailed logging:

```python
from loguru import logger

logger.info(f"Testing with data: {login_data}")
logger.debug(f"All fields: {login_data.keys()}")
```

Check framework logs for data loader output:

```
[DEBUG] Loading test data from: test_data/login.yaml
[INFO] Successfully loaded 5 test case(s) from login.yaml
```

### 4. Test IDs for Clarity

Use custom pytest IDs to make test output readable:

```python
# ❌ Bad: Uses numeric indices
@pytest.mark.parametrize("data", load_test_data("test_data/login.yaml"))

# ✓ Good: Uses meaningful identifiers
@pytest.mark.parametrize(
    "data",
    load_test_data("test_data/login.yaml"),
    ids=lambda d: d["username"]
)

# ✓ Also good: Composite IDs
@pytest.mark.parametrize(
    "data",
    load_test_data("test_data/search.json"),
    ids=lambda d: f"{d['query']}-{d.get('category', 'all')}"
)
```

---

## Backward Compatibility

✓ All existing tests continue to work  
✓ Data-driven testing is opt-in per test  
✓ No breaking changes to framework  
✓ No global configuration required  

Tests without external data work unchanged:

```python
def test_simple_navigation(driver):
    """Non-data-driven test still works."""
    driver.goto("https://example.com")
    assert driver.title == "Example"
```

---

## Integration with Existing Framework

### With BaseTest

```python
from core.base_test import BaseTest
from utils.data_loader import load_test_data

class TestMyFeature(BaseTest):
    
    @pytest.mark.parametrize(
        "test_data",
        load_test_data("test_data/my_data.yaml")
    )
    def test_something(self, driver, test_data):
        # driver fixture is automatically injected
        # test_data comes from parametrization
        ...
```

### With Browser Matrix

Data-driven tests automatically run on all browsers in the browser matrix:

```python
# If browser matrix has 3 browsers (chrome, firefox, safari)
# and test_data has 4 scenarios
# Total tests: 3 browsers × 4 scenarios = 12 test runs

@pytest.mark.parametrize("data", load_test_data("test_data/search.json"))
def test_search(driver, data):
    ...
```

### With Reporting

All parametrized tests are properly reported in Allure:

```
Test Results
├── test_search[laptop] PASSED
├── test_search[phone] PASSED
├── test_search[t-shirt] PASSED
...
```

---

## Troubleshooting

### Issue: "Data file not found"

```python
# ❌ Wrong: Relative path doesn't exist
load_test_data("../test_data/login.yaml")

# ✓ Correct: Relative to project root
load_test_data("test_data/login.yaml")

# ✓ Also works: Absolute path
load_test_data("/home/user/project/test_data/login.yaml")
```

### Issue: CSV values are strings

```python
# ❌ Wrong: Comparing string to int
assert filter_data["min_results"] >= 5  # "5" >= 5 → TypeError

# ✓ Correct: Convert CSV string to appropriate type
assert int(filter_data["min_results"]) >= 5
```

### Issue: No test cases generated

```python
# ❌ Wrong: Empty data file
# test_data/empty.yaml (contents: {})

# ✓ Correct: Add test cases or root key
# test_data/data.yaml
# tests:
#   - key: value

data = load_test_data("test_data/data.yaml")  # Works!
```

### Issue: Wrong root key in YAML/JSON

```yaml
# ❌ Wrong: Unrecognized root key
datasets:
  - username: user1
    password: pass1

# ✓ Correct: Use recognized root key
tests:
  - username: user1
    password: pass1

# ✓ Also correct: Direct list (no root key)
- username: user1
  password: pass1
```

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| YAML support | ✅ | With root key detection |
| JSON support | ✅ | With root key detection |
| CSV support | ✅ | Headers → dict keys |
| Pytest parametrization | ✅ | Primary pattern |
| Fixture wrapper | ✅ | Optional |
| Error handling | ✅ | Clear, descriptive errors |
| Logging | ✅ | Integrated with loguru |
| Backward compatibility | ✅ | Fully opt-in |
| Browser matrix integration | ✅ | Works automatically |

---

## References

- **Data Loader Module:** [utils/data_loader.py](../utils/data_loader.py)
- **Example Tests:** [tests/test_data_driven_examples.py](../tests/test_data_driven_examples.py)
- **Sample Data:**
  - [test_data/login.yaml](../test_data/login.yaml)
  - [test_data/search.json](../test_data/search.json)
  - [test_data/users.csv](../test_data/users.csv)
  - [test_data/product_filters.yaml](../test_data/product_filters.yaml)
- **pytest Parametrization:** https://docs.pytest.org/en/stable/how-to/parametrize.html
