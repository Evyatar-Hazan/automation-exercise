"""
QUICK REFERENCE: Locator Strategy Usage

DEFINE LOCATORS
===============
ELEMENT_NAME = [
    {'type': 'xpath', 'value': '//button[@id="submit"]'},
    {'type': 'css', 'value': '#submit'},
    {'type': 'text', 'value': 'Submit'}
]

PAGE OBJECT
===========
from core.base_page import BasePage

class MyPage(BasePage):
    BUTTON = [
        {'type': 'css', 'value': '#btn'},
        {'type': 'xpath', 'value': '//button[@id="btn"]'}
    ]
    
    def click_button(self):
        self.click(self.BUTTON, "Button Name")

TEST
====
from core.base_test import BaseTest

class TestExample(BaseTest):
    def test_something(self, driver):
        page = MyPage(driver)
        page.click_button()

LOCATOR TYPES
=============
xpath  : {'type': 'xpath', 'value': '//div[@id="content"]'}
css    : {'type': 'css', 'value': '#content'}
id     : {'type': 'id', 'value': 'content'}
text   : {'type': 'text', 'value': 'Click Me'}
role   : {'type': 'role', 'value': 'button'}

BASE PAGE METHODS
=================
self.click(locators, "Element Name")
self.type(locators, "text", "Element Name")
self.get_text(locators, "Element Name")
self.is_visible(locators, "Element Name")
self.find_element(locators, "Element Name")

FALLBACK BEHAVIOR
=================
Try Locator 1 → FAIL → Log
Try Locator 2 → FAIL → Log
Try Locator 3 → SUCCESS → Return element

All fail → Screenshot + Exception

RUN TESTS
=========
pytest tests/test_locator_demo.py -v
"""
