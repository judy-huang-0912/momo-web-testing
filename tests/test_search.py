import pytest

from pages.home_page import HomePage
from pages.search_result_page import SearchResultPage

SEARCH_KEYWORD = "iphone"
INVALID_SEARCH_KEYWORD = "asdfgh123"
PRODUCT_NAME_KEYWORDS = ("iphone", "ipad", "apple")
PAGES_TO_CHECK = [1, 2, 3]

FILTER_PARENT_BRAND = "Apple"
FILTER_BRAND = "iPhone17Pro"
FILTER_CAPACITY = "256GB"


@pytest.mark.e2e
def test_search_iphone(home_page: HomePage, search_result_page: SearchResultPage):
    """情境：輸入有效關鍵字「iphone」搜尋，並切換至前三頁。

    驗證：每頁商品數量 > 0、名稱含 iphone/ipad/apple、價格有顯示、圖片正確載入。
    """
    home_page.open()
    home_page.search(SEARCH_KEYWORD)
    search_result_page.wait_for_products(SEARCH_KEYWORD)

    for page_num in PAGES_TO_CHECK:
        search_result_page.go_to_page(page_num, SEARCH_KEYWORD)
        search_result_page.assert_selected_page(page_num)
        search_result_page.verify_products_match_keywords(page_num, PRODUCT_NAME_KEYWORDS)


@pytest.mark.e2e
def test_search_default_placeholder(
    home_page: HomePage, search_result_page: SearchResultPage
):
    """情境：不輸入關鍵字，直接點搜尋，使用搜尋框預設 placeholder（如「亞培」）。

    驗證：商品數量 > 0、名稱含 placeholder 文字、價格有顯示、圖片正確載入。
    """
    home_page.open()
    keyword = home_page.search_with_placeholder()
    search_result_page.wait_for_products(keyword)
    search_result_page.verify_products_contain(keyword)


@pytest.mark.e2e
def test_search_no_results(home_page: HomePage, search_result_page: SearchResultPage):
    """情境：搜尋不存在的商品「asdfgh123」。

    驗證：顯示 momocoCry 圖示與「查無相關商品」提示文字。
    """
    home_page.open()
    home_page.search(INVALID_SEARCH_KEYWORD)
    search_result_page.wait_for_results()
    search_result_page.verify_no_results(INVALID_SEARCH_KEYWORD)


@pytest.mark.e2e
def test_search_filter_brand_and_capacity(
    home_page: HomePage, search_result_page: SearchResultPage
):
    """情境：搜尋 iphone 後，依品牌與容量篩選（Apple → iPhone17Pro → 256GB）。

    驗證：前幾頁商品的名稱、價格、圖片皆正確顯示。
    """
    home_page.open()
    home_page.search(SEARCH_KEYWORD)
    search_result_page.wait_for_products(SEARCH_KEYWORD)
    search_result_page.filter_by_brand_and_capacity(
        FILTER_PARENT_BRAND, FILTER_BRAND, FILTER_CAPACITY
    )
    search_result_page.verify_filtered_products_on_pages(
        SEARCH_KEYWORD, FILTER_BRAND, FILTER_CAPACITY, max_pages=3
    )
