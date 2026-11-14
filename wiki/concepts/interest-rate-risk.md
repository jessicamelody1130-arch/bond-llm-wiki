---
title: "市場殖利率與債券價格"
topic_id: interest-rate-risk
status: validated_for_wiki_draft
source_ids: [SRC-001, SRC-002, SRC-004, SRC-006]
last_checked_at: "2026-11-14"
---

# 市場殖利率與債券價格

## 為什麼價格反向變動？

固定票息債券未來付款不會因市場殖利率立即改變，但市場要求報酬率（折現率）上升時，固定現金流的現值下降，因此理論價格下降；相反亦然。[SRC-004: Why do interest rates affect bonds?] [SRC-006]

此處的「利率」應精確指用來為這張債券估值的**要求殖利率／折現率**；央行政策利率變動不等於所有債券 YTM 必然一比一變動。

## 可以檢驗的方向

在每一期現金流為非負，且至少有一期未來付款為正的簡化固定收益模型中，對折現率提高時價格下降；定價程式可用三組 `y` 值檢驗單調性。[SRC-006: Bond Valuation]

## 風險限制

單張固定票息債券的市值短期會受利率變動影響；但持有期間總報酬也與收取票息及再投資有關，不能把「利率上升造成價格下跌」等同「所有期間投資者都必然虧損」。[SRC-004: Are rising rates always bad for bonds?]


## 來源追溯

- [SRC-001](../sources/src-001.md)
- [SRC-002](../sources/src-002.md)
- [SRC-004](../sources/src-004.md)
- [SRC-006](../sources/src-006.md)
