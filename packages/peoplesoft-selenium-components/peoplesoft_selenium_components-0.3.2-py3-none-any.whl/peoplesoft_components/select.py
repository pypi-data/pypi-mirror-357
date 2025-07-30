from selenium.webdriver.support.select import Select as SeleniumSelect

from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Select(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.SELECT)

    def select(self, text: str) -> None:
        return SeleniumSelect(self.root_element).select_by_visible_text(text)

    def select_by_index(self, index: int) -> None:
        return SeleniumSelect(self.root_element).select_by_index(index)

    @property
    def options(self) -> list[str]:
        return [option.text for option in SeleniumSelect(self.root_element).options]

    @property
    def selected_option(self) -> str:
        return SeleniumSelect(self.root_element).first_selected_option.text
