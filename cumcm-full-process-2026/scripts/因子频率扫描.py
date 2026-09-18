#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全样本因子频次扫描 —— 把"论文逆向分析"从主观判断升级为频次证据
================================================================
用法:
    python 因子频率扫描.py <ocr根目录> [--out <输出目录>]
    # 目录结构约定: <ocr根目录>/<年份目录>/*.txt   (每篇论文一个 txt)
    # 文件名建议形如 B226.txt / A196.txt —— 首字母用作题型分组 (A/B/C)

输出:
    · 控制台: 因子命中率表(总占比 + 按年 + 按题型) + 均值型指标 + 趋势警报表
    · <out>/per_paper.csv, <out>/summary.json

关键设计:
    1) 宽窄口径都给 —— 命中率 0 时先怀疑口径, 不要下"该因子无价值"的结论
    2) 趋势优先 —— 用"最近一年 vs 更早年份"找水位线漂移(总命中率会掩盖新门槛)
    3) 只测"行为词族", 不测单个词
依赖: 仅标准库。
"""
import os, re, sys, csv, json, argparse

# ---- 指标: 命中即该篇"做了这件事" (按同义词族写宽口径) ----
PATS = {
    "验证/互验":   r"验证|校验|检验|印证|复核|核对|比对|对照",
    "交叉验证类":  r"交叉验证|相互验证|互相验证|两种方法|双方法|算法对比|结果对比|对比分析",
    "误差/精度":   r"相对误差|绝对误差|误差率|精度|误差分析|残差",
    "灵敏度":      r"灵敏度|敏感性|扰动|参数扫描|单因素|敏感度",
    "鲁棒性":      r"鲁棒|稳健|抗噪|抗干扰|最坏情况|worst",
    "不确定度/区间": r"置信区间|不确定度|置信度|误差传播|误差界|区间估计",
    "递进/衔接":   r"在问题[一二三四]|基于问题[一二三四]|沿用|衔接|递进|同理|类似地|相同思路",
    "假设清单":    r"模型假设|基本假设|假设条件|假设说明",
    "创新/特色":   r"创新|特色|亮点|新颖|独到|改进之处|本文特点|优点",
    "异常/数据质量": r"异常|缺失|剔除|离群|噪声|跳变|毛刺|数据清洗|预处理",
    "自曝缺点":    r"缺点|不足|局限|有待|改进方向|模型的问题",
    "AI 申报":     r"人工智能|AI工具|AI使用|DeepSeek|ChatGPT|大模型|智能助手|语言模型",
    "落地/推广":   r"推广|应用前景|实际应用|工程应用|落地|实际价值|应用价值",
    "数学证明":    r"定理|引理|命题|证明|证毕|当且仅当|充分必要",
    "复杂度":      r"时间复杂度|空间复杂度|计算复杂度|算法效率|O\(n",
    "伪代码":      r"伪代码|算法\s*\d|Algorithm|输入[:：]|输出[:：]",
    "统计检验":    r"残差|正态性|拟合优度|显著性|p\s*值|p\s*<|Shapiro|K-S|t\s*检验|卡方|方差分析",
    "图表引用规范": r"图\s*\d+[-–.]\s*\d+|表\s*\d+[-–.]\s*\d+",
}
REF_TAIL = re.compile(r"[\u005b\uff3b]\s*\d+\s*[\u005d\uff3d]")   # 先 compile, 避开 f-string 反斜杠限制


def load(p):
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return open(p, encoding=enc).read()
        except (UnicodeDecodeError, LookupError):
            pass
    return ""


def analyze(text):
    r = {"chars": len(text)}
    for k, pat in PATS.items():
        r[k] = len(re.findall(pat, text))
    m = re.search(r"摘\s*要", text)
    ab = ""
    if m:
        seg = text[m.start():m.start() + 3000]
        m2 = re.search(r"关键词", seg)
        ab = seg[:m2.start()] if m2 else seg[:1500]
    r["摘要字数"] = len(re.sub(r"\s", "", ab))
    r["摘要含数字"] = 1 if re.search(r"\d", ab) else 0
    r["高精度数字总数"] = len(re.findall(r"\d+\.\d{4,}", text))
    m = re.search(r"参考文献", text)
    r["参考文献条数"] = len(REF_TAIL.findall(text[m.end():])) if m else 0
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="ocr 根目录(内含年份子目录)")
    ap.add_argument("--out", default="factor_freq_out")
    a = ap.parse_args()

    rows = []
    years = sorted(d for d in os.listdir(a.root) if os.path.isdir(os.path.join(a.root, d)))
    for year in years:
        d = os.path.join(a.root, year)
        for fn in sorted(os.listdir(d)):
            if fn.lower().endswith(".txt"):
                t = load(os.path.join(d, fn))
                r = analyze(t)
                r.update(year=year, code=fn[:-4], qtype=(fn[0].upper() if fn else "?"))
                rows.append(r)
    if not rows:
        sys.exit("未找到 .txt 样本")

    latest = years[-1]
    print("样本 %d 篇 / %d 个年份目录（最近年份视为 %s）\n" % (len(rows), len(years), latest) + "=" * 90)
    hdr = "%-16s%8s   " % ("指标", "占比") + "".join("%10s" % y for y in years) + "     A    B    C"
    print(hdr); print("=" * 90)
    latest_bumps = []
    for k in PATS:
        hit = [r for r in rows if r[k] > 0]
        per = {y: (sum(1 for r in hit if r["year"] == y), sum(1 for r in rows if r["year"] == y)) for y in years}
        q = {c: sum(1 for r in hit if r["qtype"] == c) for c in "ABC"}
        nq = {c: sum(1 for r in rows if r["qtype"] == c) for c in "ABC"}
        print("%-16s%5d/%-3d  " % (k, len(hit), len(rows))
              + "".join("%7d/%-3d" % per[y] for y in years)
              + "  %3d/%-3d %3d/%-3d %3d/%-3d" % (q["A"], nq["A"], q["B"], nq["B"], q["C"], nq["C"]))
        if len(years) > 1:
            cur = per[latest][0] / max(per[latest][1], 1)
            past = sum(v[0] for y, v in per.items() if y != latest) / max(sum(v[1] for y, v in per.items() if y != latest), 1)
            if cur - past > 0.25:
                latest_bumps.append((k, past, cur))
    print("=" * 90)
    for k in ("chars", "摘要字数", "高精度数字总数", "参考文献条数"):
        v = sorted(r[k] for r in rows)
        print("%-14s 均值 %8.1f  中位 %6d  最小 %6d  最大 %6d" % (k, sum(v) / len(v), v[len(v) // 2], v[0], v[-1]))
    print("\n摘要含数字: %d/%d" % (sum(r["摘要含数字"] for r in rows), len(rows)))

    print("\n【趋势警报】%s vs 更早年份（Δ>25pp）—— 水位线漂移，按最近一年处理：" % latest)
    for k, past, cur in sorted(latest_bumps, key=lambda x: -(x[2] - x[1])):
        print("  ↑ %-14s %3.0f%% → %3.0f%%   (+%2.0fpp)" % (k, past * 100, cur * 100, (cur - past) * 100))

    os.makedirs(a.out, exist_ok=True)
    keys = ["year", "code", "qtype", "chars"] + list(PATS) + ["摘要字数", "摘要含数字", "高精度数字总数", "参考文献条数"]
    with open(os.path.join(a.out, "per_paper.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    json.dump(rows, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n输出: %s/per_paper.csv, summary.json" % a.out)


if __name__ == "__main__":
    main()
