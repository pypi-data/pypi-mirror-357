import time
from abc import ABC
from typing import Self, ClassVar, Type

from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from .json_locators import ComponentLocator
from selocity import resilient_cached_webelement

MAX_RETRIES = 3
RETRY_DELAY = 0.5


class ComponentSpec:
    def __init__(
        self,
        component_cls: Type["BaseComponent"],
        label: str | None = None,
        index: int | None = None,
        timeout: int = 10
    ):
        self.component_cls = component_cls
        self.label = label
        self.index = index
        self.timeout = timeout

    def resolve(self, driver: WebDriver, relative_webelement: WebElement) -> "BaseComponent":
        return self.component_cls.find_in(
            driver=driver,
            label=self.label,
            timeout=self.timeout,
            relative_webelement=relative_webelement,
            index=self.index,
        )


class BaseComponent(ABC):
    general_locator: ClassVar[ComponentLocator] = None
    _is_always_submitting: ClassVar[bool] = False

    def __init__(self, driver: WebDriver, locator: tuple[By, str], timeout: int = 10):
        self.driver = driver
        self.base_locator = locator
        self.wait = WebDriverWait(self.driver, timeout)

    @property
    @resilient_cached_webelement
    def root_element(self) -> WebElement:
        return self.driver.find_element(*self.base_locator)

    def is_displayed(self) -> bool:
        return self.root_element.is_displayed()

    @classmethod
    def find_by_locator(cls, driver: WebDriver, locator: tuple[By, str]) -> Self:
        return cls(driver, locator)

    @classmethod
    def _resolve_xpath(cls, driver: WebDriver, element: WebElement, rel_xpath: str) -> WebElement | None:
        if "#id" in rel_xpath:
            element_id = element.get_attribute("id")
            resolved_xpath = rel_xpath.replace("#id", element_id)
        else:
            resolved_xpath = rel_xpath
        try:
            if resolved_xpath == ".":
                return element
            if resolved_xpath.startswith("."):
                return element.find_element(By.XPATH, resolved_xpath)
            return driver.find_element(By.XPATH, resolved_xpath)
        except NoSuchElementException:
            return None

    @classmethod
    def _extract_label_text(cls, label_element: WebElement, strategy: str) -> str | None:
        if strategy == "text":
            return label_element.text.strip()
        if strategy == "string":
            return (label_element.get_attribute("innerText") or label_element.text or "").strip()
        if strategy.startswith("@"):
            return (label_element.get_attribute(strategy[1:]) or "").strip()
        return None

    @classmethod
    def _resolve_label_for_element(
        cls, driver: WebDriver, element: WebElement, label_rules: list[list[str]]
    ) -> list[str]:
        label_texts = []
        for rel_xpath, strategy in label_rules:
            label_element = cls._resolve_xpath(driver, element, rel_xpath)
            if not label_element:
                continue
            if label_text := cls._extract_label_text(label_element, strategy):
                label_texts.append(label_text)
        return label_texts

    @classmethod
    def get_all(cls, driver: WebDriver, timeout: int = 10, include_hidden: bool = False) -> list[Self]:
        if cls.general_locator is None:
            raise NotImplementedError(f"{cls.__name__} must define a class-level general_locator")

        for attempt in range(MAX_RETRIES):
            try:
                components = []
                for component_xpath in cls.general_locator["components"]:
                    elements = driver.find_elements(By.XPATH, component_xpath)
                    for index, element in enumerate(elements):
                        if not include_hidden:
                            try:
                                if not element.is_displayed():
                                    continue
                            except (NoSuchElementException, StaleElementReferenceException):
                                # Ignore this individual element and continue
                                continue
                        indexed_xpath = f"({component_xpath})[{index + 1}]"
                        components.append(cls(driver, (By.XPATH, indexed_xpath), timeout))
                return components
            except StaleElementReferenceException:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise

    @classmethod
    def find(cls, driver: WebDriver, label: str = None, timeout: int = 10, index: int = None) -> Self:
        if cls.general_locator is None:
            raise NotImplementedError("general_locator must be defined")

        components = cls.get_all(driver, timeout)
        if label:
            label_strategies = cls.general_locator.get("labels", [])
            matching = [
                c for c in components
                if any(label.strip() == text.strip()
                       for text in cls._resolve_label_for_element(driver, c.root_element, label_strategies))
            ]
        else:
            matching = components

        if not matching:
            raise NoSuchElementException(f"No {cls.__name__} component found{' with label ' + label if label else ''}")

        if index is not None:
            try:
                return matching[index]
            except IndexError:
                raise NoSuchElementException(f"No {cls.__name__} component found at index {index}")
        return matching[0]

    @classmethod
    def find_in(
        cls,
        driver: WebDriver,
        label: str | None = None,
        timeout: int = 10,
        relative_webelement: WebElement | None = None,
        index: int | None = None,
    ) -> Self:
        if cls.general_locator is None:
            raise NotImplementedError("general_locator must be defined")

        search_context = relative_webelement if relative_webelement is not None else driver
        label_strategies = cls.general_locator.get("labels", [])

        found = []
        for component_xpath in cls.general_locator["components"]:
            elements = search_context.find_elements(By.XPATH, component_xpath)
            for idx, element in enumerate(elements):
                if label:
                    label_texts = cls._resolve_label_for_element(driver, element, label_strategies)
                    if not any(label.strip() == text.strip() for text in label_texts):
                        continue  # No match
                indexed_xpath = f"({component_xpath})[{idx + 1}]"
                found.append(cls(driver, (By.XPATH, indexed_xpath), timeout))

        if not found:
            raise NoSuchElementException(f"No {cls.__name__} found{' with label ' + label if label else ''}")
        if index is not None:
            try:
                return found[index]
            except IndexError:
                raise NoSuchElementException(f"No {cls.__name__} found at index {index}")
        return found[0]

    @classmethod
    def spec(cls, label: str = None, index: int = None, timeout: int = 10):
        return ComponentSpec(cls, label=label, index=index, timeout=timeout)
