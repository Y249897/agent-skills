---
name: kaoyan-phrases
description: 从英文或中英混合材料中提取考研英语的固定搭配与短语，累计进一张 Excel 总表，并交付 Anki CSV 与 Word 讲义；新材料并入同一张表，频次累加。当用户要整理固定搭配、做词组表、把阅读或真题里的短语摘成卡片、把新材料追加进词表时使用。
allowed-tools: Read, Write, Bash(python -B *)
---

# 考研词组提取

把材料里的固定搭配挑出来，累计进一张 Excel 总表，交付 Anki CSV 与带高频标记的 Word 讲义。

收的标准：一个片段能整体记住、整体替换，换掉其中一词句意就错。

脚本以**当前工作目录**为根，产出写进 `./kaoyan-phrases/`；已有总表时，产出跟随总表所在目录。

## 流程

| 步骤 | 文件 |
| --- | --- |
| 输入 | [references/01-input.md](references/01-input.md) |
| 提取 | [references/02-extract.md](references/02-extract.md) |
| 统计 | [references/03-script.md](references/03-script.md) |
| 交付 | [references/04-deliver.md](references/04-deliver.md) |
| 质量 | [references/05-quality.md](references/05-quality.md) |
| 示例 | [references/06-example.md](references/06-example.md) |

## 三条规则

1. **收整体记忆单位**：固定搭配与短语；单词、专名、自由组合、语法结构归各自的笔记。
2. **一张总表**：`./kaoyan-phrases/kaoyan-vocab.xlsx` 是唯一数据源，脚本读出条目、累加频次、写回同一文件；新搭配用 `--add` 写进总表。三份产出都在原文件里更新，不新建日期文件，不另建文件夹。每次运行同步 `kaoyan-cards.csv` 与 `kaoyan-phrases.docx`。
3. **交付看得见**：先跑 `tools/check_outputs.py`，再贴 CSV、给绝对路径、给文件卡片。
