from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Checkbox(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.CHECKBOX)

    def is_checked(self):
        return self.root_element.get_attribute("checked") == "checked"

    def check(self):
        if self.is_checked():
            return
        self.click()

    def uncheck(self):
        if not self.is_checked():
            return
        self.click()
