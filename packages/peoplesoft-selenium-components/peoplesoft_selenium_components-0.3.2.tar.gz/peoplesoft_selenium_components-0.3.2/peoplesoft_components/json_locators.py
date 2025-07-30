import json
from enum import Enum
from pathlib import Path
from typing import TypedDict

_json_path = Path(__file__).resolve().parent / "components.json"
_locators_data = json.loads(_json_path.read_text(encoding="utf-8"))

_json_locators = {
    key.lower().replace("_", ""): {
        "components": value.get("components", []),
        "labels": value.get("labels", [])
    }
    for key, value in _locators_data.items()
}


class ComponentLocator(TypedDict):
    components: list[str]
    labels: list[list[str]]


class JsonComponent(Enum):
    TABLE = "Table"
    TILE = "Tile"
    PASSWORD_INPUT = "PasswordInput"
    TOGGLE_SWITCH = "ToggleSwitch"
    LOOKUP_TEXT_INPUT = "LookupTextInput"
    DROPDOWN_BUTTON = "DropdownButton"
    SELECT = "Select"
    TEXT_INPUT = "TextInput"
    CHECKBOX = "Checkbox"
    BUTTON = "Button"
    LINK = "Link"
    IMAGE = "Image"
    TEXT = "Text"


class GeneralLocatorStore:

    @classmethod
    def get(cls, component_name: JsonComponent, default: ComponentLocator | None = None) -> ComponentLocator:
        key = component_name.value.lower().replace("_", "")
        if key in _json_locators:
            return _json_locators[key]
        if default is not None:
            return default
        raise ValueError(f"No locator found for '{component_name}'")
