# -*- coding: utf-8 -*-
# 知网(CNKI)检索结果抓取 —— 在 browser-use 环境运行
#   （Hermes 浏览器工具 / browser-use CLI；new_tab / wait_for_load / js 为环境预置函数）
# 用法：作为 browser-use 的脚本输入执行；输出标题+链接 JSON（前 25 条）
# 多页检索：循环里改页码参数即可
# 注意：仅用于个人科研文献检索；遵守目标网站条款与访问频率限制
new_tab("https://kns.cnki.net/kns8s/defaultresult/index?kw=" + "测向交叉定位")
wait_for_load()
import json, time
time.sleep(1)
res = js('''(() => {
  const out = [];
  document.querySelectorAll('a').forEach(a => {
    const h = a.href || '';
    if (h.indexOf('kcms') >= 0 || h.indexOf('dbcode') >= 0 || h.indexOf('/article/') >= 0) {
      const t = (a.innerText || '').replace(/\\s+/g, ' ').trim();
      if (t.length > 4) out.push({t: t.slice(0, 90), h: h.slice(0, 300)});
    }
  });
  return JSON.stringify({title: document.title, n: out.length, items: out.slice(0, 25)});
})()''')
print(res)
