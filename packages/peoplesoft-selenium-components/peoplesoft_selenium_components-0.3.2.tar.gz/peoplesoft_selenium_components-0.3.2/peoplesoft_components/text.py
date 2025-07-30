from .base_component import BaseComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Text(BaseComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.TEXT)
