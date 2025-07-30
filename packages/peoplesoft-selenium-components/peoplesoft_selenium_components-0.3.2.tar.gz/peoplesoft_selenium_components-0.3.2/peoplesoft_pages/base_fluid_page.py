from peoplesoft_components import NavBar
from .base_page import BasePage


class BaseFluidPage(BasePage):
    @property
    def relative_url(self) -> str:
        ...

    @property
    def page_title(self) -> str:
        ...

    @property
    def nav_bar(self):
        return NavBar(self.driver)
