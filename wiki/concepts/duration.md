---
title: "Macaulay Duration 與 Modified Duration"
topic_id: duration
status: validated_for_wiki_draft
source_ids: [SRC-005, SRC-007]
last_checked_at: "2026-11-14"
---

# Macaulay Duration 與 Modified Duration

## 兩種 Duration 不同

- **Macaulay Duration**：將債券現金流的折現值作為權重所計算的加權平均收款時間，通常以「年」表示。[SRC-007: Macaulay duration]
- **Modified Duration**：在固定現金流及 YTM 口徑下，衡量價格對殖利率小幅變動的相對敏感度；是一階近似。[SRC-007: Modified duration]

PIMCO 的 [SRC-005: What is duration?] 常以 **Effective Duration** 說明利率敏感度，不能把它當成 Macaulay Duration 或直接說三者相等。

## 公式

假設每年付息 `m` 次、共有 `N` 期、每期現金流 `CF_t`、每期折現率 `r=y/m`：

`P=sum_{t=1}^{N} CF_t/(1+r)^t`

`D_Mac=(1/m)*sum_{t=1}^{N} t*[CF_t/(1+r)^t]/P`  （年）

`D_Mod=D_Mac/(1+y/m)`

`ΔP/P ≈ -D_Mod*Δy` （殖利率變化 `Δy` 為小數形式的名目年利率變化）。[SRC-007]

## 限制

Modified Duration 線性近似在大幅利率變動下偏離真實的非線性價格曲線；若現金流隨利率改變，需考慮其他適用的 duration 度量。[SRC-005: limitations of duration] [SRC-007]


## 來源追溯

- [SRC-005](../sources/src-005.md)
- [SRC-007](../sources/src-007.md)
