# -*- coding: utf-8 -*-
"""论文配图生成模板（matplotlib 中文字体 + 常用图型骨架）

用法：
  1) 用装有 matplotlib 的 Python 运行（跑时 env -u PYTHONPATH 可避免依赖串台）
  2) 改 OUT 为论文工程 figures/（或中转目录）→ 按 Q1..Q4 补图 → python 配图模板.py

实战要点（教训）：
  - 中文字体必须设 Microsoft YaHei，否则方块；
  - 标签避免 S1 类下标字符（字体缺字会渲染成怪符号）→ 写 S1、psi 等 ASCII；
  - PDF（矢量）给 LaTeX 用、PNG 用于预览目检；文件名用 qX-含义 风格。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = r"D:/你的目录/figs"  # ← 改成你的输出目录（或论文工程 figures/）
os.makedirs(OUT, exist_ok=True)

# ---- 全局样式：中文字体 + 负号 ----
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 180


def save(fig, name, pdf=False):
    """保存并关闭；pdf=True 时同时输出矢量 PDF（给 LaTeX）"""
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name + ".png"))
    if pdf:
        fig.savefig(os.path.join(OUT, name + ".pdf"))
    plt.close(fig)
    print("saved:", name)


# ============ 示例 1：几何示意（多边形填充 + 点标注） ============
pts = np.array([[0, 0], [1, 0.3], [1.2, 1], [0.1, 0.8]])
fig, ax = plt.subplots(figsize=(8, 6))
ax.fill(pts[:, 0], pts[:, 1], color="#e15759", alpha=0.3, label="区域 R")
ax.plot(*np.vstack([pts, pts[0]]).T, color="#c23b3b", lw=2)
ax.scatter([0.5], [0.5], c="#1b9e77", s=60, zorder=5)
ax.annotate("点 P", (0.5, 0.5), textcoords="offset points", xytext=(8, 6))
ax.set_aspect("equal")
ax.grid(alpha=0.25)
ax.legend(loc="lower left")
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
ax.set_title("示例：几何示意")
save(fig, "example-geometry", pdf=True)

# ============ 示例 2：对比柱状图（数字标注） ============
labels = ["方案A", "方案B", "方案C"]
vals = [0.168, 0.037, 0.030]
fig, ax = plt.subplots(figsize=(8, 5.2))
bars = ax.bar(labels, vals, color=["#e15759", "#f28e2b", "#59a14f"], width=0.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.004, f"{v:.3f}", ha="center")
ax.set_ylabel("指标")
ax.grid(axis="y", alpha=0.25)
ax.set_title("示例：方案对比")
save(fig, "example-bar", pdf=True)

# ============ 示例 3：饼图（时间构成） ============
fig, ax = plt.subplots(figsize=(7.2, 5.4))
ax.pie([77.8, 17.7, 3.0, 1.5],
       labels=["移动", "检测", "换频", "清除"], startangle=90,
       wedgeprops=dict(width=0.55, edgecolor="w"))
ax.set_title("示例：时间构成")
save(fig, "example-pie", pdf=True)

print("done:", sorted(os.listdir(OUT)))
