from typing import Type, TypeVar, cast, Generic
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .base_component import BaseComponent, ComponentSpec
from .json_locators import GeneralLocatorStore, JsonComponent
from selocity import resilient_cached_webelements

R = TypeVar("R", bound="Table.Row")
T = TypeVar("T", bound="Table[Any]")


class Table(BaseComponent, Generic[R]):
    general_locator = GeneralLocatorStore.get(JsonComponent.TABLE)

    @property
    @resilient_cached_webelements
    def row_elements(self) -> list[WebElement]:
        return self.root_element.find_elements(By.XPATH, ".//tr")

    @property
    @resilient_cached_webelements
    def header_elements(self) -> list[WebElement]:
        return self.root_element.find_elements(By.XPATH, ".//th")

    class Row:
        def __init__(self, row_element: WebElement, driver: WebDriver):
            self.row_element = row_element
            self.driver = driver

        def __repr__(self):
            return f"<{self.__class__.__name__} row_element={self.row_element}>"

    class Cell:
        def __init__(self, element: WebElement):
            self.element = element

        @property
        def text(self) -> str:
            return self.element.text.strip()

        def __repr__(self) -> str:
            return f"<Cell text='{self.text}'>"

    def get_row(self: "Table[R]", index: int) -> R:
        row_element = self.row_elements[index]
        return self.Row(row_element, self.driver)  # type: ignore

    def get_all_rows(self: "Table[R]") -> list[R]:
        return [self.Row(row, self.driver) for row in self.row_elements]  # type: ignore

    def get_column_headings(self) -> list[str]:
        return [header.text.strip() for header in self.header_elements]

    def get_column(self, heading_text: str) -> list["Table.Cell"]:
        col_index = None
        for i, header in enumerate(self.header_elements):
            if header.text.strip() == heading_text:
                col_index = i + 1
                break
        if col_index is None:
            raise NoSuchElementException(f"No column heading matching '{heading_text}'")

        cells = []
        for row in self.row_elements:
            try:
                cell_element = row.find_element(By.XPATH, f"./td[{col_index}]")
                cells.append(Table.Cell(cell_element))
            except NoSuchElementException:
                continue
        return cells

    @classmethod
    def from_definition(cls: Type[T], row_cls: Type[R]) -> Type[T]:
        """
        Dynamically creates a subclass of Table where the Row class resolves its components using specs.
        """
        class CustomRow(row_cls):
            def __init__(self, row_element: WebElement, driver: WebDriver):
                super().__init__(row_element, driver)
                for attr_name in dir(self.__class__):
                    value = getattr(self.__class__, attr_name)
                    if isinstance(value, ComponentSpec):
                        component_instance = value.resolve(driver, row_element)
                        setattr(self, attr_name, component_instance)

        class CustomTable(cls, Generic[R]):
            Row = CustomRow

        return cast(Type[T], CustomTable)
