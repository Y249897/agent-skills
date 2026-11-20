# 03 · 脚本

脚本在技能目录的 `tools/build_kaoyan_vocab.py`，下文记作 `$SKILL`。

```powershell
python -B "$SKILL\tools\build_kaoyan_vocab.py" "材料.docx" --source "材料名"
```

数据源是 `./kaoyan-phrases/kaoyan-vocab.xlsx` 的「词组」页：

1. 读出已有的全部条目
2. 统计本次材料里每条出现的次数
3. 累加频次、把本次新出现的搭配追加进表
4. 只重写「词组」「处理记录」两页，工作簿里其它页原样保留
5. 同步 `kaoyan-cards.csv`
6. 重写 `kaoyan-phrases.docx`：高频段加 ★ 与黄底加粗

## 原文件更新

三份产出都写回同一批文件：

- `kaoyan-vocab.xlsx`：只重写「词组」「处理记录」两页，其它页与格式保留。
- `kaoyan-phrases.docx`：在原文件上更新统计行、高频段与表格；新词组按词头顺序插入，已有行就地改频次与 ★。
- `kaoyan-cards.csv`：按总表重写同一路径。

产出目录跟随总表所在目录，不另建。

## 频次口径

- 含屈折形式：took on 计入 take on，brushed aside 计入 brush aside。
- 不含无关同形词：contempt 里的 tempt 不计入 tempt。
- 解析、提分点、例句里的出现都算，都是学习材料。
- 精确值交给脚本。

## 分组与词头

- 按**词头**分组，组内频次降序；CSV 按词头字母序，组内频次降序。
- 动词短语归动词：turn out / turn down 归 turn；介词、固定表达、名词搭配归首词，释义里点出搭配对象（narrow the gap 归 narrow，释义写「缩小（差距）」）。
- `be` / `a` 开头的被动语态与数量搭配取实义词：be aimed at → aim，be based on → base，a number of → number。

## 追加

本次材料里出现、总表还没有收的搭配，用 `--add` 写进总表，格式 `词组|词头|类型|释义`：

```powershell
python -B "$SKILL\tools\build_kaoyan_vocab.py" "材料.txt" --add "be captured by|capture|动词短语|被…记录；被…概括"
```

- 频次累计：并入一次加一次；本次没出现的行保持原频次。
- 材料里没出现也直接入表，频次记 1。
- 同一份材料只并一次，先看「处理记录」页确认。
- 输出列固定为：词头、词组、频次、类型、释义。

## 重新生成

改过释义或格式后，用 `--refresh` 按现有总表重写三个产出，频次与「处理记录」保持原样：

```powershell
python -B "$SKILL\tools\build_kaoyan_vocab.py" --refresh
```
