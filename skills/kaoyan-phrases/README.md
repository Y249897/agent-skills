# kaoyan-phrases

从英文或中英混杂的材料里提取**考研英语固定搭配**，累计进一张 Excel 总表，交付 Anki CSV 与带高频标记的 Word 讲义。

只整理词组，不整理单词和词汇表。

## 它解决什么

真题解析里到处都是 `take account of`、`at the expense of`、`in terms of` 这类搭配，散落在句意和解析里，抄一遍很费时间；直接丢给模型，又容易把单词、专名、自由组合一起收进来。

这个技能把判断标准写死：一个片段能整体记住、整体替换，换掉其中一个词句意就错，才收。然后按固定流程落到三份文件里，下次新材料直接并入同一张表、频次累加。

## 产出

运行后在你的工作目录下生成 `kaoyan-phrases/`：

| 文件 | 内容 |
| --- | --- |
| `kaoyan-vocab.xlsx` | 「词组」页：词头 / 词组 / 频次 / 类型 / 释义；「处理记录」页：日期、来源、新增、更新、总条数 |
| `kaoyan-cards.csv` | Anki 基础卡导入用：`正面,背面,词头,频次,提示`，UTF-8 带 BOM |
| `kaoyan-phrases.docx` | 学习讲义：高频搭配 `★` + 黄底加粗；全表按词头归并 |

高频线 = 频次前 10% 分位，且不低于 3 次。

三份文件都在原文件上更新：总表只重写两张页，讲义就地更新统计行、高频段与表格，CSV 按总表重写同一路径。不新建日期文件，不在别处复制一套。

## 安装

把本目录复制到助手的技能目录：

```powershell
# DSH
Copy-Item . "$HOME\.dsh\skills\kaoyan-phrases" -Recurse
# Claude Code
Copy-Item . "$HOME\.claude\skills\kaoyan-phrases" -Recurse
```

技能清单立即刷新，无需重启。

## 用法

材料放进当前工作目录（粘贴文本、`.txt`、`.docx` 都行），然后让 agent 用这个技能。也可以直接跑脚本（需要 Python、`python-docx`、`openpyxl`）：

```powershell
python -B tools\build_kaoyan_vocab.py "材料.docx" --source "材料名"
```

首次运行建表，之后每次并入同一张表、累加频次。总表里还没有的搭配用 `--add "词组|词头|类型|释义"` 追加：

```powershell
python -B tools\build_kaoyan_vocab.py "材料.txt" --add "be captured by|capture|动词短语|被…记录；被…概括"
```

改过释义或格式后，按现有总表重写三个产出（不动频次）：

```powershell
python -B tools\build_kaoyan_vocab.py --refresh
```

自检三份产出是否一致：

```powershell
python -B tools\check_outputs.py
```

## 示例

[`examples/`](examples) 里是一份真实产出（106 条 / 频次 213 / 高频 11 条），可以直接打开看格式：

- `examples/kaoyan-vocab.xlsx`
- `examples/kaoyan-cards.csv`
- `examples/kaoyan-phrases.docx`

## 结构

```
SKILL.md                     工作流程与三条规则
references/01-input.md       输入入口
references/02-extract.md     提取标准与去重
references/03-script.md      脚本、频次口径、词头、追加、原文件更新
references/04-deliver.md     三份交付物、Word 规格、自检、收尾
references/05-quality.md     释义、边界、质量清单
references/06-example.md     完整示例
tools/build_kaoyan_vocab.py  统计、合并、三份产出
tools/check_outputs.py       输出自检
```

## License

MIT，见 [LICENSE](LICENSE)。
