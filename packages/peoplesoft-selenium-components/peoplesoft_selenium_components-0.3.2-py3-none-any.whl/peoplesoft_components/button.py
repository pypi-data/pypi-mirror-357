from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Button(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.BUTTON)

