# 原始資料保存狀態

本階段使用網頁可讀資料建立逐篇的結構化來源卡，**未**將受版權保護網頁全文複製到本資料夾。

如取得具授權的 PDF / 原始資料，可放入此資料夾、更新 `sources/manifest.json` 中的 local_path / 資料狀態，並重新執行 Gate A。

## 可重跑的結構化筆記 Ingest（2026-11-14 新增）

`raw/curated/src-001.json` 至 `src-006.json` 為按原始網頁可公開核對之章節，**自行改寫**的中文來源筆記，非原始網頁全文。

從專案根目錄執行：

```bash
python scripts/ingest_curated.py
```

它會逐篇檢查來源 ID、原始網址、引用章節、筆記完整性及 claim ID，並輸出：

- `sources/ingested/src-*.json`：正規化來源紀錄
- `logs/runs/2026-11-14-curated-ingest.json`：每篇 PASS/FAIL、輸入檔 SHA-256
- `logs/runs/2026-11-14-claim-map.json`：來源章節與每條知識主張的對照

這是一個**可重跑的結構化知識匯入流程**，不能等同 `AGENTS.md` 第 3.2 節所要求的原始正文 Retrieve → Parse → Validate 完整鏈。若作業嚴格要求全文 ingest，應另外取得有保存授權的原始文件再進行。容器內無法連至外部網站，因此本次執行不包括自動抓取原網頁。

## 原始網頁正文 Ingest 管線（Stage 6）

新增 `scripts/ingest_original_web.py`。在可連外的本機或 Codespace 執行以下指令，才會向 manifest 所記載來源網址取得網頁正文、分段解析、計算雜湊，並逐篇寫入 Gate A 報告：

```bash
python -m pip install requests beautifulsoup4
python scripts/ingest_original_web.py --limit 6 --min-sources 5
```

- 成功時原始解析本文留在 `raw/private-original-archive/`，**不應發佈到 GitHub Pages**；`.gitignore` 已排除該資料夾。
- 執行日誌：`logs/runs/ingest-original-live-latest.json`；至少五筆成功才標記真正的原始正文 Gate A 通過。
- 若網站有登入牆、拒絕抓取或使用條款限制，應停止該來源並記錄失敗，改用可合法取得的材料。公開瀏覽不代表允許重製或公開再散布。
- 本環境網路抓取失敗，因此**尚未執行成功的 live 原始網頁 Ingest**。

本地可先測試解析器：

```bash
python scripts/test_original_ingest.py
```

該測試會生成**自創、非真實來源**的 HTML 測試頁，僅驗證解析、雜湊、欄位檢查與日誌能否正常運行；測試成功也不算任何一篇原始來源已 ingest。

## Alternative: ingest browser-saved original HTML

If command-line HTTPS requests are blocked, open each official URL listed in
`sources/manifest.json` in your browser, choose **Save page as > Webpage, HTML only**,
and put files in `raw/saved-html/` named `src-001.html`, `src-002.html`, etc.
The five files must be actual saved source pages, not the synthetic test fixtures.

Run from repository root:

```bash
python scripts/ingest_saved_html.py --min-sources 5
```

Review `logs/runs/ingest-saved-html-latest.json` for results. Check each saved
page against its claimed URL manually before reporting ingestion as verified.
Local source HTML and parsed full-text copies are research-only; they are excluded
from GitHub by `.gitignore` and must not be published. Do **not** rename the
synthetic `tests/fixtures/source-html/` files into this folder.
