# 示例产出

一份真实运行的产出，用来给第一次用的人看格式，也可以直接用：

```
kaoyan-vocab.xlsx    总表：106 条词组 / 65 个词头 / 频次合计 213
kaoyan-cards.csv     Anki 导入文件，UTF-8 带 BOM，五列
kaoyan-phrases.docx  学习讲义：高频 11 条（频次 ≥ 4）+ 全表
```

数据来自考研英语真题解析里的答案、考点与例句，外加一句每日长难句。脚本只统计、不改写原文。

自检这份示例：

```powershell
python -B ..\tools\check_outputs.py .
```

Word 讲义里 `★` 标出的是频次 ≥ 4 的条目：`be tempted to`、`because of`（6 次），`turn out`（5 次），以及 8 条 4 次的搭配。
