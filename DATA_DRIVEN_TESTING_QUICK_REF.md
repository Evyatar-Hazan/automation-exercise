# Data-Driven Testing Quick Reference

## TL;DR

Run tests with data from external files instead of hardcoding test inputs.

```python
from utils.data_loader import load_test_data
import pytest

@pytest.mark.parametrize(
    "data",
    load_test_data("test_data/login.yaml")
)
def test_login(driver, data):
    page.login(data["username"], data["password"])
```

---

## File Organization

```
test_data/
├── login.yaml          # Login credentials
├── search.json         # Search queries
├── users.csv           # User data
└── product_filters.yaml
```

---

## Supported Formats

### YAML
```yaml
tests:
  - username: user1
    password: pass1
  - username: user2
    password: pass2
```

### JSON
```json
{
  "tests": [
    { "username": "user1", "password": "pass1" },
    { "username": "user2", "password": "pass2" }
  ]
}
```

### CSV
```csv
username,password
user1,pass1
user2,pass2
```

---

## Basic Usage

```python
from utils.data_loader import load_test_data

# Load data
data = load_test_data("test_data/login.yaml")

# Returns: [
#   {"username": "user1", "password": "pass1"},
#   {"username": "user2", "password": "pass2"}
# ]
```

---

## Pytest Parametrization

```python
@pytest.mark.parametrize(
    "login_data",
    load_test_data("test_data/login.yaml")
)
def test_login(driver, login_data):
    username = login_data["username"]
    password = login_data["password"]
    ...
```

---

## Custom Test IDs

```python
@pytest.mark.parametrize(
    "user",
    load_test_data("test_data/users.csv"),
    ids=lambda u: u["username"]  # Use username as test ID
)
def test_create_user(driver, user):
    ...

# Output:
# test_create_user[john_doe] PASSED
# test_create_user[jane_smith] PASSED
```

---

## Error Handling

```python
from utils.data_loader import load_test_data, DataLoaderError

try:
    data = load_test_data("test_data/missing.yaml")
except DataLoaderError as e:
    print(f"Error: {e}")
```

Common errors:
- `Data file not found` → Check file path
- `Unsupported file format: .txt` → Use `.yaml`, `.json`, or `.csv`
- `Empty dataset` → Add test data to file

---

## Type Conversion (CSV)

CSV values are always strings. Convert as needed:

```python
@pytest.mark.parametrize("data", load_test_data("test_data/filters.csv"))
def test_filter(driver, data):
    min_price = int(data["min_price"])      # String → int
    rating = float(data["rating"])           # String → float
    active = data["active"] == "true"        # String → bool
```

---

## Fixture Alternative

```python
@pytest.fixture(params=load_test_data("test_data/login.yaml"))
def login_fixture(request):
    return request.param

def test_login(driver, login_fixture):
    ...
```

Less explicit but useful for complex setup/teardown.

---

## Integration with Browser Matrix

Data-driven tests automatically run on all browsers:

```python
# 5 test cases × 3 browsers = 15 test runs
@pytest.mark.parametrize("data", load_test_data("test_data/login.yaml"))
def test_login(driver, data):
    ...
```

---

## Real Example

**Data:** `test_data/search.json`
```json
{
  "tests": [
    { "query": "laptop", "expected_count": 50 },
    { "query": "phone", "expected_count": 100 },
    { "query": "tablet", "expected_count": 30 }
  ]
}
```

**Test:** `test_search.py`
```python
from utils.data_loader import load_test_data
import pytest

@pytest.mark.parametrize(
    "search_params",
    load_test_data("test_data/search.json"),
    ids=lambda s: s["query"]
)
def test_search_results_count(driver, search_params):
    page = SearchPage(driver)
    results = page.search(search_params["query"])
    
    assert len(results) >= search_params["expected_count"], \
        f"Expected at least {search_params['expected_count']} results, " \
        f"got {len(results)}"
```

**Running:**
```bash
pytest test_search.py -v

# Output:
# test_search_results_count[laptop] PASSED
# test_search_results_count[phone] PASSED
# test_search_results_count[tablet] PASSED
```

---

## Best Practices

✅ **DO:**
- Keep test data separate from test code
- Use meaningful file paths: `test_data/feature_name.yaml`
- Validate required fields in tests
- Use custom pytest IDs for readability
- Convert CSV strings to appropriate types
- Log what data is being tested

❌ **DON'T:**
- Mix test logic with data loading
- Hardcode test data in test files
- Assume CSV values are numbers (always strings)
- Create deeply nested test data structures
- Use YAML without root keys (use `tests:` key)

---

## See Also

- Full documentation: [DATA_DRIVEN_TESTING.md](DATA_DRIVEN_TESTING.md)
- Data loader module: [utils/data_loader.py](utils/data_loader.py)
- Example tests: [tests/test_data_driven_examples.py](tests/test_data_driven_examples.py)
