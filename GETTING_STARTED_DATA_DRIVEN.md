# Getting Started with Data-Driven Testing

**Time to implement your first data-driven test: 5 minutes**

---

## Step 1: Create Test Data File

Create a new YAML file in `test_data/` directory:

**File:** `test_data/my_feature.yaml`

```yaml
tests:
  - username: alice
    password: secret123
    expected_role: admin

  - username: bob
    password: password456
    expected_role: user

  - username: charlie
    password: test789
    expected_role: user
```

---

## Step 2: Write Your Test

Add to your test file (e.g., `tests/test_my_feature.py`):

```python
import pytest
from utils.data_loader import load_test_data

@pytest.mark.parametrize(
    "user_data",
    load_test_data("test_data/my_feature.yaml"),
    ids=lambda u: u["username"]  # Use username as test ID
)
def test_user_login(driver, user_data):
    """Test login with multiple user credentials."""
    page = LoginPage(driver)
    page.navigate()
    page.login(user_data["username"], user_data["password"])
    
    if user_data["expected_role"]:
        assert page.get_user_role() == user_data["expected_role"]
    else:
        assert page.is_login_failed()
```

---

## Step 3: Run Your Tests

```bash
# Run all data-driven tests
pytest tests/test_my_feature.py -v

# Run specific dataset
pytest "tests/test_my_feature.py::test_user_login[alice]" -v

# With detailed output
pytest tests/test_my_feature.py -v -s
```

---

## What Happens

✅ **3 test cases are generated automatically:**
- `test_user_login[alice]` — Tests with alice's credentials
- `test_user_login[bob]` — Tests with bob's credentials  
- `test_user_login[charlie]` — Tests with charlie's credentials

✅ **Each test runs on all browsers:**
- Browser matrix is applied automatically
- Total: 3 users × 3 browsers = 9 test executions

✅ **Tests appear in reports:**
- Allure shows all 9 tests with proper naming
- Each has separate pass/fail status
- Screenshots and logs per test

---

## Other File Formats

### JSON Format

**File:** `test_data/my_feature.json`

```json
{
  "tests": [
    { "username": "alice", "password": "secret123", "expected_role": "admin" },
    { "username": "bob", "password": "password456", "expected_role": "user" }
  ]
}
```

**Usage:** Same code, just change file path
```python
load_test_data("test_data/my_feature.json")  # Works!
```

### CSV Format

**File:** `test_data/my_feature.csv`

```csv
username,password,expected_role
alice,secret123,admin
bob,password456,user
charlie,test789,user
```

**Usage:** Same code, convert types as needed
```python
@pytest.mark.parametrize("user", load_test_data("test_data/my_feature.csv"))
def test_login(driver, user):
    # CSV values are strings - convert if needed
    role = user.get("expected_role") or None
    ...
```

---

## Pro Tips

### 1. Use Custom Test IDs
Makes test output readable:

```python
@pytest.mark.parametrize(
    "data",
    load_test_data("test_data/search.json"),
    ids=lambda d: f"{d['query']}-{d['category']}"
)
def test_search(driver, data):
    ...

# Output:
# test_search[laptop-electronics] PASSED
# test_search[phone-electronics] PASSED
# test_search[shirt-clothing] PASSED
```

### 2. Mix Data Files

Use different data files for different tests:

```python
# Test login with login.yaml
@pytest.mark.parametrize("data", load_test_data("test_data/login.yaml"))
def test_login(driver, data):
    ...

# Test search with search.json
@pytest.mark.parametrize("data", load_test_data("test_data/search.json"))
def test_search(driver, data):
    ...
```

### 3. Convert CSV Types

CSV values are always strings:

```python
@pytest.mark.parametrize("data", load_test_data("test_data/filters.csv"))
def test_filter(driver, data):
    min_price = int(data["min_price"])        # String → int
    max_price = int(data["max_price"])        # String → int
    in_stock = data["in_stock"] == "true"     # String → bool
    ...
```

### 4. Add Comments to Test Data

YAML supports comments:

```yaml
# User credentials for login testing
tests:
  # Admin user - should see all features
  - username: admin
    password: admin123
    expected_role: admin

  # Regular user - limited features
  - username: user
    password: user123
    expected_role: user
```

### 5. Large Datasets

