#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拉取 GitHub Trending（daily），输出 Markdown 日报到 stdout。
只依赖 Python 标准库，方便在 GitHub Actions ubuntu runner 上零依赖运行。
"""
import re
import sys
import json
import urllib.request
from datetime import datetime, timezone, timedelta

TRENDING_URL = "https://github.com/trending?since=daily"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
    s = s.replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()


def parse_trending(html: str):
    # 每个仓库是一个 <article class="Box-row"> ... </article>
    blocks = re.split(r'<article class="Box-row', html)
    repos = []
    for blk in blocks[1:]:
        # 仓库名：<h2 ...><a href="/owner/repo" ...>
        m = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"', blk)
        if not m:
            continue
        full = m.group(1).strip()
        # 描述
        m_desc = re.search(r'<p class="col-9[^"]*"[^>]*>(.*?)</p>', blk, re.S)
        desc = strip_tags(m_desc.group(1)) if m_desc else ""
        # 语言
        m_lang = re.search(r'itemprop="programmingLanguage">([^<]+)<', blk)
        lang = m_lang.group(1).strip() if m_lang else ""
        # 总 star：/stargazers 链接内的数字（中间可能夹 svg 图标，整段剥标签）
        stars = ""
        m_star = re.search(r'href="/[^"]+/stargazers"[^>]*>(.*?)</a>', blk, re.S)
        if m_star:
            nums = re.findall(r"[\d,]+", strip_tags(m_star.group(1)))
            if nums:
                stars = nums[0]
        # fork
        forks = ""
        m_fork = re.search(r'href="/[^"]+/forks"[^>]*>(.*?)</a>', blk, re.S)
        if m_fork:
            nums = re.findall(r"[\d,]+", strip_tags(m_fork.group(1)))
            if nums:
                forks = nums[0]
        # stars today
        m_today = re.search(r'([\d,]+)\s+stars? today', blk)
        today = m_today.group(1).strip() if m_today else ""
        repos.append({
            "full": full, "desc": desc, "lang": lang,
            "stars": stars, "forks": forks, "today": today,
        })
    return repos


def render_md(repos):
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz).strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# GitHub Trending 日报 · {today}")
    lines.append("")
    lines.append(f"今日 Trending 共 {len(repos)} 个仓库，按 GitHub 官方榜单顺序列出。")
    lines.append("")
    for i, r in enumerate(repos[:25], 1):
        url = f"https://github.com/{r['full']}"
        head = f"## {i}. [{r['full']}]({url})"
        lines.append(head)
        meta = []
        if r["lang"]:
            meta.append(f"语言 `{r['lang']}`")
        if r["stars"]:
            meta.append(f"总 star ⭐ {r['stars']}")
        if r["today"]:
            meta.append(f"今日新增 ⭐ +{r['today']}")
        if meta:
            lines.append(" · ".join(meta))
            lines.append("")
        if r["desc"]:
            lines.append(r["desc"])
            lines.append("")
    lines.append("---")
    lines.append("_由 GitHub Actions 自动抓取自 https://github.com/trending?since=daily_")
    return "\n".join(lines)


def main():
    try:
        html = fetch_html(TRENDING_URL)
    except Exception as e:
        # 抓取失败也要发 issue 告知，不然用户不知道
        tz = timezone(timedelta(hours=8))
        today = datetime.now(tz).strftime("%Y-%m-%d")
        print(f"# GitHub Trending 日报 · {today}\n\n"
              f"⚠️ 抓取失败：`{type(e).__name__}: {e}`\n\n"
              f"GitHub Trending 页面本次未取到，请手动打开 {TRENDING_URL} 查看。")
        sys.exit(0)  # 不算 workflow 失败，照样发 issue
    repos = parse_trending(html)
    print(render_md(repos))


if __name__ == "__main__":
    main()
