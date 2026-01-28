"""
Login Page Module

This module provides the LoginPage class for automating login-related interactions
on the application's login page. It uses multi-locator fallback strategy to handle
dynamic UI changes and various DOM structures.

Features:
- Multiple locator strategies (CSS, XPath) for each UI element
- Automatic fallback to alternative locators if primary fails
- Complete login workflow automation
- Verification of successful login

Usage Example:
    from pages.login_page import LoginPage
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        
        login_page = LoginPage(page)
        login_page.login_flow("user@example.com", "password123")
        assert login_page.is_welcome_back_visible()
"""

from core.base_page import BasePage


class LoginPage(BasePage):
    """
    Login Page class for automating login interactions.
    
    Inherits from BasePage to leverage the multi-locator fallback strategy
    and other base page functionality.
    
    Attributes:
        GO_TO_LOGIN: Locator list for the login link/button
        LOGIN_USERNAME_INPUT: Locator list for username input field
        LOGIN_PASSWORD_INPUT: Locator list for password input field
        LOGIN_SUBMIT_BUTTON: Locator list for login submit button
        WELCOME_BACK_LABEL: Locator list for success confirmation element
    
    Methods:
        click_login_link(): Click the login link to access login form
        enter_username(): Enter username in the login form
        enter_password(): Enter password in the login form
        click_login(): Submit the login form
        is_welcome_back_visible(): Verify successful login
        login_flow(): Complete login workflow
    """

    GO_TO_LOGIN = [
        {'type': 'css', 'value': 'a[href*="rt=account/login"]'},
        {'type': 'xpath', 'value': '//a[normalize-space()="Login or register"]'},
        {'type': 'xpath', 'value': '//a[contains(text(),"Login")]'},
        {'type': 'xpath', 'value': '//li/a[contains(@href,"account/login")]'}
    ]
    """
    Locators for the login link/button.
    
    Multiple strategies to find the login link on the homepage:
    1. CSS selector matching login route parameter
    2. XPath for "Login or register" link text
    3. XPath for "Login" link text
    4. XPath for login link in list items
    """

    LOGIN_USERNAME_INPUT = [
        {'type': 'css', 'value': '#loginFrm_loginname'},
        {'type': 'css', 'value': 'input[name="loginname"]'},
        {'type': 'xpath', 'value': '//input[@id="loginFrm_loginname"]'},
        {'type': 'xpath', 'value': '//input[@type="text" and @name="loginname"]'},
        {'type': 'css', 'value': 'input.form-control'}
    ]
    """
    Locators for the username input field.
    
    Multiple strategies to find the username input:
    1. CSS selector by ID
    2. CSS selector by name attribute
    3. XPath by ID
    4. XPath by type and name
    5. CSS selector by form-control class
    """

    LOGIN_PASSWORD_INPUT = [
        {'type': 'css', 'value': '#loginFrm_password'},
        {'type': 'css', 'value': 'input[name="password"]'},
        {'type': 'xpath', 'value': '//input[@id="loginFrm_password"]'},
        {'type': 'xpath', 'value': '//input[@type="password" and @name="password"]'},
        {'type': 'css', 'value': 'input.form-control'}
    ]
    """
    Locators for the password input field.
    
    Multiple strategies to find the password input:
    1. CSS selector by ID
    2. CSS selector by name attribute
    3. XPath by ID
    4. XPath by type and name
    5. CSS selector by form-control class
    """

    LOGIN_SUBMIT_BUTTON = [
        {'type': 'css', 'value': 'button[title="Login"]'},
        {'type': 'xpath', 'value': '//button[@type="submit" and @title="Login"]'},
        {'type': 'xpath', 'value': '//button[normalize-space()="Login"]'},
        {'type': 'xpath', 'value': '//button[i[contains(@class,"fa-lock")]]'},
        {'type': 'css', 'value': 'button.btn.btn-orange'}
    ]
    """
    Locators for the login submit button.
    
    Multiple strategies to find the submit button:
    1. CSS selector by title attribute
    2. XPath by type and title
    3. XPath by button text
    4. XPath by button icon class
    5. CSS selector by button classes
    """

    WELCOME_BACK_LABEL = [
        {'type': 'xpath', 'value': '//div[contains(@class,"menu_text") and contains(text(),"Welcome back")]'},
        {'type': 'css', 'value': 'div.menu_text'},
        {'type': 'xpath', 'value': '//div[@class="menu_text"]'}
    ]
    """
    Locators for the success confirmation element.
    
    Used to verify that login was successful:
    1. XPath for "Welcome back" text in menu
    2. CSS selector for menu text class
    3. XPath by menu text class
    """





    def click_login_link(self) -> None:
        """
        Click the login link to access the login form.
        
        This method clicks the primary login/register link on the homepage
        using the multi-locator fallback strategy defined in GO_TO_LOGIN.
        If the primary locator fails, it automatically tries alternative locators.
        
        Returns:
            None
        
        Raises:
            TimeoutError: If no locator in GO_TO_LOGIN can find the element
        
        Example:
            login_page.click_login_link()
        """
        self.click(self.GO_TO_LOGIN, "Login Link")

    def enter_username(self, username: str) -> None:
        """
        Enter username in the login form.
        
        This method types the provided username into the username input field
        using the multi-locator fallback strategy defined in LOGIN_USERNAME_INPUT.
        
        Args:
            username (str): The username to enter (e.g., "user@example.com")
        
        Returns:
            None
        
        Raises:
            TimeoutError: If no locator in LOGIN_USERNAME_INPUT can find the element
        
        Example:
            login_page.enter_username("john@example.com")
        """
        self.type(self.LOGIN_USERNAME_INPUT, username, "Username Input")

    def enter_password(self, password: str) -> None:
        """
        Enter password in the login form.
        
        This method types the provided password into the password input field
        using the multi-locator fallback strategy defined in LOGIN_PASSWORD_INPUT.
        
        Args:
            password (str): The password to enter
        
        Returns:
            None
        
        Raises:
            TimeoutError: If no locator in LOGIN_PASSWORD_INPUT can find the element
        
        Example:
            login_page.enter_password("MyPassword123")
        """
        self.type(self.LOGIN_PASSWORD_INPUT, password, "Password Input")

    def click_login(self) -> None:
        """
        Submit the login form.
        
        This method clicks the login submit button to submit the login credentials
        using the multi-locator fallback strategy defined in LOGIN_SUBMIT_BUTTON.
        
        Returns:
            None
        
        Raises:
            TimeoutError: If no locator in LOGIN_SUBMIT_BUTTON can find the element
        
        Example:
            login_page.click_login()
        """
        self.click(self.LOGIN_SUBMIT_BUTTON, "Login Submit Button")

    def is_welcome_back_visible(self) -> bool:
        """
        Verify that login was successful.
        
        Checks if the "Welcome back" confirmation element is visible on the page.
        This indicates that the login operation completed successfully.
        
        Uses the multi-locator fallback strategy defined in WELCOME_BACK_LABEL
        to locate the confirmation element.
        
        Returns:
            bool: True if "Welcome back" element is visible, False otherwise
        
        Example:
            if login_page.is_welcome_back_visible():
                print("Login successful!")
        """
        return self.is_visible(self.WELCOME_BACK_LABEL, "Welcome Back Label")

    

    def login_flow(self, username: str, password: str) -> bool:
        """
        Complete login workflow.
        
        Executes the entire login process in sequence:
        1. Clicks the login link
        2. Enters the username
        3. Enters the password
        4. Clicks the submit button
        5. Verifies successful login by checking for "Welcome back" message
        
        This is a higher-level method that combines all individual login steps
        into a single convenient method.
        
        Args:
            username (str): The username/email to use for login
            password (str): The password to use for login
        
        Returns:
            bool: True if login was successful (welcome message visible),
                  False otherwise
        
        Raises:
            TimeoutError: If any step fails to find required elements
        
        Example:
            login_page = LoginPage(driver)
            success = login_page.login_flow("user@example.com", "password123")
            assert success, "Login failed - welcome message not visible"
        
        Note:
            This method performs the complete login flow and returns the result
            of is_welcome_back_visible() for convenient assertion in tests.
        """
        self.click_login_link()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self.is_welcome_back_visible()
