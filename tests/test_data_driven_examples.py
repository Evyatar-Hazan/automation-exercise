"""
Data-Driven Testing Examples

This module demonstrates how to use the load_test_data() function with pytest
parametrization to run tests against multiple datasets from external files.

Patterns shown:
1. Direct parametrization with load_test_data()
2. Using fixture wrapper for more complex scenarios
3. Multiple data formats (YAML, JSON, CSV)
4. Proper error handling and logging

These tests are NOT meant to run against a real application.
They serve as documentation and templates for implementing data-driven tests.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from loguru import logger

from utils.data_loader import load_test_data, DataLoaderError
from core.base_test import BaseTest


class TestDataDrivenLoginExamples(BaseTest):
    """
    Example: Data-Driven Login Tests
    
    Demonstrates loading credentials from YAML and running parametrized tests.
    Each test case represents a different login scenario (valid, admin, locked, etc).
    """
    
    @pytest.mark.parametrize(
        "login_data",
        load_test_data("test_data/login.yaml"),
        ids=lambda d: f"{d['username']}"  # Use username as test ID
    )
    def test_login_with_yaml_data(self, driver, login_data: Dict[str, Any]):
        """
        Test login with credentials from YAML.
        
        Each test case is a separate test run with different credentials.
        
        Args:
            driver: Playwright page fixture
            login_data: Dict from login.yaml containing username, password, expected_role
        
        Example test IDs generated:
            test_login_with_yaml_data[user1@example.com]
            test_login_with_yaml_data[user2@example.com]
            test_login_with_yaml_data[standard_user]
        """
        username = login_data["username"]
        password = login_data["password"]
        expected_role = login_data.get("expected_role", "customer")
        
        logger.info(
            f"Testing login for user: {username} "
            f"(expected role: {expected_role})"
        )
        
        # This is pseudo-code showing the pattern
        # In reality, you would:
        # 1. Navigate to login page
        # 2. Enter credentials
        # 3. Submit form
        # 4. Verify success/failure based on expected_role
        
        assert username is not None, "Username must not be empty"
        assert password is not None, "Password must not be empty"
        logger.info(f"✓ Login test passed for {username}")


class TestDataDrivenSearchExamples(BaseTest):
    """
    Example: Data-Driven Search Tests
    
    Demonstrates loading search queries from JSON and validating results.
    """
    
    @pytest.mark.parametrize(
        "search_params",
        load_test_data("test_data/search.json"),
        ids=lambda d: f"{d['query']}"
    )
    def test_search_with_json_data(self, driver, search_params: Dict[str, Any]):
        """
        Test product search with queries from JSON.
        
        Args:
            driver: Playwright page fixture
            search_params: Dict from search.json containing query, min_results, category
        """
        query = search_params["query"]
        min_results = search_params.get("min_results", 1)
        category = search_params.get("category")
        
        logger.info(f"Searching for: {query} (category: {category})")
        
        # Pseudo-code:
        # 1. Navigate to search page
        # 2. Enter query
        # 3. Apply filters if category specified
        # 4. Verify at least min_results returned
        
        assert query is not None, "Search query must not be empty"
        assert min_results > 0, "min_results must be positive"
        logger.info(f"✓ Search test passed for query: {query}")


class TestDataDrivenUserExamples(BaseTest):
    """
    Example: Data-Driven Tests with CSV
    
    Demonstrates loading user data from CSV with headers as dict keys.
    """
    
    @pytest.mark.parametrize(
        "user",
        load_test_data("test_data/users.csv"),
        ids=lambda d: f"{d['username']}"
    )
    def test_user_creation_with_csv_data(self, driver, user: Dict[str, Any]):
        """
        Test user account creation with data from CSV.
        
        CSV headers (username, password, email, first_name, last_name, role)
        are automatically converted to dict keys.
        
        Args:
            driver: Playwright page fixture
            user: Dict from users.csv with user account information
        """
        username = user["username"]
        password = user["password"]
        email = user["email"]
        role = user["role"]
        
        logger.info(
            f"Creating user: {username} (email: {email}, role: {role})"
        )
        
        # Pseudo-code:
        # 1. Navigate to user creation form
        # 2. Fill in all fields from user dict
        # 3. Submit
        # 4. Verify user created with correct role
        
        assert username, "Username required"
        assert password, "Password required"
        assert email, "Email required"
        assert role in ["customer", "admin", "moderator"], "Invalid role"
        logger.info(f"✓ User creation test passed for {username}")


class TestDataDrivenProductFilters(BaseTest):
    """
    Example: Data-Driven Product Filter Tests
    
    Demonstrates complex test data with multiple filter scenarios.
    """
    
    @pytest.mark.parametrize(
        "filter_config",
        load_test_data("test_data/product_filters.yaml"),
        ids=lambda d: f"{d['filter_name']}-{list(d.keys())[1]}"
    )
    def test_product_filtering_with_yaml_data(
        self,
        driver,
        filter_config: Dict[str, Any]
    ):
        """
        Test product filtering with various filter combinations.
        
        Args:
            driver: Playwright page fixture
            filter_config: Dict from product_filters.yaml with filter settings
        """
        filter_name = filter_config["filter_name"]
        expected_count = filter_config.get("expected_count", 0)
        
        logger.info(f"Testing filter: {filter_name}")
        logger.debug(f"Filter config: {filter_config}")
        
        # Pseudo-code:
        # 1. Navigate to products page
        # 2. Apply filter from filter_config (price, brand, category, etc)
        # 3. Verify result count matches expected_count
        
        assert filter_name, "Filter name required"
        assert expected_count > 0, "Expected count must be positive"
        logger.info(f"✓ Filter test passed: {filter_name}")


# ============================================================================
# OPTIONAL: Fixture-based approach
# ============================================================================

@pytest.fixture(params=load_test_data("test_data/login.yaml"))
def login_fixture(request):
    """
    Fixture-based approach: automatically parametrizes with login.yaml data.
    
    Usage:
        def test_something(driver, login_fixture):
            username = login_fixture["username"]
            ...
    
    This is optional - direct parametrization (shown above) is preferred
    as it keeps the test signature clean and parametrization explicit.
    """
    return request.param


def test_login_with_fixture_approach(driver, login_fixture: Dict[str, Any]):
    """
    Alternative: Using fixture instead of direct parametrization.
    
    Less explicit about parametrization in test signature,
    but useful for complex setup/teardown logic.
    """
    username = login_fixture["username"]
    logger.info(f"Testing login with fixture approach: {username}")
    assert username is not None
