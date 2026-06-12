import pytest

from pages.home_page import HomePage
from pages.search_result_page import SearchResultPage

pytest_plugins = ["pytest_playwright"]


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "locale": "zh-TW",
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }


@pytest.fixture
def home_page(page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def search_result_page(page) -> SearchResultPage:
    return SearchResultPage(page)
