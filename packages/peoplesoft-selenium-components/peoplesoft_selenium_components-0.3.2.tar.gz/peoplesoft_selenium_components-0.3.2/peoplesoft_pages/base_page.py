import inspect
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.expected_conditions import D, T
from selenium.webdriver.support.ui import WebDriverWait


class PageTitleNotFoundError(Exception):
    """Custom exception for when the page title is not found."""

    pass


class BaseUrlNotSetError(Exception):
    """Custom exception for when the PEOPLESOFT_BASE_URL has not been set."""

    pass


def no_page_wait(method):
    """
    Decorator to indicate that the wrapped method should bypass the page initialisation check.

    When a method is decorated with @no_page_wait, it will not trigger the _initialize method
    even if the page is not yet initialized. This can be useful for methods that do not require
    the full page to be loaded or initialized before being called.

    Usage:
        @no_page_wait
        def some_method(self):
            # Method implementation

    Args:
        method (callable): The method to be decorated.

    Returns:
        callable: The decorated method with the no_page_wait attribute set to True.
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        return method(*args, **kwargs)

    wrapper.no_page_wait = True
    return wrapper


class BasePage(ABC):
    def __init__(
        self,
        driver: WebDriver,
        timeout: int = 10,
    ):
        """
        Initialises the BasePage instance.

        Args:
            driver:         Webdriver instance being used.
            timeout:        Maximum time to wait for elements or conditions, in seconds.
        """
        self.driver = driver
        self.timeout = timeout
        self._initialized = False

    def _initialize(self) -> None:
        self._initialized = True
        try:
            self._verify_page_title()
            logging.info(f'"{self.page_title}" launched')
        except TimeoutException:
            error_msg = "Window title not found."
            logging.info(error_msg)
            raise PageTitleNotFoundError(error_msg)

    def _verify_page_title(self) -> None:

        def title_matches(driver):
            return self._clean_title(driver.title) == self.page_title

        try:
            self.wait_for(
                title_matches,
                timeout=self.timeout,
                message="Page title mismatch or not found",
            )
        except TimeoutException:
            actual_title = self._clean_title(self.driver.title)
            error_msg = f"Title mismatch. Expected: '{self.page_title}', Actual: '{actual_title}'"
            logging.info(error_msg)
            raise PageTitleNotFoundError(error_msg)

    def __getattribute__(self, attr: str) -> Any:
        if attr in {"_initialized", "_initialize", "__class__", "__init__"}:
            return object.__getattribute__(self, attr)

        if not object.__getattribute__(self, "_initialized"):
            attr_obj = object.__getattribute__(self, attr)
            if inspect.ismethod(attr_obj) or inspect.isfunction(attr_obj):
                if getattr(attr_obj, "no_page_wait", False):
                    return attr_obj
                if not self._initialized:
                    self._initialize()

        return object.__getattribute__(self, attr)

    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean the title string by stripping whitespace and removing newlines."""
        return " ".join(title.split())

    def is_on_page(self) -> bool:
        """
        Checks if the driver is currently on the expected page.

        Returns:
            bool: True if the driver is on the expected page, False otherwise.
        """
        try:
            self._verify_page_title()
        except PageTitleNotFoundError:
            return False
        return True

    @property
    @abstractmethod
    def page_title(self) -> str:
        """
        Defines the expected title of the page.

        Returns:
            str: The expected title of the page.

        Note:
            - This should be the web browser's window/tab title.
        """
        ...

    @property
    @abstractmethod
    def relative_url(self) -> str:
        """
        The relative URL of the page (the part after removing the hostname and/or port.

        Returns:
            str: Relative URL.
        """
        ...

    @no_page_wait
    def go_to_page(self):
        base_url = os.getenv("PEOPLESOFT_BASE_URL")
        if not base_url:
            raise BaseUrlNotSetError("`PEOPLESOFT_BASE_URL` environment variable was not set.")
        self.driver.get(base_url + self.relative_url)

    @contextmanager
    @no_page_wait
    def wait_for_new_window(self, wait_time: int = 10) -> Generator[None, Any, None]:
        """
        Context manager to wait for a new browser window to open.

        Args:
            wait_time (int): Maximum time to wait in seconds for the new window to appear.
        """
        initial_windows = self.driver.window_handles
        yield
        self.wait_for(
            lambda d: len(d.window_handles) > len(initial_windows),
            timeout=wait_time,
            message=(
                "Waited for new window/tab to open, "
                f"but found {len(self.driver.window_handles)} windows/tabs "
                f"and there were {len(initial_windows)} windows/tabs "
                "before performing an action that should have opened a new window/tab."
            ),
        )
        new_window = (set(self.driver.window_handles) - set(initial_windows)).pop()
        self.driver.switch_to.window(new_window)

    @no_page_wait
    def wait_for(
        self,
        condition: Callable[[D], bool | T],
        timeout: int = None,
        message: str = "",
    ) -> Any:
        """
        Wait for a condition to be true.

        Args:
            condition: A callable that takes a WebDriver instance and returns a boolean.
            timeout: Maximum time to wait for the condition to be true.
            message: The message to show if the wait times out.

        Returns:
            The result of the condition callable.

        Raises:
            TimeoutException: If the timeout is reached before the condition is true.
        """
        return WebDriverWait(self.driver, timeout or self.timeout).until(condition, message)

    def __init_subclass__(cls, **kwargs):
        """
        Ensure that subclasses define `page_title` and `relative_url` as properties
        returning a str or None.
        """
        super().__init_subclass__(**kwargs)

        def validate_property(prop_name: str):
            if prop_name not in cls.__dict__:
                raise TypeError(f"Subclasses of {cls.__name__} must define a '{prop_name}' property of type 'str'")
            prop = getattr(cls, prop_name)
            if not isinstance(prop, property):
                raise TypeError(f"'{prop_name}' in class {cls.__name__} must be a property")
            if prop.fget is not None:
                value = prop.fget(cls)
                if not (isinstance(value, str) or value is None):
                    raise TypeError(f"Property '{prop_name}' in class {cls.__name__} must return a 'str' or be None")

        for prop_name in ("page_title", "relative_url"):
            validate_property(prop_name)
