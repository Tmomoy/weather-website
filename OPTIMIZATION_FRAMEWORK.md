# 台灣天氣系統優化框架

## 1. 優化目標

本次重構以「先恢復可運行，再改善架構」為原則，目標如下：

1. 恢復所有中文內容與 Python、Jinja 語法，讓應用能正常啟動。
2. 移除寫死的中央氣象署 API 金鑰，改由環境變數管理。
3. 將路由、外部 API、資料轉換、地區資料與畫面拆分，降低耦合。
4. 為外部請求加入 TLS 驗證、逾時、錯誤處理與有限重試。
5. 提供一致的查詢、載入、空資料與錯誤狀態。
6. 建立自動化測試與基本品質檢查，避免重構後功能退化。
7. 改善響應式版面、無障礙、載入速度與 PWA 行為。

## 2. 目前主要問題

| 層級 | 問題 | 影響 | 優先度 |
|---|---|---|---|
| 可運行性 | `app.py`、`taiwan_districts.py` 與模板出現編碼及語法損壞 | 應用無法可靠啟動 | P0 |
| 安全 | API 金鑰寫在原始碼及 Git 歷史中 | 金鑰可能遭濫用 | P0 |
| 安全 | HTTP 請求使用 `verify=False` 並關閉警告 | 無法驗證伺服器身分 | P0 |
| 穩定性 | 外部請求沒有 timeout，且以廣泛 `Exception` 吞掉錯誤 | 請求可能卡住，使用者看不到真正原因 | P0 |
| 正確性 | 以陣列固定索引取得天氣元素 | API 欄位順序改變時資料會錯置 | P1 |
| 正確性 | 濕度固定為 60 | 呈現非真實資料 | P1 |
| 架構 | 路由同時負責驗證、API 呼叫、轉換與畫面資料 | 難以測試與維護 | P1 |
| 效能 | 七日預報下載整份全臺資料，沒有快取 | 回應慢且增加 API 負擔 | P1 |
| 前端 | 內嵌大量圖表程式、缺少狀態提示及輸入驗證 | 維護與使用體驗不佳 | P2 |
| PWA | Service Worker 未註冊，manifest 圖示使用外部網址 | 離線／安裝功能不完整 | P2 |

> 已寫入 Git 歷史的 API 金鑰應立即在中央氣象署平台撤銷並重新產生；只從目前檔案移除不足以保護舊金鑰。

## 3. 目標架構

```text
天氣/
├─ app/
│  ├─ __init__.py             # Flask application factory
│  ├─ config.py               # 環境變數與環境設定
│  ├─ routes/
│  │  └─ weather.py           # HTTP 輸入、輸出與狀態碼
│  ├─ services/
│  │  ├─ cwa_client.py        # 中央氣象署 API client
│  │  └─ weather_service.py   # 查詢流程與快取協調
│  ├─ domain/
│  │  ├─ models.py            # Weather、Forecast 等資料模型
│  │  └─ locations.py         # 地名正規化與行政區映射
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ index.html
│  │  ├─ result.html
│  │  └─ error.html
│  └─ static/
│     ├─ css/app.css
│     ├─ js/app.js
│     ├─ js/chart.js
│     ├─ icons/
│     ├─ manifest.json
│     └─ sw.js
├─ tests/
│  ├─ unit/
│  │  ├─ test_locations.py
│  │  ├─ test_cwa_parser.py
│  │  └─ test_weather_service.py
│  └─ integration/
│     └─ test_routes.py
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ README.md
└─ wsgi.py                     # 部署入口
```

小型 Flask 專案不需要一開始拆成微服務；以上結構保留單體部署的簡單性，同時讓外部 API 與網頁路由可以分別測試。

## 4. 模組責任

### Route 層

- 接收並驗證城市或行政區輸入。
- 呼叫 `WeatherService`，不直接呼叫 `requests`。
- 將成功、查無資料與外部服務失敗映射為明確畫面及狀態碼。

### Service 層

- 組合即時、36 小時與七日預報。
- 設定短效快取，避免相同地區重複下載資料。
- 回傳一致的 domain model，不讓模板依賴中央氣象署原始 JSON。

### API Client 層

- 統一處理 API base URL、授權、TLS、timeout 與回應驗證。
- 依 `elementName` 取值，不使用不穩定的固定索引。
- 將網路、HTTP、JSON 與資料格式錯誤轉為可辨識的例外。

### Domain 層

- 正規化「台／臺」、縣市後綴與行政區對應。
- 定義目前天氣、逐時預報、每日預報等資料結構。
- 保持純函式，方便單元測試。

### Template／前端層

- 模板只負責語意結構與顯示，不解析 API 資料。
- JavaScript 負責定位、圖表、雷達更新及 Service Worker 註冊。
- 所有互動提供載入中、成功、空資料與失敗狀態。

## 5. 主要資料流

