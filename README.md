# 島嶼天氣 Island Weather

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://weather-website-6q48.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tests](https://github.com/Tmomoy/weather-website/actions/workflows/ci.yml/badge.svg)](https://github.com/Tmomoy/weather-website/actions/workflows/ci.yml)

> 一個為臺灣使用者設計的全端天氣服務。整合中央氣象署與 Open-Meteo，提供縣市搜尋、GPS 定位、36 小時預報、一週趨勢與即時雷達圖。

**[開啟線上作品](https://weather-website-6q48.onrender.com/)** · **[查看 JSON API](https://weather-website-6q48.onrender.com/api/v1/weather?city=%E8%87%BA%E5%8C%97%E5%B8%82)**

## 專案亮點

- **完整全端資料流**：原生 JavaScript 呼叫 Flask REST API，查詢時不需重新載入頁面。
- **雙資料源韌性**：優先使用中央氣象署，未設定金鑰或服務失敗時切換 Open-Meteo。
- **穩定的 API Client**：具備 TLS 驗證、連線逾時、有限重試、錯誤分類與記憶體快取。
- **安全設定**：API 金鑰只由環境變數取得，不寫入原始碼。
- **漸進增強**：JavaScript 非同步介面之外，仍保留伺服器渲染結果頁作為分享與無 JS 備援。
- **響應式體驗**：支援桌面與手機、GPS 失敗狀態、鍵盤操作及 reduced-motion。
- **可驗證品質**：21 個單元／路由測試與 GitHub Actions 自動檢查。

## 技術架構

```text
Browser
  ├─ Jinja page shell
  ├─ Vanilla JavaScript UI state
  └─ GET /api/v1/weather?city=...
                 │
                 ▼
Flask Routes ── WeatherService ── TTL Cache
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       CWA API Client      Open-Meteo fallback
             │                   │
             └─────────┬─────────┘
                       ▼
              Weather domain models
```

| 領域 | 技術 |
|---|---|
| Frontend | HTML5、CSS3、Vanilla JavaScript、Canvas |
| Backend | Python、Flask、Gunicorn |
| API | REST JSON、中央氣象署、Open-Meteo |
| Quality | Pytest、GitHub Actions |
| Deployment | Render、GitHub continuous deployment |

## 功能展示

- 22 縣市與常用行政區搜尋
- 「台／臺」與縣市後綴正規化
- 瀏覽器 GPS 定位與反向地理編碼
- 今明 36 小時天氣預報
- 一週高低溫與降雨趨勢
- Canvas 原生溫度圖表
- 中央氣象署雷達回波定時更新
- PWA manifest 與 Service Worker 靜態快取
- `/health` 部署健康檢查

## REST API

### 可搜尋地區

```http
GET /api/v1/locations
```

### 天氣預報

```http
GET /api/v1/weather?city=臺北市
```

回應範例：

```json
{
  "data": {
    "location": "臺北市",
    "updated_at": "2026-07-13T20:00:00+08:00",
    "current": {
      "summary": "局部多雲",
      "min_temp_c": 27,
      "max_temp_c": 34,
      "rain_probability": 20
    },
    "hourly": [],
    "daily": [],
    "warnings": []
  }
}
```

## 專案結構

```text
app/
├─ domain/                 # 天氣模型與地名規則
├─ routes/
│  ├─ api.py               # REST API
│  └─ weather.py           # HTML routes
├─ services/
│  ├─ cwa_client.py        # 中央氣象署 client 與 parser
│  ├─ open_meteo_client.py # 免金鑰備援資料源
│  └─ weather_service.py   # 查詢、快取與容錯流程
├─ __init__.py             # Flask application factory
└─ config.py               # 環境設定
static/                    # CSS、JavaScript、PWA
templates/                 # Jinja templates
tests/                     # Unit and route tests
wsgi.py                    # Production entry point
```

## 本機執行

需要 Python 3.10 以上版本。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

開啟 `http://127.0.0.1:10000`。未填入 `CWA_API_KEY` 時，系統會自動使用免金鑰備援預報。

## 環境變數

| 名稱 | 必填 | 說明 |
|---|---|---|
| `CWA_API_KEY` | 否 | 中央氣象署授權碼；未提供時使用備援 API |
| `SECRET_KEY` | 正式環境建議 | Flask secret key |
| `WEATHER_CACHE_TTL` | 否 | 天氣快取秒數，預設 600 |
| `CWA_CONNECT_TIMEOUT` | 否 | 連線逾時秒數 |
| `CWA_READ_TIMEOUT` | 否 | 讀取逾時秒數 |

## 測試

```powershell
python -m pytest -q
```

測試使用 fake service 與固定 payload，不依賴即時網路或 API 額度。

## 部署

正式環境使用：

```text
gunicorn wsgi:app
```

本專案包含 `render.yaml`，也可在 Render 以 Blueprint 建立服務。部署後可用 `/health` 進行健康檢查。

## 設計與工程取捨

- 維持小型 Flask 單體架構，避免為作品規模引入不必要的微服務複雜度。
- 前端採用原生 JavaScript，展示 DOM、Fetch API、無障礙與狀態管理能力。
- 將外部 API JSON 轉換為 domain model，讓模板與前端不依賴供應商資料格式。
- 允許部分資料成功，避免單一資料源問題讓整個頁面失效。

資料來源：[中央氣象署開放資料平臺](https://opendata.cwa.gov.tw/)與 [Open-Meteo](https://open-meteo.com/)。天氣預報僅供日常參考。
