
from asyncio.log import logger
from core.base_page import BasePage
import os


class CardPage(BasePage):
        
    CART_LINK = [
        {'type': 'css', 'value': 'a.dropdown-toggle[href*="checkout/cart"]'},
        {'type': 'xpath', 'value': '//a[contains(@class,"dropdown-toggle") and contains(@href,"checkout/cart")]'}
    ]

    SUB_TOTAL = [
        {'type': 'css', 'value': 'table#totals_table tr td span.extra.bold:contains("Sub-Total:") + td span.bold'},
        {'type': 'xpath', 'value': '//table[@id="totals_table"]//tr[td/span[contains(text(),"Sub-Total:")]]/td[2]/span'}
    ]

    REMOVE_CART_ITEMS = [
        {'type': 'css', 'value': 'a.btn.btn-sm.btn-default[href*="remove="]'},
        {'type': 'xpath', 'value': '//a[contains(@class,"btn") and contains(@class,"btn-sm") and contains(@href,"remove=")]'}
    ]


    def open_cart(self) -> None:
        """
        Open the cart page by clicking the cart link.
        """
        self.click(self.CART_LINK, "Cart Link")
        self.wait_for_page_load()

    def get_cart_subtotal(self) -> float:
        """
        Retrieve the cart subtotal amount.
        """
        subtotal_text = self.get_text(self.SUB_TOTAL, "Cart Subtotal")
        subtotal_value = float(subtotal_text.replace('$', '').replace(',', '').strip())
        logger.info(f"Cart subtotal retrieved: {subtotal_value:.2f}")
        return subtotal_value
    

    def remove_all_cart_items(self) -> None:
        """
        Remove all items from the cart.
        Iterates over all remove buttons and clicks them one by one.
        """
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        while True:
            try:
                # Find all remove buttons (fresh after each removal)
                remove_buttons = self.page.locator('a.btn.btn-sm.btn-default[href*="remove="]')
                count = remove_buttons.count()
                if count == 0:
                    break
                # Always click the first one (DOM updates after each click)
                remove_buttons.nth(0).click()
                self.wait_for_page_load()
            except PlaywrightTimeoutError:
                break
            except Exception:
                break

        

    def card_flow(self, budgetPerItem: float, itemsCount: int) -> bool:
        self.open_cart()
        subtotal = self.get_cart_subtotal()
        expected_total = budgetPerItem * itemsCount
        logger.info(f"Expected subtotal: {expected_total:.2f}, Actual subtotal: {subtotal:.2f}")
        self.remove_all_cart_items()
        return expected_total >= subtotal
