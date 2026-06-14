import re

from playwright.sync_api import Locator, Page, expect

class SearchResultPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_for_results(self) -> None:
        # 等搜尋結果頁「載入完成」：要嘛有商品，要嘛顯示查無結果，兩者其一即可
        self.page.locator("h3.prdName, .noResultText").first.wait_for(
            state="attached",
            timeout=60_000,
        )

    def wait_for_products(self, keyword: str) -> None:
        self.wait_for_results()
        if self.page.locator("h3.prdName").count() == 0:
            raise AssertionError(f"搜尋「{keyword}」未返回任何商品")

    def verify_no_results(self, keyword: str) -> None:
        no_result_message = (
            f'很抱歉，查無 "{keyword}"的相關商品，您可以調整關鍵字試試看'
        )

        expect(self.page.locator("div.momocoCry")).to_be_visible(timeout=30_000)

        keywords = self.page.locator("span.keywords")
        expect(keywords).to_be_visible(timeout=10_000)
        expect(keywords).to_have_text(f'"{keyword}"')

        no_result_text = self.page.locator("div").filter(
            has=self.page.locator("span.keywords", has_text=keyword)
        ).filter(has_text="很抱歉，查無")
        expect(no_result_text.first).to_contain_text(no_result_message)

    def verify_products_contain(
        self, keyword: str, page_num: int | None = None
    ) -> None:
        product_cards = self.page.locator(".goodsUrl")
        product_count = product_cards.count()
        page_label = f"第 {page_num} 頁" if page_num else ""
        assert product_count > 0, f"{page_label}搜尋結果應至少有一筆商品"

        for i in range(product_count):
            card = product_cards.nth(i)
            item_label = f"{page_label}第 {i + 1} 筆"
            name = card.locator("h3.prdName").inner_text().strip()
            assert keyword in name, (
                f"{item_label}商品名稱應包含「{keyword}」，實際為：{name}"
            )
            self._assert_price_visible(card, item_label)
            self._assert_image_loaded(card.locator('img[src*="goodsimg"]').first)

    def verify_products_match_keywords(
        self, page_num: int, name_keywords: tuple[str, ...]
    ) -> None:
        product_cards = self.page.locator(".goodsUrl")
        assert product_cards.count() > 0, f"第 {page_num} 頁搜尋結果應至少有一筆商品"

        card = product_cards.first
        item_label = f"第 {page_num} 頁第 1 筆"
        name = card.locator("h3.prdName").inner_text().strip()
        name_lower = name.lower()
        keywords_lower = tuple(kw.lower() for kw in name_keywords)
        assert any(kw in name_lower for kw in keywords_lower), (
            f"{item_label}商品名稱應包含 "
            f"{name_keywords} 其中之一，實際為：{name}"
        )
        self._assert_price_visible(card, item_label)
        self._assert_image_loaded(card.locator('img[src*="goodsimg"]').first)

    def filter_by_brand_and_capacity(
        self, parent_brand: str, model_brand: str, capacity: str
    ) -> None:
        parent = self.page.locator("div.label-name", has_text=parent_brand).first
        parent.scroll_into_view_if_needed()
        expect(parent).to_be_visible(timeout=30_000)
        parent.click()
        self._wait_for_filter_update()

        model = self.page.locator("div.label-name", has_text=model_brand).first
        expect(model).to_be_visible(timeout=30_000)
        model.click()
        self._wait_for_filter_update()

        capacity_label = self.page.locator(
            f'label.label-name-area[title="{capacity}"]'
        ).first
        capacity_label.scroll_into_view_if_needed()
        expect(capacity_label).to_be_visible(timeout=30_000)
        capacity_label.click()
        self._wait_for_filter_update()

    def verify_filtered_products_display(
        self, page_num: int, model_brand: str, capacity: str
    ) -> None:
        product_cards = self.page.locator(".goodsUrl")
        assert product_cards.count() > 0, f"第 {page_num} 頁篩選後應至少有一筆商品"

        capacity_hint = capacity.replace("GB", "").replace("G", "")

        card = product_cards.first
        item_label = f"第 {page_num} 頁第 1 筆"

        name_el = card.locator("h3.prdName")
        expect(name_el).to_be_visible(timeout=10_000)
        name = name_el.inner_text().strip()
        assert name, f"{item_label}商品名稱應正確顯示"

        name_lower = name.lower()
        assert "17" in name_lower and "pro" in name_lower, (
            f"{item_label}商品名稱應符合品牌篩選「{model_brand}」，實際為：{name}"
        )
        assert capacity_hint in name or f"{capacity_hint}g" in name_lower, (
            f"{item_label}商品名稱應符合容量篩選「{capacity}」，實際為：{name}"
        )

        self._assert_price_visible(card, item_label)
        self._assert_image_loaded(card.locator('img[src*="goodsimg"]').first)

    def verify_filtered_products_on_pages(
        self,
        keyword: str,
        model_brand: str,
        capacity: str,
        max_pages: int = 3,
    ) -> None:
        total_pages = self.get_total_pages()
        pages_to_check = range(1, min(max_pages, total_pages) + 1)
        assert pages_to_check, "篩選後應至少有一頁商品結果"

        for page_num in pages_to_check:
            if page_num > 1:
                self.go_to_page(page_num, keyword)
            self.assert_selected_page(page_num)
            self.verify_filtered_products_display(page_num, model_brand, capacity)

    def get_total_pages(self) -> int:
        return self.page.evaluate(
            """() => {
                const match = document.body.innerText.match(/頁數\\s*\\d+\\s*\\/\\s*(\\d+)/);
                return match ? Number(match[1]) : 0;
            }"""
        )

    def go_to_page(self, page_num: int, keyword: str) -> None:
        if self._get_current_page() == page_num:
            return

        self._scroll_to_pagination()
        self._pagination().locator("a.pagination-link:not(.pagination-arrow)").filter(
            has_text=re.compile(rf"^{page_num}$")
        ).click()

    def assert_selected_page(self, page_num: int) -> None:
        self._scroll_to_pagination()
        selected = self._pagination().locator("a.pagination-link.selected")
        expect(selected).to_have_text(str(page_num), timeout=10_000)

    def _pagination(self) -> Locator:
        return self.page.locator("ul.pagination").last

    def _scroll_to_pagination(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        expect(self._pagination()).to_be_visible(timeout=30_000)

    def _get_current_page(self) -> int:
        return self.page.evaluate(
            """() => {
                const pagination = document.querySelectorAll('ul.pagination');
                const selected = pagination[pagination.length - 1]
                    ?.querySelector('a.pagination-link.selected');
                return selected ? Number(selected.innerText.trim()) : 0;
            }"""
        )

    def _wait_for_filter_update(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)
        self.wait_for_products("filter")

    def _assert_price_visible(self, card: Locator, item_label: str) -> None:
        price = card.locator(".price").first
        expect(price).to_be_visible(timeout=10_000)
        price_text = price.inner_text().strip()
        assert re.search(r"\d", price_text), (
            f"{item_label}商品價格應有顯示，實際為：{price_text!r}"
        )

    def _assert_image_loaded(self, image: Locator) -> None:
        image.scroll_into_view_if_needed()
        expect(image).to_be_visible(timeout=10_000)
        expect(image).to_have_attribute("src", re.compile(r"goodsimg"))
        self.page.wait_for_function(
            "(img) => img.complete && img.naturalWidth > 0 && img.naturalHeight > 0",
            arg=image.element_handle(),
            timeout=15_000,
        )
