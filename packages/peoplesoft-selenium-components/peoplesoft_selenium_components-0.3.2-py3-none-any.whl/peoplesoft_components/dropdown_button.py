from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .json_locators import JsonComponent, GeneralLocatorStore
from .button import Button
from selocity import resilient_cached_webelement


class DropdownButton(Button):
    general_locator = GeneralLocatorStore.get(JsonComponent.DROPDOWN_BUTTON)
    _is_always_submitting = False

    @property
    @resilient_cached_webelement
    def menu_items_dropdown(self) -> WebElement:
        return self.driver.find_element(By.CLASS_NAME, "ps_popup-menu")

    def select(self, item_name: str):
        self.click()
        self.wait.until(lambda _: self.menu_items_dropdown.is_displayed())
        item = self.menu_items_dropdown.find_element(By.LINK_TEXT, item_name)
        item.click()
