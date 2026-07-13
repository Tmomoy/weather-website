# 島嶼天氣

以 Flask 與中央氣象署開放資料建立的臺灣天氣查詢網站，提供今明 36 小時、一週縣市預報、雷達回波與瀏覽器定位查詢。

## 功能

- 臺灣 22 縣市與常用行政區搜尋
- 「台／臺」及縣市後綴自動正規化
- 今明 36 小時與一週天氣預報
- 一週高低溫趨勢圖（無第三方圖表依賴）
- 雷達回波定時更新
- GPS 定位與明確錯誤狀態
- 外部 API timeout、有限重試、部分成功與記憶體快取
- 未設定中央氣象署金鑰時，自動使用免金鑰備援預報
- 響應式、鍵盤友善與 PWA 基礎支援

## 專案結構

```text
app/
├─ domain/       # 資料模型與地名規則
├─ routes/       # Flask 路由
├─ services/     # CWA API 與天氣查詢流程
├─ __init__.py   # application factory
└─ config.py     # 環境設定
static/          # CSS、JavaScript、manifest、service worker
templates/       # Jinja 頁面
tests/           # 單元與路由測試
app.py           # 本機啟動入口
wsgi.py          # 正式部署入口
```

完整設計決策請參閱 [優化框架](OPTIMIZATION_FRAMEWORK.md)。

## 本機啟動

需要 Python 3.10 以上版本。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

編輯 `.env`，將 `CWA_API_KEY` 改成你在中央氣象署開放資料平臺申請的授權碼，然後啟動。若尚未申請金鑰，系統會自動使用備援預報：

```powershell
python app.py
```

開啟 `http://127.0.0.1:10000`。健康檢查位於 `/health`。

## 測試

```powershell
python -m pytest
```

測試使用固定資料與假服務，不會消耗中央氣象署 API 額度。

## 部署

正式環境請設定 `CWA_API_KEY` 與隨機的 `SECRET_KEY`，再以 WSGI server 啟動：

```text
gunicorn wsgi:app
```

`PORT` 預設為 `10000`。外部 API 僅使用 HTTPS，且不應關閉 TLS 憑證驗證。

## 金鑰安全

舊版曾將 API 金鑰寫入 Git 歷史。請在中央氣象署平台撤銷舊金鑰並重新產生；只刪除目前檔案中的內容無法讓舊金鑰失效。新的金鑰只放在 `.env` 或部署平台的環境變數中，請勿提交到版本控制。

## 資料來源

- 中央氣象署 F-C0032-001：今明 36 小時天氣預報
- 中央氣象署 F-C0032-005：一週縣市天氣預報
- 中央氣象署雷達回波圖
- Open-Meteo Weather Forecast API（未設定 CWA 金鑰時的備援）
