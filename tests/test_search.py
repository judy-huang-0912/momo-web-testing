import re

import pytest
from playwright.sync_api import Page, expect

HOME_URL = "https://www.momoshop.com.tw/main/Main.jsp"
SEARCH_KEYWORD = "iphone"
PRODUCT_NAME_KEYWORDS = ("iphone", "ipad", "apple")
PAGES_TO_CHECK = [1, 2, 3]


def _name_matches_product_keyword(name: str) -> bool:
    name_lower = name.lower()
    return any(keyword in name_lower for keyword in PRODUCT_NAME_KEYWORDS)


def _fill_search_keyword(page: Page, keyword: str) -> None:
    search_input = page.get_by_test_id("header-search-input")
    expect(search_input).to_be_visible(timeout=30_000)
    expect(search_input).to_be_enabled(timeout=30_000)
    expect(search_input).to_have_attribute("placeholder", re.compile(r".+"), timeout=30_000)

    search_input.click()
    search_input.fill(keyword)
    expect(search_input).to_have_value(keyword, timeout=10_000)


def _submit_search(page: Page) -> None:
    search_button = page.get_by_test_id("header-search-button")
    expect(search_button).to_be_visible(timeout=10_000)

    with page.expect_navigation(timeout=60_000):
        search_button.click()


def _wait_for_search_page_ready(page: Page) -> None:
    page.wait_for_function(
        """() => {
            const hasProducts = document.querySelectorAll('h3.prdName').length > 0;
            const hasNoResult = document.body.innerText.includes('查無');
            return hasProducts || hasNoResult;
        }""",
        timeout=60_000,
    )

    if page.locator("h3.prdName").count() == 0:
        pytest.fail(f"搜尋「{SEARCH_KEYWORD}」未返回任何商品")


def _pagination(page: Page):
    return page.locator("ul.pagination").last


def _scroll_to_pagination(page: Page) -> None:
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    expect(_pagination(page)).to_be_visible(timeout=30_000)


def _get_current_page(page: Page) -> int:
    return page.evaluate(
        """() => {
            const pagination = document.querySelectorAll('ul.pagination');
            const selected = pagination[pagination.length - 1]
                ?.querySelector('a.pagination-link.selected');
            return selected ? Number(selected.innerText.trim()) : 0;
        }"""
    )


def _go_to_page(page: Page, page_num: int) -> None:
    if _get_current_page(page) == page_num:
        return

    _scroll_to_pagination(page)
    _pagination(page).locator("a.pagination-link:not(.pagination-arrow)").filter(
        has_text=re.compile(rf"^{page_num}$")
    ).click()

    page.wait_for_function(
        """(num) => {
            const paginations = document.querySelectorAll('ul.pagination');
            const selected = paginations[paginations.length - 1]
                ?.querySelector('a.pagination-link.selected');
            return selected?.innerText?.trim() === String(num);
        }""",
        arg=page_num,
        timeout=30_000,
    )
    _wait_for_search_page_ready(page)


def _assert_selected_page(page: Page, expected_page: int) -> None:
    _scroll_to_pagination(page)
    selected = _pagination(page).locator("a.pagination-link.selected")
    expect(selected).to_have_text(str(expected_page), timeout=10_000)


def _assert_image_loaded(page: Page, image) -> None:
    image.scroll_into_view_if_needed()
    expect(image).to_be_visible(timeout=10_000)
    expect(image).to_have_attribute("src", re.compile(r"goodsimg"))
    page.wait_for_function(
        "(img) => img.complete && img.naturalWidth > 0 && img.naturalHeight > 0",
        arg=image.element_handle(),
        timeout=15_000,
    )


def _verify_product_list(page: Page, page_num: int) -> None:
    product_cards = page.locator(".goodsUrl")
    product_count = product_cards.count()
    assert product_count > 0, f"第 {page_num} 頁搜尋結果應至少有一筆商品"

    for i in range(product_count):
        card = product_cards.nth(i)
        name = card.locator("h3.prdName").inner_text().strip()
        assert _name_matches_product_keyword(name), (
            f"第 {page_num} 頁第 {i + 1} 筆商品名稱應包含 {PRODUCT_NAME_KEYWORDS} 其中之一，實際為：{name}"
        )

        image = card.locator('img[src*="goodsimg"]').first
        _assert_image_loaded(page, image)


@pytest.mark.e2e
def test_search_iphone(page: Page):
    page.goto(HOME_URL, wait_until="domcontentloaded", timeout=60_000)

    _fill_search_keyword(page, SEARCH_KEYWORD)
    _submit_search(page)
    _wait_for_search_page_ready(page)

    for page_num in PAGES_TO_CHECK:
        _go_to_page(page, page_num)
        _assert_selected_page(page, page_num)
        _verify_product_list(page, page_num)
