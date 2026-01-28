"""
Data-Driven Testing Usage Examples

Quick copy-paste examples for different scenarios.
All examples are production-ready and follow framework conventions.
"""

# ============================================================================
# EXAMPLE 1: Simple YAML Login Test
# ============================================================================

"""
Test data: test_data/login.yaml

tests:
  - username: user1
    password: pass1
  - username: user2
    password: pass2
"""

import pytest
from utils.data_loader import load_test_data

@pytest.mark.parametrize(
    "login_data",
    load_test_data("test_data/login.yaml")
)
def test_login_simple(driver, login_data):
    """Simplest data-driven test pattern."""
    page = LoginPage(driver)
    page.login(login_data["username"], login_data["password"])
    assert page.is_logged_in()


# ============================================================================
# EXAMPLE 2: JSON with Custom Test IDs
# ============================================================================

"""
Test data: test_data/search.json

{
  "tests": [
    { "query": "laptop", "min_results": 5 },
    { "query": "phone", "min_results": 10 }
  ]
}
"""

@pytest.mark.parametrize(
    "search_params",
    load_test_data("test_data/search.json"),
    ids=lambda s: s["query"]  # Use query as test ID
)
def test_search_with_ids(driver, search_params):
    """Data-driven test with readable test IDs."""
    page = SearchPage(driver)
    results = page.search(search_params["query"])
    
    assert len(results) >= search_params["min_results"], \
        f"Expected at least {search_params['min_results']} results"


# ============================================================================
# EXAMPLE 3: CSV with Type Conversion
# ============================================================================

"""
Test data: test_data/users.csv

username,email,age,is_admin
john_doe,john@example.com,25,true
jane_smith,jane@example.com,30,false
"""

@pytest.mark.parametrize(
    "user",
    load_test_data("test_data/users.csv")
)
def test_create_user_from_csv(driver, user):
    """CSV data requires type conversion."""
    page = UserPage(driver)
    
    # CSV values are strings - convert as needed
    username = user["username"]
    email = user["email"]
    age = int(user["age"])  # CSV → int
    is_admin = user["is_admin"] == "true"  # CSV → bool
    
    page.create_user(username, email, age, is_admin)
    assert page.user_exists(username)


# ============================================================================
# EXAMPLE 4: Complex Data with Validation
# ============================================================================

"""
Test data: test_data/filters.yaml

tests:
  - filter_name: price
    min_price: 10
    max_price: 100
    expected_min_count: 5
  - filter_name: brand
    brand: "BrandA"
    expected_min_count: 3
"""

@pytest.mark.parametrize(
    "filter_config",
    load_test_data("test_data/filters.yaml"),
    ids=lambda c: c["filter_name"]
)
def test_product_filters(driver, filter_config):
    """Complex data with validation and conditional logic."""
    page = ProductPage(driver)
    
    # Validate required fields
    required_fields = ["filter_name", "expected_min_count"]
    for field in required_fields:
        assert field in filter_config, f"Missing required field: {field}"
    
    # Apply appropriate filter
    filter_name = filter_config["filter_name"]
    
    if filter_name == "price":
        page.filter_by_price(
            filter_config["min_price"],
            filter_config["max_price"]
        )
    elif filter_name == "brand":
        page.filter_by_brand(filter_config["brand"])
    else:
        raise ValueError(f"Unknown filter: {filter_name}")
    
    # Verify results
    results = page.get_results()
    assert len(results) >= filter_config["expected_min_count"], \
        f"Filter '{filter_name}' returned {len(results)} results, " \
        f"expected at least {filter_config['expected_min_count']}"


# ============================================================================
# EXAMPLE 5: Using with BaseTest
# ============================================================================

from core.base_test import BaseTest

class TestDataDrivenFeatures(BaseTest):
    """Data-driven tests using BaseTest for better organization."""
    
    @pytest.mark.parametrize(
        "credentials",
        load_test_data("test_data/login.yaml"),
        ids=lambda c: c["username"]
    )
    def test_multi_user_login(self, driver, credentials):
        """Parametrized test within BaseTest class."""
        page = LoginPage(driver)
        page.login(credentials["username"], credentials["password"])
        assert page.is_logged_in()


# ============================================================================
# EXAMPLE 6: Fixture-Based Approach (Alternative)
# ============================================================================

"""
Use fixtures when you need setup/teardown per test case.
Less common than direct parametrization, but useful for complex scenarios.
"""

@pytest.fixture(params=load_test_data("test_data/users.csv"))
def user_with_setup(request):
    """Fixture that parametrizes with CSV data and adds setup."""
    user = request.param
    
    # Setup: Create any required objects
    print(f"Setting up test for user: {user['username']}")
    
    yield user
    
    # Teardown: Cleanup after each test
    print(f"Cleaning up after user: {user['username']}")


