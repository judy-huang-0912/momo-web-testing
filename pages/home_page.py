import re
from playwright.sync_api import Page, expect
HOME_URL = "https://www.momoshop.com.tw/main/Main.jsp"
class HomePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.search_input = page.get_by_test_id("header-search-input")
        self.search_button = page.get_by_test_id("header-search-button")

    def open(self) -> None:
        self.page.goto(HOME_URL, wait_until="domcontentloaded", timeout=60_000)

    def wait_for_search_input_ready(self) -> None:
        expect(self.search_input).to_be_visible(timeout=30_000)
        expect(self.search_input).to_be_enabled(timeout=30_000)
        expect(self.search_input).to_have_attribute(
            "placeholder", re.compile(r".+"), timeout=30_000
        )

    def get_placeholder_keyword(self) -> str:
        self.wait_for_search_input_ready()
        placeholder = self.search_input.get_attribute("placeholder")
        assert placeholder, "搜尋框應有預設 placeholder 文字"
        return placeholder

    def search(self, keyword: str) -> None:
        self.wait_for_search_input_ready()
        self.search_input.click()
        self.search_input.fill(keyword)
        expect(self.search_input).to_have_value(keyword, timeout=10_000)
        self._submit()

    def search_with_placeholder(self) -> str:
        keyword = self.get_placeholder_keyword()
        expect(self.search_input).to_have_value("", timeout=10_000)
        self._submit()
        return keyword

    def _submit(self) -> None:
        expect(self.search_button).to_be_visible(timeout=10_000)
        with self.page.expect_navigation(timeout=60_000):
            self.search_button.click()
