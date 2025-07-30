import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selocity import resilient_cached_webelement

from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class IDNotFoundError(Exception):
    pass


class ToggleSwitch(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.TOGGLE_SWITCH)

    @property
    @resilient_cached_webelement
    def on_off_input(self) -> WebElement:
        on_click_value = self.root_element.get_attribute("onClick")
        match = re.search(r"getElementById\('([^']+)'\)", on_click_value)
        if match:
            input_id = match.group(1)
        else:
            raise IDNotFoundError("No element ID found in the onClick attribute.")
        return self.driver.find_element(By.ID, input_id)

    def check(self) -> None:
        checked_value = self.on_off_input.get_attribute("aria-checked")
        if checked_value.lower() == "true":
            return
        self.root_element.click()

    def uncheck(self) -> None:
        checked_value = self.on_off_input.get_attribute("aria-checked")
        if checked_value.lower() == "false":
            return
        self.root_element.click()