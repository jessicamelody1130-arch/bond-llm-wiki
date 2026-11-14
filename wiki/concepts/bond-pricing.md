---
title: "債券價格與現金流折現"
topic_id: bond-pricing
status: validated_for_wiki_draft
source_ids: [SRC-002, SRC-006]
last_checked_at: "2026-11-14"
---

# 債券價格與現金流折現

## 定價邏輯

固定票息債券的理論價格，是未來每期票息及到期本金折現到今天的現值。這是現金流折現（Discounted Cash Flow）應用。[SRC-006: Determining Bond Yield Using an Equation]

## 公式與假設

假設每年付息 `m` 次、剩餘 `N` 期、面額 `F`、年票面利率 `c`、名目年 YTM `y`，且每期折現率固定為 `r=y/m`：

`C=F*c/m`

`P=sum_{t=1}^{N} C/(1+r)^t + F/(1+r)^N`

等價於 `P=C*[1-(1+r)^(-N)]/r+F/(1+r)^N`（`r != 0`）；當 `r=0`，`P=CN+F`。[SRC-006]

這裡假設現金流固定、折現率相同、估值時間為付息日（不計應計利息），價格是簡化的理論全價。實務債券的報價、結算日、應計利息與不同殖利率慣例會影響實際價格。[SRC-002: Bonds and Notes]

## 溢價與折價

在其他條件一致、正票息、固定現金流與相同付息口徑下，若 `y<c` 則價格通常高於面額；`y=c` 平價；`y>c` 折價。[SRC-002: Bonds and Notes] [SRC-006: Relationship of Yield to Maturity and Coupon Rate]


## 來源追溯

- [SRC-002](../sources/src-002.md)
- [SRC-006](../sources/src-006.md)
