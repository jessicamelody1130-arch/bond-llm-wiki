# Bond LLM Wiki：發佈前交接說明（2026-11-14）

## 目前已完成
- 六份來源的結構化筆記可重跑 ingest；八張 Wiki 來源卡、六篇教學概念頁
- 十頁 HTML 教學簡報及主題、來源對照
- Wiki lint 54/54、網站靜態預檢 35/35、JavaScript 模擬 14/14、真正 Chromium DOM 互動 19/19
- Loop/graph、失敗與修正紀錄、繳交草稿

## 尚未完成（勿填成已通過）
- 至少五篇原始網頁全文本地存檔與正式解析；目前為 0 篇，須在可連網的電腦執行 `python scripts/ingest_original_web.py --limit 6 --min-sources 5`，或先合法另存五篇 HTML 到 raw/saved-html，再執行 `python scripts/ingest_saved_html.py`。若來源禁止保存，須替換可用來源。
- GitHub Pages 公開發布：需帳號連接/授權，本站目前沒有公開網址。
- 真正公開站點跨頁連結與資源載入測試。

## 發布操作
GitHub 建立 public repo `bond-llm-wiki`，上傳此專案的內容（不要把資料夾再包一層）。進入 Settings → Pages → Deploy from a branch → main /(root)，完成後確認首頁、`/wiki/` 與 `/slides/` 均可在一般瀏覽器開啟。

## 提醒
原始全文若取得，保留於非公開研究用資料夾 `raw/private-original-archive`，不要公開上傳第三方完整原文。
