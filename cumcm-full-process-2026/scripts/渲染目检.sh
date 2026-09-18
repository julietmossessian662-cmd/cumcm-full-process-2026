#!/bin/bash
# ============================================================
#  渲染 PDF 指定页为 PNG（字体/版式目检用）
#  用法：bash 渲染目检.sh <PDF路径> <输出目录> <页码...>
#  例：  bash 渲染目检.sh paper/main.pdf render_out 1 4 6 21 29
#  依赖：rungs.exe（TeX Live 自带 ghostscript 工具；可用环境变量 RUNG 指定完整路径）
#       可用环境变量 RUNG 覆盖路径
# ============================================================
GS="${RUNG:-rungs.exe}"
PDF="$1"
OUT="$2"
shift 2 || true

if [ -z "$PDF" ] || [ -z "$OUT" ]; then
  echo "用法: bash 渲染目检.sh <PDF> <输出目录> <页码...>"
  exit 1
fi
mkdir -p "$OUT"
for p in "$@"; do
  "$GS" -q -dNOSAFER -sDEVICE=png16m -r120 -dFirstPage=$p -dLastPage=$p -o "$OUT/p$p.png" "$PDF" \
    && echo "rendered: $OUT/p$p.png"
done
ls -la "$OUT"