No problem - load from files instead of embedding:

```python
# File: test_data/1000_users.csv (1000 rows)
# Code: Same as always!
@pytest.mark.parametrize("user", load_test_data("test_data/1000_users.csv"))
def test_user_import(driver, user):
    ...

# Generates 1000 tests automatically
# Each runs on all browsers
# Perfect for load testing!
```

---

## Common Patterns

### Pattern 1: Authentication Tests
```python
@pytest.mark.parametrize("creds", load_test_data("test_data/login.yaml"))
def test_login(driver, creds):
    LoginPage(driver).login(creds["username"], creds["password"])
```

### Pattern 2: Search Tests
```python
@pytest.mark.parametrize("query", load_test_data("test_data/searches.json"))
def test_search(driver, query):
    results = SearchPage(driver).search(query["term"])
    assert len(results) >= query["min_results"]
```

### Pattern 3: E2E Tests
```python
@pytest.mark.parametrize("user", load_test_data("test_data/users.csv"))
@pytest.mark.parametrize("product", load_test_data("test_data/products.json"))
def test_purchase(driver, user, product):
    # Tests: users × products combinations
    page = StorePage(driver)
    page.login(user["username"], user["password"])
    page.buy(product["id"])
```

### Pattern 4: Configuration Tests
```python
@pytest.mark.parametrize("config", load_test_data("test_data/configs.yaml"))
def test_apply_config(driver, config):
    page = SettingsPage(driver)
    for key, value in config.items():
        page.set(key, value)
    assert page.save_config()
```

---

## File Organization

Best practices for organizing test data:

```
test_data/
├── authentication/
│   ├── valid_users.yaml
│   ├── invalid_users.yaml
│   └── locked_accounts.yaml
├── search/
│   ├── queries.json
│   └── filters.yaml
├── checkout/
│   ├── valid_payments.csv
│   └── invalid_payments.csv
└── smoke_tests.yaml
```

Then reference with full path:
```python
load_test_data("test_data/authentication/valid_users.yaml")
```

---

## Verification

Verify everything works:

```bash
# 1. Load all formats
python3 << 'EOF'
from utils.data_loader import load_test_data
yaml_data = load_test_data("test_data/login.yaml")
json_data = load_test_data("test_data/search.json")
csv_data = load_test_data("test_data/users.csv")
print(f"✓ YAML: {len(yaml_data)} cases")
print(f"✓ JSON: {len(json_data)} cases")
print(f"✓ CSV: {len(csv_data)} cases")
EOF

# 2. Collect tests
pytest tests/test_my_feature.py --collect-only -q

# 3. Run tests
pytest tests/test_my_feature.py -v
```

---

## Troubleshooting

### Issue: "Data file not found"
```python
# ❌ Wrong relative path
load_test_data("../test_data/login.yaml")

# ✓ Correct - relative to project root
load_test_data("test_data/login.yaml")
```

### Issue: CSV values are strings
```python
# ❌ Wrong - comparing string to int
assert data["count"] > 5  # "5" > 5 is an error

# ✓ Correct - convert first
assert int(data["count"]) > 5
```

### Issue: YAML not recognized
```python
# ❌ Wrong - no root key
# test_data/bad.yaml
- username: user1
  password: pass1

# ✓ Correct - use root key
# test_data/good.yaml
tests:
  - username: user1
    password: pass1
```

---

## Next Steps

1. ✅ Create your test data file (YAML/JSON/CSV)
2. ✅ Write your parametrized test
3. ✅ Run `pytest --collect-only` to see generated tests
4. ✅ Run tests: `pytest tests/your_test.py -v`
5. ✅ Check reports in `reports/` directory

---

## Resources

- **Quick Reference:** [DATA_DRIVEN_TESTING_QUICK_REF.md](DATA_DRIVEN_TESTING_QUICK_REF.md)
- **Complete Guide:** [DATA_DRIVEN_TESTING.md](DATA_DRIVEN_TESTING.md)
- **Code Examples:** [DATA_DRIVEN_EXAMPLES.py](DATA_DRIVEN_EXAMPLES.py)
- **Example Tests:** [tests/test_data_driven_examples.py](tests/test_data_driven_examples.py)

---

**That's it! You're ready to write data-driven tests.** 🚀
