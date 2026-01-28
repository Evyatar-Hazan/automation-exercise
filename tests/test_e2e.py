

"""
End-to-End (E2E) Tests

Complete user journeys and full application flow tests.
Each test simulates real user interactions across multiple pages/features.

Test execution with browser matrix:
  pytest tests/test_e2e.py -v
  pytest tests/test_e2e.py --browser=chrome_127 -v
  
Tests will run on all browsers defined in config/browsers.yaml
"""

import pytest
from typing import Dict, Any
from loguru import logger

from core.base_test import BaseTest
from pages.cart_page import CardPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.search_page import SearchPage
from utils.data_loader import load_test_data

@pytest.fixture(params=load_test_data("test_data/login.yaml"))
def login_and_search_data(request):
    return request.param

class TestE2E(BaseTest):
    def test_e2e(self, driver, login_and_search_data):
        user = {
            "userName": login_and_search_data["userName"],
            "userPassword": login_and_search_data["userPassword"]
        }
        search = login_and_search_data["search"]

        logger.info(f"Running E2E test for: {user['userName']}")

        base_url = self.config_loader.get('base_url')
        driver.goto(base_url)

        login_page = LoginPage(driver)
        search_page = SearchPage(driver)
        products_page = ProductsPage(driver)
        card_page = CardPage(driver)

        assert login_page.login_flow(user['userName'], user['userPassword'])

        product_list = search_page.search_flow(search['query'], search['maxPrice'], search['limit'])
        assert len(product_list) > 0

        result = products_page.products_flow(product_list)
        assert result['itemsCount'] == len(product_list)

        assert card_page.card_flow(result['itemsCount'], result['budgetPerItem'])

        logger.info("E2E test completed successfully")

    
