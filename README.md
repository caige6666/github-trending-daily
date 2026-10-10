# github-trending-daily

每天早上 08:12（北京时间）自动抓 GitHub Trending（daily 榜），把 Top 25 仓库整理成 Markdown 日报，作为一条 Issue 提交到本仓库。

GitHub 账号绑定邮箱后，新 Issue 会自动发到你邮箱，手机上也能收。

## 它每天做什么

1. GitHub Actions 启动一个 ubuntu runner；
2. 跑 `fetch_trending.py` 抓 https://github.com/trending?since=daily；
3. 解析每个仓库的：名称、链接、描述、主语言、总 star、今日新增 star；
4. 用 `gh issue create` 把 Markdown 日报提交成本仓库的一个新 Issue。

## 手动触发

仓库页 → Actions → Daily Trending Report → Run workflow，立刻跑一次。

## 文件说明

- `fetch_trending.py` — 抓取 + 渲染脚本，纯标准库，零依赖。
- `.github/workflows/daily.yml` — 定时任务定义。

## 后续可扩展

- 加微信/企业微信机器人 webhook：在 workflow 里加一步 curl；
- 过滤只看 AI / Python 方向：改 `TRENDING_URL` 为 `https://github.com/trending/python?since=daily` 之类；
- 写进 README 归档：在 workflow 里加一步 commit。
