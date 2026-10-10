#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Markdown 日报推到企业微信群机器人。
用法：python push_wecom.py report.md
环境变量：WEBHOOK（企业微信群机器人 webhook URL）
"""
import sys
import os
import json
import urllib.request

MAX_BYTES = 4000  # 企业微信 markdown 消息 content 上限 4096 字节，留点余量


def main():
    if len(sys.argv) < 2:
        print("usage: push_wecom.py <report.md>", file=sys.stderr)
        sys.exit(1)
    webhook = os.environ.get("WEBHOOK", "").strip()
    if not webhook:
        print("WEBHOOK env not set, skip.")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        body = f.read()

    # 按字节截断，避免超 4096
    encoded = body.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        body = encoded[:MAX_BYTES].decode("utf-8", errors="ignore")
        body += "\n\n……（过长已截断，完整内容见仓库 Issue）"

    payload = json.dumps({
        "msgtype": "markdown",
        "markdown": {"content": body},
    }).encode("utf-8")

    req = urllib.request.Request(
        webhook, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("WeCom response:", resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        # 推送失败不阻塞整个 workflow
        print(f"WeCom push failed (non-blocking): {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
