# kaoyan-phrases

从英文或中英混杂的材料里提取**考研英语固定搭配**，累计进一张 Excel 总表，交付 Anki CSV 与带高频标记的 Word 讲义。

## 安装

把整个文件夹放进技能目录：

- DSH：`~/.dsh/skills/kaoyan-phrases/`
- Claude Code：`~/.claude/skills/kaoyan-phrases/`

技能清单立即刷新，无需重启。

## 用法

材料放进当前工作目录（粘贴文本、`.txt`、`.docx` 都行），让 agent 用这个技能；也可以在装有 python、python-docx、openpyxl 的环境里直接跑：

```powershell
python -B "<技能目录>\tools\build_kaoyan_vocab.py" "材料.docx" --source "材料名"
```

首次运行建表，之后每次并入同一张表、累加频次。新搭配与要移除的条目和材料**一条命令**处理（`--add` 可重复）：

```powershell
python -B "<技能目录>\tools\build_kaoyan_vocab.py" "材料.txt" --source "每日一题" `
  --add "follow up|follow|动词短语|跟进；采取后续行动" `
  --add "cut costs|cut|动词短语|削减开支" `
  --drop "take action"
```

同一来源名再次运行会被拦下（退出码 3），防止同一份材料并两次把频次翻倍；确要重并加 `--force`。

改过格式或释义后，按现有总表重写三个产出（不动频次）：

```powershell
python -B "<技能目录>\tools\build_kaoyan_vocab.py" --refresh
```

产出落在 `./kaoyan-phrases/`（已有总表时跟随总表所在目录）：

| 文件 | 内容 |
| --- | --- |
| `kaoyan-vocab.xlsx` | 「词组」页：词头/词组/频次/类型/释义；「处理记录」页：日期、来源、新增、更新、删除、总条数 |
| `kaoyan-cards.csv` | Anki 基础卡导入用：`正面,背面,词头,频次,提示` |
| `kaoyan-phrases.docx` | 学习讲义：高频段 `★` + 黄底加粗；全表按词头归并 |

高频线 = 频次前 10% 分位，且不低于 3 次。

三份文件都在原文件上更新：总表只重写两张页，讲义就地更新统计行、高频段与表格，CSV 按总表重写同一路径。

## 自检

```powershell
python -B "<技能目录>\tools\check_outputs.py"
```

核对 CSV、总表、Word 三者一致（条数、顺序、频次、字段、`★` 条数），退出码 0 即通过。

## 结构

```
SKILL.md                     工作流程与三条规则
references/01-input.md       输入入口
references/02-extract.md     提取标准与去重
references/03-script.md      脚本、频次口径、词头、追加与删除、刷新
references/04-deliver.md     三份交付物、自检、收尾
references/05-quality.md     释义、边界、质量清单
references/06-example.md     完整示例
tools/build_kaoyan_vocab.py  统计、合并、三份产出
tools/check_outputs.py       输出自检
```

## License

MIT，见 [LICENSE](LICENSE)。