```text
使用者輸入／GPS
       ↓
Route 驗證輸入
       ↓
地名正規化與行政區映射
       ↓
WeatherService 查詢快取
       ↓ 未命中
CWA Client 呼叫官方 API
       ↓
Parser 轉為 domain models
       ↓
Route 渲染結果或錯誤頁
```

## 6. 分階段執行

### Phase 0：恢復基線（P0）

- 從最後一個中文及語法仍完整的 Git 版本恢復受損內容。
- 補齊殘缺的 Jinja 標籤並確認 Flask 可啟動。
- 建立 smoke test：首頁 200、合法查詢可渲染、錯誤不造成 500。

驗收：Python 可編譯、模板可載入、首頁與結果頁可開啟。

### Phase 1：安全與設定（P0）

- 使用 `CWA_API_KEY` 環境變數，新增 `.env.example`，禁止提交 `.env`。
- 撤銷目前外洩金鑰並更換。
- 恢復 TLS 驗證，設定 connect/read timeout。
- 對日誌隱藏金鑰與敏感查詢參數。

驗收：原始碼不含金鑰；缺少設定時啟動或請求會得到清楚錯誤。

### Phase 2：後端分層（P1）

- 建立 application factory、config、route、service、client 與 domain。
- 將 API JSON 解析改為名稱導向。
- 移除假濕度；若資料源沒有濕度，就不顯示該圖表。
- 統一輸入驗證、錯誤類型與日誌格式。

驗收：Route 測試不需連網；parser 可用固定 fixture 完整測試。

### Phase 3：效能與韌性（P1）

- 依資料更新頻率設定記憶體快取 TTL。
- 可平行取得互不相依的預報資料，並允許部分結果成功。
- 對暫時性錯誤做有限次數重試，不重試輸入或授權錯誤。
- 使用 Session／連線池，量測 API 與整體回應時間。

驗收：相同查詢的快取命中不再次呼叫外部 API；單一資料源失敗時仍可呈現其他資料。

### Phase 4：前端與體驗（P2）

- 建立共用 `base.html`，移除重複標記與內嵌 JavaScript。
- 建立 mobile-first 響應式版面、輸入建議與清楚的錯誤訊息。
- 圖表增加單位、完整日期時間、鍵盤操作與文字替代資訊。
- GPS 加入不支援、拒絕授權與反向地理編碼失敗處理。
- 雷達圖增加 `alt`、載入失敗狀態與合理更新策略。

驗收：手機與桌面皆無水平捲動；鍵盤可完成查詢；錯誤狀態可理解。

### Phase 5：PWA、品質與部署（P2）

- 使用本地 icon，註冊 Service Worker，定義靜態資源快取策略。
- 增加測試、lint、格式化與部署前檢查。
- README 補上本機啟動、環境變數、測試與部署說明。
- Gunicorn 使用 `wsgi:app`，提供 health endpoint 與結構化日誌。

驗收：乾淨環境可依 README 啟動；測試全數通過；部署平台可健康檢查。

## 7. 對外介面草案

```python
class CwaClient:
    def get_36_hour_forecast(self, city: str) -> dict: ...
    def get_weekly_forecast(self, city: str) -> dict: ...

class WeatherService:
    def get_weather(self, location: str) -> "WeatherReport": ...

def normalize_location(value: str) -> str: ...
```

`WeatherReport` 建議包含：

- `location`
- `observed_or_forecast_at`
- `summary`
- `temperature_c`
- `rain_probability_percent`
- `hourly_forecasts`
- `daily_forecasts`
- `warnings`

## 8. 測試框架

- 地名：台／臺、完整縣市、缺少後綴、行政區、空白與未知地名。
- Parser：欄位順序改變、缺欄位、空陣列、非數字、API 錯誤格式。
- Client：timeout、401／403、429、5xx、非 JSON 回應。
- Service：快取命中、部分資料源失敗、完整失敗。
- Route：首頁、合法查詢、非法查詢、外部服務失敗與 HTML escaping。
- 前端：定位拒絕、網路失敗、圖表無資料、窄螢幕與鍵盤操作。

外部 API 測試應使用 mock／fixture，避免測試結果依賴即時網路與 API 額度。

## 9. 完成定義

- 原始碼中沒有 API 金鑰，也沒有停用 TLS 驗證。
- 核心流程有測試，且測試不依賴即時中央氣象署服務。
- 所有外部請求有 timeout、可觀察錯誤與合理的快取策略。
- 不呈現捏造資料；缺值以明確的無資料狀態表示。
- 手機、桌面與鍵盤操作皆可完成主要查詢流程。
- 新開發者可只依 README 在乾淨環境啟動、測試與部署。

## 10. 建議執行順序

下一步先完成 Phase 0 與 Phase 1，建立一個可運行且安全的基線；接著再做後端分層。這樣每一階段都能獨立驗證，也較容易找出重構造成的回歸。
