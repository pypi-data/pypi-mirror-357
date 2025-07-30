from selenium.common import StaleElementReferenceException

from .abstract_input_component import AbstractInputComponent


class AbstractClickableComponent(AbstractInputComponent):
    def _is_submitting(self):
        try:
            if self._is_always_submitting is not None:
                return self._is_always_submitting
            on_change_value = self.root_element.get_attribute("onchange")
            href_value = self.root_element.get_attribute("href")
            values = [on_change_value, href_value]
            return any("submitaction" in (val or "").lower() for val in values)
        except StaleElementReferenceException:
            # The page has changed and the element is no longer attached!
            return False

    def click(self):
        original_url = self.driver.current_url
        self.root_element.click()
        if self._is_submitting():
            self._wait_for_spinner_or_navigation(original_url)

    def click_with_save_spinner(self):
        self.click()
        self._wait_for_saved_spinner()
