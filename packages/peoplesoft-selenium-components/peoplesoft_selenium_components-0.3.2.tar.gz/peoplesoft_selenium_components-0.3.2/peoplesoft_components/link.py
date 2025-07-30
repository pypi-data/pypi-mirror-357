from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import GeneralLocatorStore, JsonComponent


class Link(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.LINK)
