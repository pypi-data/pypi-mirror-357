from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .base_component import BaseComponent
from .button import Button
from .dropdown_button import DropdownButton


class NavBar(BaseComponent):
    general_locator = (By.XPATH, "//div[contains(concat(' ', normalize-space(@class), ' '), ' ps_header_bar_cont ')]")

    # Default subcomponent definitions.
    # Each key will become an attribute on the NavBar instance.
    # The value is a tuple (ComponentClass, lookup_reference).
    # For example, Image.find_in(driver, label="Accessibility", relative_webelement=nav_bar.root_element)
    default_components = {
        "recently_visited": (Button, "Recently Visited"),
        "favorites": (Button, "Favorites"),
        "home": (Button, "Home"),
        "actions": (DropdownButton, "Actions")
    }

    def __init__(self, driver: WebDriver, components: dict = None, timeout: int = 10):
        """
        Initialize the NavBar.

        :param driver: The Selenium WebDriver.
        :param components: Optional dictionary to override default subcomponents.
           The dictionary should use the same keys as default_components with values
           of the form (ComponentClass, lookup). For example:
           {
               "home": (Image, "Custom Home Label"),
               "search": (Textbox, "Custom Search Label")
           }
        :param timeout: Timeout for locating the NavBar element.
        """
        super().__init__(driver, self.general_locator, timeout)

        comp_defs = self.default_components.copy()
        if components:
            comp_defs.update(components)

        for attr_name, (comp_cls, lookup) in comp_defs.items():
            component_instance = comp_cls.find_in(
                self.driver,
                label=lookup,
                relative_webelement=self.root_element
            )
            setattr(self, attr_name, component_instance)

    @classmethod
    def with_components(cls, driver: WebDriver, components: dict) -> Self:
        """
        Alternative class method for instantiating a NavBar with custom components.

        :param components: A dictionary to override default components.
        :return: An instance of NavBar with the merged component definitions.
        """
        return cls(driver, components)
