# Gate C：鍵盤導覽回歸測試（實際執行）

- **初次狀態：FAIL**。以 Node.js 模擬 DOM 執行 `scripts/test_interactions_offline.cjs`，測試 `keyboard_when_button_focused` 失敗。原程式將所有 `BUTTON` 焦點都排除，造成使用者按下一頁按鈕後，箭頭鍵不能切換。
- **修改位置：** `slides/script.js`。將焦點排除範圍從 `INPUT,BUTTON,TEXTAREA` 調整為 `INPUT,TEXTAREA,SELECT`；對輸入欄位保留預設鍵盤行為，按鈕獲焦時仍可換頁。
- **重新測試：** 重新執行同一測試，12/12 通過。測試是 Node.js DOM 模擬，非真實 Chromium 瀏覽器測試。
- **流程調整：** 在 HTML 生成後的 Gate C，加入按鈕獲焦時的鍵盤測試作為發布前固定檢查。
