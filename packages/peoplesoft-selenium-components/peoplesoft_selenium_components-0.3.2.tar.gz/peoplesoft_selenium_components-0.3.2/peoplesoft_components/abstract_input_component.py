from contextlib import contextmanager

from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .base_component import BaseComponent
from selocity import resilient_cached_webelement, resilient_cached_webelements


class AbstractInputComponent(BaseComponent):
    @property
    @resilient_cached_webelement
    def body_element(self) -> WebElement:
        return self.driver.find_element(By.TAG_NAME, "body")

    @property
    @resilient_cached_webelements
    def _save_spinner_elements(self) -> list[WebElement]:
        return self.driver.find_elements(By.CSS_SELECTOR, "[id^='SAVED_win']")

    @property
    @resilient_cached_webelement
    def _processing_spinner_element(self) -> WebElement:
        return self.driver.find_element(By.ID, "processing")

    @classmethod
    def _find_by_label(cls, driver: WebDriver, label: str):
        xpath = f"//input[@id = //label[normalize-space(text()) = '{label}']/@for]"
        return cls(driver, (By.XPATH, xpath))

    @classmethod
    def _find_by_title(cls, driver: WebDriver, title: str):
        xpath = f"//input[@title = '{title}']"
        return cls(driver, (By.XPATH, xpath))

    @staticmethod
    def _raise_no_such_element(label):
        """Raises NoSuchElementException with a formatted message."""
        raise NoSuchElementException(f"Could not find any element with label or title: {label}")

    def _wait_for_spinner_or_navigation(self, original_url: str):
        """
        Two‑phase WebDriverWait that short‑circuits if URL changes.
        """
        def appeared_or_navigated(driver):
            # short‑circuit on nav
            if driver.current_url != original_url:
                return True
            # otherwise, spinner has shown
            try:
                return self._processing_spinner_element.is_displayed()
            except (StaleElementReferenceException, TimeoutException):
                return False

        # Phase 1: wait for spinner to appear or URL to change
        self.wait.until(appeared_or_navigated)

        # if URL changed before spinner ever showed, exit immediately
        if self.driver.current_url != original_url:
            return

        def gone_or_navigated(driver):
            # short‑circuit on nav
            if driver.current_url != original_url:
                return True
            # otherwise, spinner has disappeared
            try:
                return not self._processing_spinner_element.is_displayed()
            except (StaleElementReferenceException, TimeoutException):
                return True

        # Phase 2: wait for spinner to disappear or URL to change
        self.wait.until(gone_or_navigated)

    def _wait_for_saved_spinner(self):
        """Waits for 'SAVED_win' elements to transition from `display:block` to `display:none`."""

        def all_elements_display_block(_):
            """Checks if all elements with ID starting with 'SAVED_win' have `display:block`."""
            return any(
                "display:block"
                in (el.get_attribute("style") or "").replace(" ", "").lower()
                for el in self._save_spinner_elements
            )

        def all_elements_display_none(_):
            """Checks if all elements with ID starting with 'SAVED_win' have `display:none`."""
            return all(
                "display:none"
                in (el.get_attribute("style") or "").replace(" ", "").lower()
                for el in self._save_spinner_elements
            )

        # Wait for elements to reach `display:block`
        try:
            self.wait.until(
                all_elements_display_block,
                message="Saved spinner never appeared.",
            )
        except TimeoutException:
            return  # Exit early if it never appeared

        # Wait for elements to transition to `display:none`
        self.wait.until(
            all_elements_display_none,
            message="'display:block' elements did not transition to 'display:none' in time.",
        )
