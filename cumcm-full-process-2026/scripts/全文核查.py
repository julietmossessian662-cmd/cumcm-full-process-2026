# -*- coding: utf-8 -*-
"""论文全文文本核查（定稿纪律第③步：旧串清零 / 新串就位）

用法：
  python 全文核查.py main.pdf --must "关键词" "参考文献" --must-not "旧版本词" "待补充"
  - --must    ：必须出现的串（报告出现页码；未找到=!!）
  - --must-not ：禁止出现的串（命中页即报警，需要清理）

依赖：PyMuPDF（uv pip install pymupdf 或 pip install pymupdf）
"""
import sys

import fitz  # PyMuPDF


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print(__doc__)
        return
    pdf = args[0]
    must, must_not = [], []
    mode = "must"
    for a in args[1:]:
        if a == "--must":
            mode = "must"
            continue
        if a == "--must-not":
            mode = "must-not"
            continue
        (must if mode == "must" else must_not).append(a)

    doc = fitz.open(pdf)
    pages = [p.get_text() for p in doc]
    print("PDF:", pdf, "| 总页数:", len(pages))

    for kw in must:
        hits = [i + 1 for i, t in enumerate(pages) if kw in t]
        print(f"[必须出现] {kw!r}: {hits if hits else '!! 未找到'}")

    for kw in must_not:
        hits = [i + 1 for i, t in enumerate(pages) if kw in t]
        if hits:
            print(f"[禁止出现] {kw!r}: 命中页 {hits}  -> 需要清理!")
        else:
            print(f"[禁止出现] {kw!r}: 零命中 OK")


if __name__ == "__main__":
    main()
