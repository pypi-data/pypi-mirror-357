from .abstract_clickable_component import AbstractInputComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class TextInput(AbstractInputComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.TEXT_INPUT)

    def set_value(self, value: str):
        self.root_element.send_keys(value)
