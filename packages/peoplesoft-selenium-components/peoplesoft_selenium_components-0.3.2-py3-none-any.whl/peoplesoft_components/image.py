from .base_component import BaseComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Image(BaseComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.IMAGE)
