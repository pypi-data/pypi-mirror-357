from .json_locators import GeneralLocatorStore, JsonComponent
from .text_input import TextInput


class PasswordInput(TextInput):
    general_locator = GeneralLocatorStore.get(JsonComponent.PASSWORD_INPUT)