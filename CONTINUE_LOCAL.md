# 下一步：補足五篇真正原始來源的 Ingest（供 Windows 使用）

目前不用立即操作。正式發布 GitHub 前，請在有網路的電腦依下列順序處理。

1. 解壓縮最新版 ZIP，確認有 `AGENTS.md`、`sources/manifest.json`、`scripts/`、`wiki/`、`slides/`。
2. 以瀏覽器依 `sources/manifest.json` 開啟至少五篇公開來源，使用「另存網頁 / HTML only」；另存後依來源 ID 命名 `src-001.html` 等。**不要使用測試檔。**
3. 於專案內新增 `raw/saved-html/`，放入至少五個來源的 HTML 檔。
4. 於專案根目錄執行：

   ```bash
   python -m pip install beautifulsoup4 requests
   python scripts/ingest_saved_html.py --min-sources 5
   ```

5. 開啟 `logs/runs/ingest-saved-html-latest.json`，確認至少五篇為 PASS、`gate_a_pass=true`，並手動比對其標題、重要段落與原始來源網址。
6. 重新執行 `python scripts/lint_wiki.py`、`python scripts/test_site_predeploy.py` 與 `node scripts/test_interactions_offline.cjs`；再用真實瀏覽器檢查 `slides/index.html`。
7. **不要上傳 `raw/saved-html/` 或 `raw/private-original-archive/` 到 GitHub**，它們是第三方網頁的本地研究副本，`.gitignore` 已排除。

如原網頁無法另存正文，請改用其他合法公開來源並先更新 manifest 和 Wiki 對照；不要將自創測試文件當成正式來源。
