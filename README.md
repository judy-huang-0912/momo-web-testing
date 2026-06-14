# momo-web-testing

momo 購物網 E2E 測試（Playwright + pytest + Page Object Model）

## 專案結構

```
project/
├── pages/
│   ├── home_page.py
│   └── search_result_page.py
├── tests/
│   └── test_search.py
├── conftest.py
├── requirements.txt
└── README.md
```

## 安裝

```bash
# 使用 uv
uv sync
uv run playwright install chromium

# 或使用 pip
pip install -r requirements.txt
playwright install chromium
```

## 執行測試

```bash
# 全部測試
uv run pytest tests/ -v

# 平行執行（依 CPU 自動分配 worker，E2E 上限 4）
uv run pytest tests/ -v -n auto

# 指定 worker 數量
uv run pytest tests/ -v -n 4

# 關閉平行，改回單程序
uv run pytest tests/ -v -n 0

# 有頭模式
uv run pytest tests/ -v --headed

# 平行 + 有頭模式
uv run pytest tests/ -v -n auto --headed

# 透過 main.py 執行（支援 -n 參數）
uv run python main.py -n auto
uv run python main.py -n 4 --headed

# 單一測試
uv run pytest tests/test_search.py::test_search_iphone -v
```

## 測試案例

| 測試 | 說明 |
|------|------|
| `test_search_iphone` | 搜尋 iphone，驗證前三頁商品與圖片 |
| `test_search_no_results` | 搜尋不存在商品，驗證無結果頁面 |
| `test_search_filter_brand_and_capacity` | 搜尋 iphone，filter：品牌 + 容量篩選，驗證商品資料顯示 |
