---
title: "債券定價與利率敏感度範例"
topic_id: numeric-examples
status: validated_for_wiki_draft
source_ids: [SRC-006, SRC-007]
last_checked_at: "2026-11-14"
---

# 債券定價與利率敏感度範例

## 可重現教學案例（依 Wiki 定價公式自行計算）

假設：面額 `F=1000`；年票面利率 `c=4%`；年付息 `m=1`；剩餘 `N=5` 年；為一般固定票息債券；估值日恰為付息日；無違約與交易成本。

- 每年票息 `C=40`。
- 對 `y=3%、4%、5%` 分別使用 `P=sum C/(1+y)^t+F/(1+y)^5`，比較債券理論價格。
- 對 `y=4%`，再依 [duration](duration.md) 的公式計算 Macaulay Duration、Modified Duration。
- 改變 `y` 時必須固定其他條件，並記錄理論價格與 Duration 的近似誤差。

數值計算來源：以 [SRC-006: Bond Valuation] 之折現模型及 [SRC-007: Duration measures] 之 Duration 定義為基礎的**自製計算案例**，不是原文給出的相同範例。


## 來源追溯

- [SRC-006](../sources/src-006.md)
- [SRC-007](../sources/src-007.md)
