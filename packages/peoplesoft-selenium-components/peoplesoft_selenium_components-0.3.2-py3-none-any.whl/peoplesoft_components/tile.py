from .abstract_clickable_component import AbstractClickableComponent
from .json_locators import JsonComponent, GeneralLocatorStore


class Tile(AbstractClickableComponent):
    general_locator = GeneralLocatorStore.get(JsonComponent.TILE)
    _is_always_submitting = True
