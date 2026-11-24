r"""校验 kaoyan-phrases 的产出是否自洽。

用法（在用户工作区里跑）：
    python -B "$SKILL\tools\check_outputs.py" [产出目录]

默认产出目录是 <当前目录>/kaoyan-phrases。全部通过退出码 0，否则 1。
"""

import csv
import pathlib
import re
import sys

from openpyxl import load_workbook

HEAD_RULE_EXCEPTIONS = {"be", "a"}  # 被动语态与数量搭配，词头取实义词


def fail(msgs, msg):
    msgs.append(msg)
    print("  FAIL", msg)


def main():
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd() / "kaoyan-phrases"
    xlsx = out / "kaoyan-vocab.xlsx"
    csvf = out / "kaoyan-cards.csv"
    msgs = []

    print(f"校验目录：{out}")
    for f in (xlsx, csvf):
        if not f.exists():
            fail(msgs, f"缺少文件 {f.name}")
    if msgs:
        return 1

    # ---- 总表
    wb = load_workbook(xlsx)
    if "词组" not in wb.sheetnames:
        fail(msgs, "缺少「词组」工作表")
        return 1
    ws = wb["词组"]
    hdr = [c.value for c in ws[1]]
    want = ["词头", "词组", "频次", "类型", "释义"]
    if hdr != want:
        fail(msgs, f"总表表头应为 {want}，实际 {hdr}")
    rows = [tuple(r) for r in ws.iter_rows(min_row=2, values_only=True) if r and r[1]]
    print(f"总表：{len(rows)} 条")

    # ---- CSV
    raw = csvf.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        fail(msgs, "CSV 缺少 UTF-8 BOM，Excel 里会乱码")
    text = raw.decode("utf-8-sig")
    if text.lstrip().startswith("|"):
        fail(msgs, "CSV 里出现了 markdown 表格")
    crows = list(csv.reader(text.splitlines()))
    chdr = crows[0]
    want_c = ["正面", "背面", "词头", "频次", "提示"]
    if chdr != want_c:
        fail(msgs, f"CSV 表头应为 {want_c}，实际 {chdr}")
    body = crows[1:]
    print(f"CSV：{len(body)} 条")
    for i, r in enumerate(body, start=2):
        if len(r) != 5:
            fail(msgs, f"CSV 第 {i} 行字段数为 {len(r)}（应为 5）")

    # ---- 一致性
    if len(rows) != len(body):
        fail(msgs, f"条数不一致：总表 {len(rows)}，CSV {len(body)}")
    if len(rows) == len(body):
        for i, (xr, cr) in enumerate(zip(rows, body)):
            if (xr[0], xr[1]) != (cr[2], cr[0]):
                fail(msgs, f"第 {i + 2} 行条目/顺序不一致：{xr[0]} {xr[1]} vs {cr[2]} {cr[0]}")
                break
            if int(xr[2]) != int(cr[3]):
                fail(msgs, f"第 {i + 2} 行频次不一致：{xr[1]} {xr[2]} vs {cr[3]}")
                break
    if len({(r[0], r[1]) for r in rows}) != len(rows):
        fail(msgs, "总表有重复条目")

    # ---- 内容
    for r in rows:
        head, phrase, freq, kind, mean = r[0], r[1], r[2], r[3], r[4]
        if not isinstance(freq, int) or freq <= 0:
            fail(msgs, f"频次不是正整数：{phrase} = {freq!r}")
        if not kind:
            fail(msgs, f"类型为空：{phrase}")
        if not mean:
            fail(msgs, f"释义为空：{phrase}")
        first = re.match(r"[A-Za-z]+", phrase.strip())
        first = first.group(0).lower() if first else ""
        if first not in HEAD_RULE_EXCEPTIONS and first != (head or "").lower():
            fail(msgs, f"词头应为「{first}」而非「{head}」：{phrase}")

    # ---- 处理记录
    if "处理记录" not in wb.sheetnames:
        fail(msgs, "缺少「处理记录」工作表")
    else:
        lg = wb["处理记录"]
        lh = [c.value for c in lg[1]]
        if lh != ["日期", "来源材料", "新增", "更新", "删除", "总条数"]:
            fail(msgs, f"处理记录表头应为 [日期, 来源材料, 新增, 更新, 删除, 总条数]，实际 {lh}")
        logs = [tuple(r) for r in lg.iter_rows(min_row=2, values_only=True) if r[0]]
        running = 0
        for l in logs:
            if int(l[2]) < 0 or int(l[3]) < 0 or int(l[4]) < 0:
                fail(msgs, f"处理记录新增/更新/删除为负：{l}")
            running += int(l[2]) - int(l[4])
            if int(l[5]) != running:
                fail(msgs, f"处理记录累计条数对不上：{l}（前几行净增累计应为 {running}）")
        if logs and int(logs[-1][5]) != len(rows):
            fail(msgs, f"末行总条数 {logs[-1][5]} 与当前 {len(rows)} 不符")
        print(f"处理记录：{len(logs)} 行")

    # ---- Word 讲义
    docxf = out / "kaoyan-phrases.docx"
    if not docxf.exists():
        fail(msgs, "缺少文件 kaoyan-phrases.docx")
    else:
        from docx import Document

        d = Document(str(docxf))
        if not d.tables:
            fail(msgs, "Word 里没有词组表")
        else:
            body = d.tables[0].rows[1:]
            if len(body) != len(rows):
                fail(msgs, f"Word 表格 {len(body)} 行，总表 {len(rows)} 条")
            freqs = sorted((int(r[2]) for r in rows), reverse=True)
            cut = max(3, freqs[max(0, round(len(freqs) * 0.10) - 1)]) if freqs else 3
            want_high = sum(1 for r in rows if int(r[2]) >= cut)
            got_high = sum(1 for r in body if r.cells[0].text.startswith("★"))
            if got_high != want_high:
                fail(msgs, f"Word 高频标记 {got_high} 条，应为 {want_high} 条（线 {cut}）")
            print(f"Word：{len(body)} 行 · 高频 {got_high} 条（线 {cut}）")

    # ---- 汇总
    freqs = [int(r[2]) for r in rows]
    heads = {r[0] for r in rows}
    top = sorted(rows, key=lambda r: -int(r[2]))[:5]
    print(f"词头 {len(heads)} 个 · 频次合计 {sum(freqs)} · 最高 {max(freqs)}")
    print("Top5：", "、".join(f"{r[1]}({r[2]})" for r in top))

    if msgs:
        print(f"\n未通过：{len(msgs)} 项")
        return 1
    print("\n全部通过：CSV 与总表在条数、顺序、频次、字段上一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
