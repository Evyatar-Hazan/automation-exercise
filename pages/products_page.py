
from asyncio.log import logger
from core.base_page import BasePage
import os


class ProductsPage(BasePage):
        
    ADD_TO_CART_BUTTON = [
        {'type': 'css', 'value': 'a.cart'},
        {'type': 'xpath', 'value': '//a[contains(@class,"cart")]'},
        {'type': 'xpath', 'value': '//a[i[contains(@class,"fa-cart-plus")]]'},
        {
            'type': 'xpath',
            'value': '//a[contains(@onclick,"submit")]'
        }
    ]

    def add_products_to_cart_and_screenshot(self, product_urls: list, screenshot_dir: str = None) -> dict:
        """
        For each product URL in the list:
        - Navigate to the product page
        - Add the product to the cart
        - Save a screenshot after adding to cart (in the current run's allure/timestamped report directory)
        
        Args:
            product_urls (list): List of product page URLs
            screenshot_dir (str): Directory to save screenshots (default: None, will use allure run dir)
        """
        from core import conftest
        if screenshot_dir is None:
            base_dir = getattr(conftest, '_REPORTS_RUN_DIR', None)
            if base_dir is None:
                base_dir = 'screenshots'
            screenshot_dir = os.path.join(str(base_dir), 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        prices = []
        for idx, url in enumerate(product_urls, 1):
            print(f"Processing product {idx}: {url}")
            self.navigate_to(url)
            self.wait_for_page_load()
            # Try to extract price before adding to cart
            price = None
            try:
                # Try common price selectors
                price_selectors = [
                    {'type': 'css', 'value': '.price .oneprice'},
                    {'type': 'css', 'value': '.price .pricenew'},
                    {'type': 'css', 'value': '.price'},
                    {'type': 'xpath', 'value': '//div[contains(@class,"price")]'},
                ]
                for sel in price_selectors:
                    try:
                        price_el = self.page.locator(sel['value'])
                        if price_el.count() > 0:
                            price_text = price_el.first.inner_text().replace(',', '').replace('₪', '').replace('$', '').strip()
                            price = float(''.join(c for c in price_text if (c.isdigit() or c == '.')))
                            break
                    except Exception:
                        continue
            except Exception:
                pass
            if price is not None:
                prices.append(price)
            self.click(self.ADD_TO_CART_BUTTON, f"Add To Cart Button (product {idx})")
            self.wait_for_page_load()
            screenshot_path = os.path.join(screenshot_dir, f"product_{idx}_cart.png")
            self.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Saved screenshot for product {idx} to {screenshot_path}")
        budget_per_item = sum(prices) / len(prices) if prices else 0
        items_count = len(product_urls)
        return {"budgetPerItem": budget_per_item, "itemsCount": items_count}
    
    

        

    def products_flow(self, products_list: list) -> dict:
        result = self.add_products_to_cart_and_screenshot(products_list)
        logger.info(f"Added {result['itemsCount']} items to cart with average price {result['budgetPerItem']:.2f}")
        return result