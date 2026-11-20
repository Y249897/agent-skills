"""从考研材料（.docx 或 .txt）里统计词组：去重、按词头分组、标出出现频次。

用法：python build_kaoyan_vocab.py <材料.docx|材料.txt> [输出目录] [--existing 总表.xlsx] [--source 材料名]
输出目录省略时默认 <当前工作目录>/kaoyan-phrases；--existing 省略时自动找该目录下已有的 kaoyan-vocab.xlsx。
产出：kaoyan-vocab.xlsx（筛选/排序，唯一总表）、kaoyan-cards.csv（Anki 导入）。
不落地中间纯文本，也不输出 markdown 表格。
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------- 数据

# (词头, 词组, 类型, 释义)
PHRASES = [
    # --- 2026-11-20 每日长难句
    ("capture", "be captured by", "动词短语", "被…记录；被…概括"),
    ("seek", "seek knowledge", "动词短语", "求知；探求知识"),
    ("dare", "dare to know", "固定表达", "敢于求知"),
    # --- s
    ("subscribe", "subscribe to", "动词短语", "赞同（观点、理论）；订阅"),
    ("attribute", "attribute to", "动词短语", "把……归因于"),
    ("contribute", "contribute to", "动词短语", "促成；有助于；是……的原因之一"),
    ("resort", "resort to", "动词短语", "求助于；诉诸（多指负面手段）"),
    # --- g
    ("go", "go after", "动词短语", "追求；谋求"),
    ("go", "go for", "动词短语", "选择；喜欢"),
    ("go", "go through", "动词短语", "经历；仔细检查"),
    ("go", "go over", "动词短语", "复习；仔细审查"),
    ("go", "go off", "动词短语", "爆炸；（电器）停止运转"),
    # --- w
    ("weigh", "weigh up", "动词短语", "权衡；估量"),
    ("ward", "ward off", "动词短语", "避开；抵御"),
    ("work", "work out", "动词短语", "算出；制定出；解决"),
    # --- t
    ("turn", "turn out", "动词短语", "结果是；证明是"),
    ("turn", "turn up", "动词短语", "出现；调大（音量）"),
    ("turn", "turn away", "动词短语", "避开；不准进入；拒绝"),
    ("turn", "turn over", "动词短语", "翻转；仔细考虑；移交"),
    ("turn", "turn off", "动词短语", "关掉（电器）"),
    ("turn", "turn down", "动词短语", "拒绝；调低（音量）"),
    ("take", "take account of", "动词短语", "考虑到；顾及"),
    ("take", "take into account", "动词短语", "考虑到；把……考虑在内"),
    ("take", "take on", "动词短语", "承担；呈现；雇佣"),
    ("take", "take off", "动词短语", "起飞；走红；脱下"),
    ("take", "take over", "动词短语", "接管；接手"),
    ("trap", "trap oneself in", "习语", "把自己困在……里；自愿困于"),
    # --- m
    ("make", "make up", "动词短语", "编造；弥补；组成；和好"),
    ("make", "make out", "动词短语", "辨认出；理解"),
    ("make", "make up for", "动词短语", "弥补；补偿"),
    ("make", "make the point", "动词短语", "提出（某一）观点"),
    ("miss", "miss out on", "动词短语", "错失；错过"),
    # --- p
    ("pick", "pick up", "动词短语", "捡起；学会；接人"),
    ("put", "put out", "动词短语", "扑灭；发布；生产"),
    ("pass", "pass over", "动词短语", "忽视；忽略；跳过"),
    # --- f
    ("figure", "figure out", "动词短语", "弄明白；搞清楚；算出"),
    ("fall", "fall for", "动词短语", "上当；听信；爱上"),
    ("fit", "fit in", "动词短语", "融入；相处融洽；合得来"),
    # --- b
    ("bring", "bring out", "动词短语", "使显现；出版；推出"),
    ("bring", "bring up", "动词短语", "抚养；提出（话题）"),
    ("bring", "bring about", "动词短语", "导致；引起"),
    ("brush", "brush aside", "动词短语", "漠视；不理会"),
    ("brush", "brush up", "动词短语", "温习；复习"),
    ("brush", "brush off", "动词短语", "不理睬；掸掉"),
    ("brush", "brush down", "动词短语", "刷干净"),
    ("bridge", "bridge the gap", "名词搭配", "弥合差距"),
    ("box", "box oneself in", "习语", "自我设限；画地为牢"),
    # --- g
    ("give", "give out", "动词短语", "分发；耗尽；发出"),
    ("give", "give away", "动词短语", "赠送；泄露"),
    ("guard", "guard against", "动词短语", "防范；防止"),
    ("get", "get rid of", "动词短语", "摆脱；除去"),
    ("get", "get over", "动词短语", "克服；从……中恢复"),
    # --- s
    ("set", "set out", "动词短语", "出发；动身；着手做（set out to do）"),
    ("set", "set aside", "动词短语", "留出；拨出；搁置"),
    ("set", "set back", "动词短语", "推迟；阻碍；使倒退"),
    ("set", "set about", "动词短语", "着手做；开始做"),
    ("set", "set forth", "动词短语", "阐明；陈述；出发"),
    ("sort", "sort out", "动词短语", "整理；梳理；解决"),
    ("single", "single out", "动词短语", "挑选出；找出"),
    ("stem", "stem from", "动词短语", "源于；由……造成"),
    # --- d
    ("dwell", "dwell on", "动词短语", "老是想着；纠结；详述"),
    ("drop", "drop out", "动词短语", "退学；退出；掉出"),
    ("draw", "draw a circle on the ground", "习语", "画地为牢（字面义）"),
    ("desire", "desire nothing more than", "固定表达", "只想要；最渴望"),
    ("define", "define ... as", "动词短语", "把……定义为"),
    # --- c
    ("carry", "carry out", "动词短语", "实施；执行；开展"),
    ("carry", "carry off", "动词短语", "赢得；成功完成；带走"),
    ("carry", "carry over", "动词短语", "延续；结转；遗留"),
    ("carry", "carry away", "动词短语", "使激动；带走"),
    ("catch", "catch on", "动词短语", "理解；流行起来"),
    ("catch", "catch up", "动词短语", "赶上；追上"),
    ("catch", "catch up with", "动词短语", "赶上；追上（接宾语）"),
    ("count", "count on", "动词短语", "依靠；指望"),
    ("call", "call off", "动词短语", "取消"),
    ("call", "call for", "动词短语", "需要；要求；号召"),
    ("call", "call up", "动词短语", "打电话；回忆起"),
    ("call", "call on", "动词短语", "拜访；号召"),
    ("come", "come up with", "动词短语", "想出；提出（方案）"),
    ("compensate", "compensate for", "动词短语", "补偿；弥补"),
    ("cater", "cater for", "动词短语", "迎合；满足需要"),
    ("cut", "cut off", "动词短语", "切断；中断；隔绝"),
    # --- a
    ("account", "account for", "动词短语", "解释；说明；占（比例）"),
    ("allow", "allow for", "动词短语", "考虑到；把……算在内"),
    ("abide", "abide by", "动词短语", "遵守；遵从"),
    ("aim", "be aimed at", "固定表达", "针对；旨在；以……为目的"),
    ("base", "be based on", "固定表达", "基于；以……为基础"),
    # --- h
    ("hold", "hold on", "动词短语", "坚持；稍等；抓住"),
    ("hold", "hold back", "动词短语", "抑制；隐瞒；阻止"),
    ("hold", "hold out", "动词短语", "坚持；伸出；维持"),
    ("hold", "hold off", "动词短语", "推迟；暂缓（计划、行动）"),
    # --- k
    ("keep", "keep to", "动词短语", "遵守；恪守（计划、时间表）"),
    ("keep", "keep up", "动词短语", "维持；保持；跟上"),
    ("keep", "keep one's end up", "习语", "（在困境中）不泄气；坚持不懈"),
    # --- r
    ("root", "root out", "动词短语", "找出；根除；铲除"),
    ("restrict", "restrict sb to", "动词短语", "把某人限制在……范围内"),
    ("result", "result in", "动词短语", "导致；造成"),
    ("result", "result from", "动词短语", "源于；由……造成"),
    ("replace", "replace A with B", "固定搭配", "以……取代……"),
    # --- n
    ("narrow", "narrow the gap", "名词搭配", "缩小差距"),
    ("nothing", "nothing more than", "固定表达", "只不过是；仅仅是"),
    ("number", "a number of", "固定表达", "若干；许多"),
    ("term", "a term of contempt", "名词搭配", "轻蔑之词"),
    ("tempt", "be tempted to", "固定表达", "想要；忍不住（做某事）"),
    ("in", "in favor of", "介词短语", "支持；赞成；有利于"),
    ("lie", "lie in", "动词短语", "在于；取决于"),
    ("because", "because of", "介词短语", "因为；由于"),
]

IRREGULAR = {
    "take": ["took", "taken", "takes", "taking"],
    "give": ["gave", "given", "gives", "giving"],
    "come": ["came", "comes", "coming"],
    "make": ["made", "makes", "making"],
    "get": ["got", "gotten", "gets", "getting"],
    "go": ["went", "gone", "goes", "going"],
    "hold": ["held", "holds", "holding"],
    "keep": ["kept", "keeps", "keeping"],
    "set": ["set", "sets", "setting"],
    "put": ["put", "puts", "putting"],
    "cut": ["cut", "cuts", "cutting"],
    "bring": ["brought", "brings", "bringing"],
    "catch": ["caught", "catches", "catching"],
    "draw": ["drew", "drawn", "draws", "drawing"],
    "fall": ["fell", "fallen", "falls", "falling"],
}

_L = r"(?<![A-Za-z])"
_R = r"(?![A-Za-z])"

SPECIAL = {
    "keep one's end up": _L + r"keep\w*\s+(?:one's|their|his|her|your|our|its)\s+end\s+up" + _R,
    "box oneself in": _L + r"box\w*\s+(?:oneself|yourself|himself|herself|themselves|myself)\s+in" + _R,
    "trap oneself in": _L + r"trap\w*\s+(?:oneself|yourself|himself|herself|themselves|myself)\s+in" + _R,
    "restrict sb to": _L + r"restrict\w*\s+\w+\s+to" + _R,
    "replace A with B": _L + r"replac\w*\s+\w+\s+with" + _R,
    "define ... as": _L + r"defin\w*\s+[^.\n]{1,40}?\s+as" + _R,
    "be aimed at": _L + r"(?:is|are|was|were|be|being|been)?\s*aimed\s+at" + _R,
    "be tempted to": _L + r"(?:is|are|was|were|be|am)?\s*tempted\s+to" + _R,
    "be based on": _L + r"based\s+on" + _R,
    "desire nothing more than": _L + r"desire\w*\s+nothing\s+more\s+than" + _R,
    "nothing more than": _L + r"nothing\s+more\s+than" + _R,
    "draw a circle on the ground": _L + r"dr(?:aw|ew|awn|aws|awing)\s+a\s+circle\s+on\s+the\s+ground" + _R,
    "a number of": _L + r"(?:of\s*)?a\s+number\s+of" + _R,
    "a term of contempt": _L + r"a\s+term\s+of\s+contempt" + _R,
    "in favor of": _L + r"in\s+favou?r\s+of" + _R,
    "lie in": _L + r"lie[sd]?\s+in" + _R,
    "because of": _L + r"because\s+of" + _R,
    "be captured by": _L + r"(?:is|are|was|were|be|being|been)?\s*captured\s+by" + _R,
    "dare to know": _L + r"dar(?:e|es|ed|ing)\s+to\s+know" + _R,
}


# ---------------------------------------------------------------- 词形

def inflections(word):
    out = {word}
    w = word.lower()
    if w in IRREGULAR:
        return {word} | set(IRREGULAR[w])
    if w.endswith("e"):
        out |= {w + "s", w + "d", w[:-1] + "ing"}
    elif w.endswith("y") and len(w) > 1 and w[-2] not in "aeiou":
        out |= {w[:-1] + "ies", w[:-1] + "ied", w + "ing"}
    elif re.search(r"(?:s|x|z|ch|sh|o)$", w):
        out |= {w + "es", w + "ed", w + "ing"}
    elif re.fullmatch(r"[^aeiou]*[aeiou][^aeiouwxy]", w):
        out |= {w + "s", w + w[-1] + "ed", w + w[-1] + "ing"}
    else:
        out |= {w + "s", w + "ed", w + "ing"}
    return out


LB = r"(?<![A-Za-z])"
LA = r"(?![A-Za-z])"


def build_pattern(phrase):
    if phrase in SPECIAL:
        return re.compile(SPECIAL[phrase], re.I)
    parts = phrase.split()
    forms = sorted(inflections(parts[0]), key=len, reverse=True)
    alt = "|".join(re.escape(f) for f in forms)
    rest = r"\s+".join(re.escape(p) for p in parts[1:])
    return re.compile(rf"{LB}(?:{alt})\s+{rest}{LA}", re.I)


# ---------------------------------------------------------------- 统计

def count_spans(text, pattern, used):
    hits = []
    for m in pattern.finditer(text):
        s, e = m.span()
        if any(not (e <= us or s >= ue) for us, ue in used):
            continue
        hits.append((s, e))
        used.append((s, e))
    return hits


def seed_entries():
    return [dict(head=h, text=t, kind=k, mean=m) for h, t, k, m in PHRASES]


def count_entries(text, entries):
    """统计每条搭配在 text 中的出现次数（长串优先，不重叠）。"""
    rows = [dict(e) for e in entries]
    rows.sort(key=lambda e: len(e["text"]), reverse=True)
    used = []
    for e in rows:
        e["freq"] = len(count_spans(text, build_pattern(e["text"]), used))
    return rows


def load_existing(path):
    """读总表：词组页是数据源，处理记录页保留历史。"""
    from openpyxl import load_workbook

    wb = load_workbook(path)
    ws = wb["词组"]
    hdr = [c.value for c in ws[1]]
    idx = {name: i for i, name in enumerate(hdr) if name}
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r:
            continue
        pos = idx.get("词组", 1)
        t = r[pos] if len(r) > pos else None
        if not t:
            continue
        rows.append(
            dict(
                head=r[idx.get("词头", 0)] or "",
                text=str(t).strip(),
                freq=int(r[idx.get("频次", 2)] or 0),
                kind=r[idx.get("类型", 3)] or "",
                mean=r[idx.get("释义", 4)] or "",
            )
        )
    log = []
    if "处理记录" in wb.sheetnames:
        log = [list(x) for x in wb["处理记录"].iter_rows(min_row=2, values_only=True) if x and x[0]]
    return rows, log


def merge_rows(old_rows, counted):
    """已有的累加频次，材料里新出现的追加；本次没出现的保持不动。"""
    table = {r["text"].lower(): r for r in old_rows}
    added = updated = 0
    for e in counted:
        if e["freq"] <= 0:
            continue
        k = e["text"].lower()
        if k in table:
            table[k]["freq"] = int(table[k].get("freq", 0)) + e["freq"]
            if not table[k]["mean"]:
                table[k]["mean"] = e["mean"]
            updated += 1
        else:
            table[k] = dict(e)
            added += 1
    return list(table.values()), added, updated


def safe(v):
    """单元格落盘：以 = + - @ 开头时前导单引号，Excel 按文本读。"""
    s = str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s


def high_freq_cut(rows):
    """高频线：频次前 10% 分位，且不低于 3 次。"""
    freqs = sorted((e["freq"] for e in rows), reverse=True)
    if not freqs:
        return 3
    k = max(1, round(len(freqs) * 0.10))
    return max(3, freqs[k - 1])


def _fmt_high(p, e, accent, grey):
    from docx.enum.text import WD_COLOR_INDEX
    from docx.shared import Pt

    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("★ " + e["text"])
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = accent
    r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    r2 = p.add_run(f"（{e['freq']} 次）{e['mean']}（{e['kind']}）")
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = grey


def _fmt_row(cells, e, star, accent):
    from docx.shared import Pt

    c0 = cells[0]
    c0.text = ""
    r = c0.paragraphs[0].add_run(("★ " if star else "") + e["text"])
    r.font.size = Pt(9.5)
    if star:
        r.bold = True
        r.font.color.rgb = accent
    for i, val in enumerate([str(e["freq"]), e["kind"], e["mean"]], start=1):
        cells[i].text = ""
        rr = cells[i].paragraphs[0].add_run(val)
        rr.font.size = Pt(9.5)


def _set_text(p, text):
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def _docx_header(rows, log, cut):
    total = sum(e["freq"] for e in rows)
    names = "、".join(str(x[1]) for x in log) or "—"
    return (
        f"共 {len(rows)} 条 · 频次合计 {total} · 高频线 {cut} 次"
        f"（{sum(1 for e in rows if e['freq'] >= cut)} 条）· 材料：{names}"
    )


def _update_docx(path, rows, log, cut, accent, grey):
    from docx import Document

    doc = Document(path)
    high = sorted([e for e in rows if e["freq"] >= cut], key=lambda x: (-x["freq"], x["text"]))

    heading = anchor = None
    for p in doc.paragraphs:
        if p.text.startswith("共 ") and "频次合计" in p.text:
            _set_text(p, _docx_header(rows, log, cut))
        elif p.text.startswith("高频搭配（"):
            heading = p
        elif p.text.startswith("全部词组（"):
            anchor = p

    if heading is not None and anchor is not None:
        cur = heading._p.getnext()
        while cur is not None and cur is not anchor._p:
            nxt = cur.getnext()
            cur.getparent().remove(cur)
            cur = nxt
        _set_text(heading, f"高频搭配（频次 ≥ {cut}）")
        for e in high:
            _fmt_high(anchor.insert_paragraph_before(""), e, accent, grey)

    if doc.tables:
        table = doc.tables[0]
        order = {e["text"]: i for i, e in enumerate(rows)}
        seen = {}
        for row in table.rows[1:]:
            key = row.cells[0].text.replace("★", "").strip()
            if key:
                seen[key] = row
        for e in rows:
            row = seen.get(e["text"])
            if row is None:
                row = table.add_row()
                pos = order[e["text"]]
                for other in table.rows[1:-1]:
                    key = other.cells[0].text.replace("★", "").strip()
                    if order.get(key, 10 ** 9) > pos:
                        other._tr.addprevious(row._tr)
                        break
                seen[e["text"]] = row
            _fmt_row(row.cells, e, e["freq"] >= cut, accent)

    doc.save(path)


def write_docx(rows, out, log, cut):
    """学习讲义：高频段显著标记，全表按词头归并；已有讲义则原文件更新。"""
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    accent = RGBColor(0x0D, 0x5C, 0x56)
    grey = RGBColor(0x5F, 0x5A, 0x4E)
    path = Path(out) / "kaoyan-phrases.docx"

    if path.exists():
        try:
            _update_docx(path, rows, log, cut, accent, grey)
            return
        except Exception:
            pass

    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(1.8)
        s.left_margin = s.right_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    def para(text="", size=10.5, bold=False, color=None, before=0, after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        if color is not None:
            r.font.color.rgb = color
        return p

    para("考研高频固定搭配", 20, True, accent, after=2)
    para(_docx_header(rows, log, cut), 9, False, grey, after=12)

    para(f"高频搭配（频次 ≥ {cut}）", 13, True, accent, before=4)
    for e in sorted([e for e in rows if e["freq"] >= cut], key=lambda x: (-x["freq"], x["text"])):
        _fmt_high(doc.add_paragraph(), e, accent, grey)

    para("全部词组（按词头归并）", 13, True, accent, before=10)

    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, name in enumerate(["词组", "频次", "类型", "释义"]):
        cell = table.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(name)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "0D5C56")
        cell._tc.get_or_add_tcPr().append(shd)

    for e in rows:
        _fmt_row(table.add_row().cells, e, e["freq"] >= cut, accent)

    widths = [Cm(4.8), Cm(1.4), Cm(2.6), Cm(7.6)]
    for row in table.rows:
        for i, w_ in enumerate(widths):
            row.cells[i].width = w_
    for col, w_ in zip(table._tbl.tblGrid.findall(qn("w:gridCol")), widths):
        col.set(qn("w:w"), str(int(w_.twips)))

    para("频次为累计口径：同一搭配在多次并入里累加；★ 为高频标记。", 8.5, False, grey, before=10)
    doc.save(path)


def write_outputs(rows, outdir, log, keep_from=None):
    import csv

    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    rows.sort(key=lambda e: (e["head"], -e["freq"], e["text"]))
    total = sum(e["freq"] for e in rows)
    heads = {}
    for e in rows:
        heads.setdefault(e["head"], []).append(e)
    cut = high_freq_cut(rows)

    with open(out / "kaoyan-cards.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["正面", "背面", "词头", "频次", "提示"])
        for e in rows:
            w.writerow([safe(e["text"]), safe(f"{e['mean']}（{e['kind']}）"), safe(e["head"]), e["freq"], ""])

    accent = "0D5C56"
    fill = PatternFill("solid", fgColor=accent)
    font = Font(color="FFFFFF", bold=True, size=11)
    thin = Side(style="thin", color="D8D2C4")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    if keep_from and Path(keep_from).exists():
        wb = load_workbook(keep_from)
        for name in ("词组", "处理记录"):
            if name in wb.sheetnames:
                del wb[name]
        ws = wb.create_sheet("词组", 0)
        lg = wb.create_sheet("处理记录", 1)
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "词组"
        lg = wb.create_sheet("处理记录")

    def header(sheet, cols):
        sheet.append(cols)
        for c in sheet[1]:
            c.fill, c.font, c.border = fill, font, border
            c.alignment = Alignment(horizontal="center", vertical="center")

    header(ws, ["词头", "词组", "频次", "类型", "释义"])
    for e in rows:
        ws.append([e["head"], e["text"], e["freq"], e["kind"], e["mean"]])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.border = border
    for i, w_ in enumerate([12, 30, 8, 12, 42], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w_
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{ws.max_row}"

    header(lg, ["日期", "来源材料", "新增", "更新", "总条数"])
    for r in log:
        lg.append(list(r[:5]))
    for i, w_ in enumerate([20, 40, 8, 8, 10], start=1):
        lg.column_dimensions[get_column_letter(i)].width = w_
    lg.freeze_panes = "A2"

    wb.save(out / "kaoyan-vocab.xlsx")
    write_docx(rows, out, log, cut)
    return heads, total


def read_text(src):
    """读材料：.docx 在内存里抽取段落与表格，.txt/.md 直接读。"""
    p = Path(src)
    if p.suffix.lower() == ".docx":
        import docx

        doc = docx.Document(str(p))
        parts = [para.text for para in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    parts.append("\t".join(cells))
        return "\n".join(x for x in parts if x)
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("不是 UTF-8 也不是 GBK 编码，请另存为 UTF-8 后重试")


def main(src=None, outdir=None, existing=None, source=None, add=None, refresh=False):
    if existing:
        out = Path(existing).parent
    else:
        out = Path(outdir) if outdir else Path.cwd() / "kaoyan-phrases"
        cand = out / "kaoyan-vocab.xlsx"
        existing = cand if cand.exists() else None

    old_rows, log = load_existing(existing) if existing else ([], [])
    if refresh:
        if not old_rows:
            print(f"没有可刷新的总表：{out / 'kaoyan-vocab.xlsx'}")
            return 1
        try:
            heads, total = write_outputs(old_rows, out, log, keep_from=existing)
        except PermissionError:
            print(f"文件被占用（可能已在 Excel / Word 里打开）：{out}，关闭后重试。")
            return 1
        print(f"刷新：{len(old_rows)} 条 / 词头 {len(heads)} 个 / 累计频次 {total}")
        print(f"写入：{out.resolve()}（xlsx / csv / docx 三份同步更新）")
        return 0

    # 内置词表始终参与匹配；总表里的条目优先，保留用户改过的词头、释义与频次
    entries = seed_entries()
    by_text = {e["text"].lower(): e for e in entries}
    for r in old_rows:
        by_text[r["text"].lower()] = r
    entries = list(by_text.values())
    manual = None
    if add:
        part = [x.strip() for x in add.split("|")]
        if len(part) == 4:
            manual = dict(text=part[0], head=part[1], kind=part[2], mean=part[3])
            entries.append(manual)

    try:
        text = read_text(src)
    except OSError as exc:
        print(f"读不到材料：{src}（{exc.strerror or exc}）")
        return 1
    except (UnicodeDecodeError, ValueError) as exc:
        print(f"读不到材料：{src}（{exc}）")
        return 1

    counted = count_entries(text, entries)
    rows, added, updated = merge_rows(old_rows, counted)
    if manual and manual["text"] not in {r["text"] for r in rows}:
        got = count_entries(text, [manual])
        rows.append(dict(manual, freq=got[0]["freq"] or 1))
        added += 1

    src_name = source or Path(src).name
    log.append([datetime.now().strftime("%Y-%m-%d %H:%M"), src_name, added, updated, len(rows)])
    try:
        heads, total = write_outputs(rows, out, log, keep_from=existing)
    except PermissionError:
        print(f"文件被占用（可能已在 Excel / Word 里打开）：{out}，关闭后重试。")
        return 1

    print(f"并入 {src_name}：新增 {added} 条，更新 {updated} 条")
    print(f"写入：{out.resolve()}（xlsx / csv / docx 三份同步更新）")
    print(f"词组 {len(rows)} 条 / 词头 {len(heads)} 个 / 累计频次 {total}")
    top = sorted(rows, key=lambda e: -e["freq"])[:15]
    print("Top 15：", "、".join(f"{e['text']}({e['freq']})" for e in top))
    return 0


USAGE = (
    "用法：python build_kaoyan_vocab.py <材料.docx|材料.txt> [输出目录] "
    "[--existing 总表.xlsx] [--source 材料名] [--add 词组|词头|类型|释义]\n"
    "      python build_kaoyan_vocab.py --refresh [输出目录]"
)

if __name__ == "__main__":
    argv = sys.argv[1:]
    opts = {"existing": None, "source": None, "add": None}
    positional = []
    refresh = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(USAGE)
            sys.exit(0)
        if a == "--refresh":
            refresh = True
            i += 1
            continue
        if a in ("--existing", "--source", "--add"):
            opts[a[2:]] = argv[i + 1]
            i += 2
            continue
        positional.append(a)
        i += 1
    if not refresh and not positional:
        print(USAGE)
        sys.exit(1)
    # --refresh 时第一个位置参数是产出目录，不是材料
    if refresh:
        src, outdir = None, (positional[0] if positional else None)
    else:
        src = positional[0] if positional else None
        outdir = positional[1] if len(positional) > 1 else None
    sys.exit(main(src, outdir, opts["existing"], opts["source"], opts["add"], refresh))