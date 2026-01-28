
from core.base_page import BasePage
from asyncio.log import logger


class SearchPage(BasePage):
    NEXT_PAGE_BUTTON = [
        {'type': 'xpath', 'value': '//a[normalize-space()=">"]'},
        {'type': 'xpath', 'value': '//a[contains(@href,"page=")]'},
        {'type': 'xpath', 'value': '//ul[contains(@class,"pagination")]//a[normalize-space()=">"]'}
    ]

    SEARCH_KEYWORD_INPUT = [
        {'type': 'css', 'value': '#filter_keyword'},
        {'type': 'css', 'value': 'input[name="filter_keyword"]'},
        {'type': 'xpath', 'value': '//input[@id="filter_keyword"]'},
        {'type': 'xpath', 'value': '//input[@type="text" and @name="filter_keyword"]'},
        {'type': 'xpath', 'value': '//input[@placeholder="Search Keywords"]'},
        {'type': 'css', 'value': 'input.search-query'}
    ]

    SEARCH_SUBMIT_BUTTON = [
        {'type': 'css', 'value': 'div.button-in-search[title="Go"]'},
        {'type': 'xpath', 'value': '//div[contains(@class,"button-in-search") and @title="Go"]'},
        {'type': 'xpath', 'value': '//div[i[contains(@class,"fa-search")]]'},
        {'type': 'css', 'value': 'div.button-in-search'}
    ]

    SORT_DROPDOWN = [
        {'type': 'css', 'value': '#sort'},
        {'type': 'css', 'value': 'select[name="sort"]'},
        {'type': 'xpath', 'value': '//select[@id="sort"]'},
        {'type': 'xpath', 'value': '//select[@id="sort" and @name="sort"]'},
        {'type': 'css', 'value': 'select.form-control'}
    ]

    PRODUCTS_GRID = [
        {'type': 'css', 'value': 'div.thumbnails.grid'},
        {'type': 'xpath', 'value': '//div[contains(@class,"thumbnails") and contains(@class,"grid")]'}
    ]

    PRODUCT_CARD = [
        {'type': 'css', 'value': 'div.thumbnails.grid > div.col-md-3'},
        {'type': 'xpath', 'value': '//div[contains(@class,"thumbnails")]/div[contains(@class,"col-md-3")]'}
    ]

    PRODUCT_PRICE = [
        {'type': 'css', 'value': '.price .oneprice'},
        {'type': 'css', 'value': '.price .pricenew'},
        {
            'type': 'xpath',
            'value': './/div[contains(@class,"price")]//div[contains(@class,"price")]'
        }
    ]

    NEXT_PAGE_BUTTON = [
        {'type': 'xpath', 'value': '//a[normalize-space()=">"]'},
        {'type': 'xpath', 'value': '//a[contains(@href,"page=")]'},
        {
            'type': 'xpath',
            'value': '//ul[contains(@class,"pagination")]//a[normalize-space()=">"]'
        }
    ]






    def enter_search_keyword(self, keyword: str) -> None:
        self.type(self.SEARCH_KEYWORD_INPUT, keyword, "Search Keyword Input")

    def click_search_button(self) -> None:
        self.click(self.SEARCH_SUBMIT_BUTTON, "Search Button")

    def click_sort_dropdown(self) -> None:
        self.click(self.SORT_DROPDOWN, "Sort Dropdown")

    def select_price_low_to_high(self) -> None:
        self.select(self.SORT_DROPDOWN, value="p.price-ASC", element_name="Sort Dropdown")

    def get_products_under_price(self, max_price: float, limit: int = 5) -> list:
        product_links = []
        visited_pages = set()
        while len(product_links) < limit:
            grid = self.find_element(self.PRODUCTS_GRID, "Products Grid")
            cards = grid.locator('div.col-md-3')
            count = cards.count()
            for i in range(count):
                if len(product_links) >= limit:
                    break
                card = cards.nth(i)
                price_text = None
                for price_locator in self.PRODUCT_PRICE:
                    try:
                        price_el = card.locator(price_locator['value'])
                        if price_el.count() > 0:
                            price_text = price_el.first.inner_text().replace(',', '').replace('₪', '').replace('$', '').strip()
                            break
                    except Exception:
                        continue
                if not price_text:
                    continue
                try:
                    price = float(''.join(c for c in price_text if (c.isdigit() or c == '.')))
                except Exception:
                    continue
                if price <= max_price:
                    try:
                        link_el = card.locator('a')
                        if link_el.count() > 0:
                            href = link_el.first.get_attribute('href')
                            if href and href not in product_links:
                                product_links.append(href)
                    except Exception:
                        continue
            if len(product_links) >= limit:
                break
            # Try to go to next page if possible
            try:
                next_btn = self.find_element(self.NEXT_PAGE_BUTTON, "Next Page Button")
                current_url = self.page.url
                if current_url in visited_pages:
                    break
                visited_pages.add(current_url)
                if next_btn.is_enabled() and next_btn.is_visible():
                    next_btn.click()
                    self.wait_for_page_load()
                else:
                    break
            except Exception:
                break
        return product_links[:limit]

    def search_flow(self, query: str, maxPrice: float, limit = 5) -> list:
        self.enter_search_keyword(query)
        self.click_search_button()
        self.select_price_low_to_high()
        products = self.get_products_under_price(maxPrice, limit)
        logger.info(f"Found {len(products)} products under {maxPrice}:")
        for p in products:
            logger.info(f" - {p}")
        return products