def test_user_with_fixture(driver, user_with_setup):
    """Use fixture when you need complex setup/teardown."""
    page = UserPage(driver)
    page.create_user(user_with_setup["username"], user_with_setup["email"])
    assert page.user_exists(user_with_setup["username"])


# ============================================================================
# EXAMPLE 7: Error Handling
# ============================================================================

from utils.data_loader import load_test_data, DataLoaderError

def load_test_data_safe(path: str):
    """Load data with error handling."""
    try:
        return load_test_data(path)
    except DataLoaderError as e:
        print(f"Failed to load test data: {e}")
        # Fallback to empty list or default data
        return []


# ============================================================================
# EXAMPLE 8: Multiple Parametrizations
# ============================================================================

"""
Combine multiple parametrizations for cross-product testing.
"""

@pytest.mark.parametrize(
    "username",
    ["user1", "user2"]
)
@pytest.mark.parametrize(
    "product",
    load_test_data("test_data/products.yaml")
)
def test_product_purchase_multiple_users(driver, username, product):
    """Run same test with multiple users and products."""
    page = StorePage(driver)
    page.login(username)
    page.buy_product(product["id"])
    assert page.purchase_confirmed()


# ============================================================================
# EXAMPLE 9: Parametrize with Both Data and Browser Matrix
# ============================================================================

"""
Data-driven tests automatically run on all browsers in browser matrix.
If browser matrix has 3 browsers and data has 5 cases:
Total test runs = 3 browsers × 5 data cases = 15 tests
"""

@pytest.mark.parametrize(
    "search_term",
    load_test_data("test_data/searches.json"),
    ids=lambda s: s["query"]
)
def test_search_all_browsers_all_queries(driver, search_term):
    """
    Runs automatically on:
    - chrome_127 + query1
    - chrome_127 + query2
    - chrome_latest + query1
    - chrome_latest + query2
    - firefox_latest + query1
    - firefox_latest + query2
    etc.
    """
    page = SearchPage(driver)
    results = page.search(search_term["query"])
    assert len(results) > 0


# ============================================================================
# EXAMPLE 10: Real-World E2E Test
# ============================================================================

"""
Complete end-to-end test combining multiple patterns.
"""

from pages.login_page import LoginPage
from pages.products_page import ProductPage
from pages.checkout_page import CheckoutPage
from core.base_test import BaseTest

class TestE2EPurchaseFlow(BaseTest):
    """End-to-end purchase test with multiple data sources."""
    
    @pytest.mark.parametrize(
        "user_data",
        load_test_data("test_data/users.csv"),
        ids=lambda u: u["username"]
    )
    @pytest.mark.parametrize(
        "product",
        load_test_data("test_data/products.json"),
        ids=lambda p: p["name"]
    )
    def test_complete_purchase_flow(self, driver, user_data, product):
        """
        Test complete purchase flow for multiple users and products.
        
        Generates tests like:
        - test_complete_purchase_flow[john_doe-laptop]
        - test_complete_purchase_flow[john_doe-phone]
        - test_complete_purchase_flow[jane_smith-laptop]
        - test_complete_purchase_flow[jane_smith-phone]
        etc.
        """
        
        # Login
        login_page = LoginPage(driver)
        login_page.navigate()
        login_page.login(user_data["username"], user_data["password"])
        
        # Browse products
        product_page = ProductPage(driver)
        product_page.navigate()
        product_page.search(product["name"])
        product_page.select_product(product["id"])
        
        # Add to cart and checkout
        checkout_page = CheckoutPage(driver)
        checkout_page.add_to_cart()
        checkout_page.proceed_to_checkout()
        
        # Complete purchase
        order_id = checkout_page.complete_order(
            user_data["username"],
            user_data["email"]
        )
        
        assert order_id is not None, "Order should be created"


# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
PATTERNS:

1. Simple parametrization:
   @pytest.mark.parametrize("data", load_test_data("file.yaml"))
   def test_something(driver, data):

2. With custom test IDs:
   @pytest.mark.parametrize(
       "data",
       load_test_data("file.yaml"),
       ids=lambda d: d["key"]
   )
   def test_something(driver, data):

3. With fixture (optional):
   @pytest.fixture(params=load_test_data("file.yaml"))
   def data_fixture(request):
       return request.param
   
   def test_something(driver, data_fixture):

4. CSV type conversion:
   age = int(data["age"])  # CSV → int
   active = data["active"] == "true"  # CSV → bool

FILES:

- test_data/login.yaml       - Login credentials
- test_data/search.json      - Search queries
- test_data/users.csv        - User data
- test_data/product_*.yaml   - Product configurations

DOCUMENTATION:

- Full guide: DATA_DRIVEN_TESTING.md
- Quick ref: DATA_DRIVEN_TESTING_QUICK_REF.md
- Implementation: DATA_DRIVEN_TESTING_IMPLEMENTATION.md
- Source: utils/data_loader.py
"""
