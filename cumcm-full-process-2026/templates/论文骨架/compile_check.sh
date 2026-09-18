#!/bin/bash
# ============================================================
#  编译 + 三项计数检查（论文终版验收通用脚本）
#  用法：放在论文工程根目录（与 main.tex 同级）执行：bash compile_check.sh
#  要求：xelatex 在 PATH（TeX Live 的 bin 目录）
#  说明：不用 latexmk（它会误判 up-to-date），直接 xelatex 连编两遍
# ============================================================
cd "$(dirname "$0")" || exit 1
rm -f main.fdb_latexmk main.fls
xelatex -interaction=nonstopmode main.tex >/dev/null 2>&1
xelatex -interaction=nonstopmode main.tex >/dev/null 2>&1
echo "=================== 编译结果 ==================="
echo -n "错误数(^!): "; grep -c '^!' main.log || true
echo -n "Overfull: "; grep -c 'Overfull' main.log || true
echo -n "Missing character: "; grep -c 'Missing character' main.log || true
echo -n "LaTeX Warning: "; grep -c 'LaTeX Warning' main.log || true
echo "页数:"; grep -o 'Output written on main.pdf ([0-9]* pages' main.log | tail -1
echo "=== 错误详情（如有） ==="; grep -A4 '^!' main.log | head -50 || true
echo "=== Missing char 详情（如有） ==="; grep 'Missing character' main.log | sort | uniq -c | sort -rn | head -25 || true
