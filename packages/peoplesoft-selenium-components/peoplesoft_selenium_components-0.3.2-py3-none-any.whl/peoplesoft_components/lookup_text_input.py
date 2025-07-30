from selenium.webdriver import Keys

from .text_input import TextInput


class LookupTextInput(TextInput):
    def set_value(self, value: str):
        self.root_element.send_keys(value + Keys.TAB)
