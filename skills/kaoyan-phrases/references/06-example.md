# 06 · 完整示例

## 输入（节选）

> Researchers have long tried to account for the gap between what people say and what they do. A growing body of evidence suggests that this discrepancy is subject to social pressure, and that it may give rise to systematic bias in surveys.

## 输出

```csv
正面,背面,词头,频次,提示
account for,"解释；占（比例）（动词短语）。例：Researchers have long tried to account for the gap between what people say and what they do.",account,1,宾语是 gap 时取「解释」义
a growing body of evidence,"越来越多的证据（名词搭配）。例：A growing body of evidence suggests that this discrepancy is subject to social pressure.",a,2,整体作主语，谓语用单数
be subject to,"受……影响；易遭受（形容词搭配）。例：This discrepancy is subject to social pressure.",be,2,后接名词
give rise to,"引起，导致（动词短语）。例：It may give rise to systematic bias in surveys.",give,1,宾语多为负面或中性结果
```

## 说明

- 四行对应四类：动词短语、名词搭配、形容词搭配、动词短语。
- `account for` 与 `a growing body of evidence` 的词头分别是 `account`、`a`，按字母序排在前。
- discrepancy、systematic 属单词，留给单词表。

按 [04-deliver.md](04-deliver.md) 交付即可。
