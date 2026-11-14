# Stage 6 — 原始來源 Ingest 可重現性補強

- 日期：2026-11-14（亞洲台北）
- 完成項目：建立 `scripts/ingest_original_web.py`，具備 manifest URL 下載、HTML 正文解析、篇章內容長度檢查、SHA-256、逐篇日誌、Gate A 最低五篇門檻。
- 模擬測試：`python scripts/test_original_ingest.py`，6/6 自創 HTML 測試頁通過；**不代表實際來源匯入**。
- 真實連線嘗試：`python scripts/ingest_original_web.py --limit 1 --min-sources 1`，因 DNS/網路限制失敗，0/1。詳見 `ingest-original-live-latest.json`。
- 原有 Wiki 結構與基本計算 Lint：54/54 通過。
- 重要區分：已完成 6 篇來源筆記 Ingest（12 條知識主張）；未取得原始網頁全文，因此原始全文 Gate A 仍未達標。
- 後續必要條件：在合法且可連外環境對至少五篇真實來源成功執行 live 模式，或以合法取得的原始檔進行解析，並重新檢查 Wiki 引用；完成瀏覽器實測後才發布與繳交。
