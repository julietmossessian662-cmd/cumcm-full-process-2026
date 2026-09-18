# -*- coding: utf-8 -*-
"""支撑材料打包（zip + md5 + 条目清单）

用法：改 STAGE / OUT_ZIP 两个路径 → python 支撑材料打包.py
要点：
  - zip 内统一前缀（如 "支撑材料/"），目录结构即 staging 的层级；
  - 打包后打印 条目数 / 大小 / md5 —— 抄进提交清单（MD5 提交后文件不可再动）；
  - 每轮改动后重打包 → 再算 md5（旧的 md5 一律作废）。
"""
import hashlib
import os
import zipfile

STAGE = r"D:/你的目录/support"            # ← 要打包的目录（staging）
OUT_ZIP = r"D:/你的目录/支撑材料.zip"      # ← 输出 zip 路径
ARC_PREFIX = "支撑材料/"                   # ← zip 内统一前缀


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    cnt = 0
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, fs in os.walk(STAGE):
            dirs.sort()
            for f in sorted(fs):
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, STAGE).replace("\\", "/")
                zf.write(fp, ARC_PREFIX + rel)
                cnt += 1
    print("zip 条目:", cnt, "| 大小:", os.path.getsize(OUT_ZIP), "| md5:", md5(OUT_ZIP))


if __name__ == "__main__":
    main()
