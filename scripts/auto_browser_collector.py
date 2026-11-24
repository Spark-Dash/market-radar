#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蝉妈妈 / 闲鱼 / 小红书 免破解全自动抓取器 (Playwright 持久化登录态 + XHR JSON 响应拦截)
核心原理：
1. 不逆向前端 JS 签名算法（避免平台每周更新 webpack 导致爬虫失效或封号）；
2. 启动本地真实 Google Chrome 并挂载独立持久化目录 (.browser_profile/)：
   - 首次运行 `--login` 扫码登录一次蝉妈妈/闲鱼/小红书，Cookie 与设备指纹永久保存在本地；
   - 后续日常或定时任务运行 `--collect`，自动打开目标榜单/搜索页，通过 `page.on("response")` 直接在内存里截获后台返回的干净 JSON 数据包并写入 SQLite 与 JSONL！
"""

import argparse
import json
import pathlib
import re
import sqlite3
import sys
import time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import urllib.parse
from typing import Any, Dict, List

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROFILE_DIR = BASE_DIR / ".browser_profile"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def extract_json_candidates(data: Any, platform: str, query: str) -> List[Dict[str, str]]:
    """递归从截获的 XHR/Fetch JSON 响应树中提取商品、投流视频或痛点笔记条目"""
    results: List[Dict[str, str]] = []

    def walk(node: Any):
        if isinstance(node, dict):
            # 1. 蝉妈妈视频/商品投流结构识别
            title = (
                node.get("aweme_title")
                or node.get("product_title")
                or node.get("title")
                or node.get("note_title")
                or node.get("display_title")
                or ""
            )
            if isinstance(title, str) and len(title.strip()) >= 6:
                sales_or_like = (
                    node.get("volume_text")
                    or node.get("sales_count")
                    or node.get("digg_count")
                    or node.get("liked_count")
                    or node.get("want_cnt")
                    or node.get("wantCnt")
                    or ""
                )
                author = (
                    node.get("author_name")
                    or node.get("nickname")
                    or node.get("shop_name")
                    or node.get("user_nick")
                    or platform
                )
                price = node.get("price_text") or node.get("price") or "高潜商业信号"
                url = node.get("aweme_url") or node.get("url") or node.get("share_url") or ""
                desc = node.get("desc") or node.get("sub_title") or title
                if sales_or_like != "" or "chanmama" in platform.lower():
                    results.append(
                        {
                            "title": str(title).strip()[:180],
                            "content": f"[自动拦截XHR数据包] {str(desc).strip()[:400]}",
                            "author": str(author).strip()[:80],
                            "metric_primary": f"热度/销量: {sales_or_like}" if sales_or_like else "榜单命中",
                            "metric_secondary": f"检索词: {query}",
                            "price": str(price)[:60],
                            "url": str(url)[:300],
                        }
                    )
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    # 去重
    uniq = {}
    for r in results:
        uniq[r["title"]] = r
    return list(uniq.values())[:15]


def run_browser_collector(mode: str, targets: List[str], keywords: List[str], headless: bool = False) -> int:
    from playwright.sync_api import sync_playwright
    import radar_cli
    from collab_utils import dump_db_to_jsonl, sync_db_from_jsonl

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    conn = radar_cli.get_conn()
    radar_cli.init_db(conn)
    sync_db_from_jsonl(conn, BASE_DIR, radar_cli.insert_signal)

    added_total = 0
    with sync_playwright() as p:
        launch_kwargs: Dict[str, Any] = {
            "user_data_dir": str(PROFILE_DIR),
            "headless": headless if mode != "login" else False,
            "viewport": {"width": 1360, "height": 860},
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        if pathlib.Path(CHROME_PATH).exists():
            launch_kwargs["executable_path"] = CHROME_PATH

        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else context.new_page()

        if mode == "login":
            print("=================================================================")
            print("🔓 已打开持久化 Chrome 窗口，请在浏览器中扫码登录：")
            print("   1. 蝉妈妈: https://www.chanmama.com/")
            print("   2. 闲鱼网页版: https://www.goofish.com/")
            print("   3. 小红书: https://www.xiaohongshu.com/")
            print("💡 登录成功后直接关闭浏览器窗口，登录态将永久保存在 .browser_profile/")
            print("=================================================================")
            page.goto("https://www.chanmama.com/", wait_until="domcontentloaded")
            p2 = context.new_page(); p2.goto("https://www.goofish.com/", wait_until="domcontentloaded")
            p3 = context.new_page(); p3.goto("https://www.xiaohongshu.com/", wait_until="domcontentloaded")
            try:
                page.wait_for_event("close", timeout=300000)
            except Exception:
                pass
            context.close()
            return 0

        captured_items: List[Dict[str, str]] = []
        current_meta = {"platform": "", "query": "", "url": ""}

        def handle_response(resp):
            try:
                ctype = resp.headers.get("content-type", "")
                if "application/json" in ctype and resp.status == 200:
                    data = resp.json()
                    items = extract_json_candidates(data, current_meta["platform"], current_meta["query"])
                    for it in items:
                        it["platform"] = current_meta["platform"]
                        it["query"] = current_meta["query"]
                        if not it["url"]:
                            it["url"] = current_meta["url"]
                        captured_items.append(it)
            except Exception:
                pass

        page.on("response", handle_response)

        platform_urls = {
            "chanmama": ("蝉妈妈投流监测(自动XHR)", "https://www.chanmama.com/promotionVideo?keyword="),
            "xianyu": ("闲鱼虚拟监测(自动XHR)", "https://www.goofish.com/search?q="),
            "xhs": ("小红书痛点监测(自动XHR)", "https://www.xiaohongshu.com/search_result?keyword="),
        }

        for tgt in targets:
            if tgt not in platform_urls:
                continue
            ch_name, base_url = platform_urls[tgt]
            for kw in keywords:
                captured_items.clear()
                target_url = base_url + urllib.parse.quote(kw)
                current_meta.update({"platform": ch_name, "query": kw, "url": target_url})
                print(f"[AUTO-BROWSER] 正在访问并监听后台数据包: {ch_name} -> 关键词『{kw}』")
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                    page.wait_for_timeout(4500)
                    # 若 XHR 未命中，兜底提取 DOM 可见文本卡片
                    if not captured_items:
                        body_txt = page.inner_text("body")
                        lines = [ln.strip() for ln in body_txt.splitlines() if len(ln.strip()) > 12]
                        if lines and not any(k in body_txt[:300] for k in ["请登录", "扫码登录", "安全验证"]):
                            for ln in lines[:5]:
                                captured_items.append(
                                    {
                                        "platform": ch_name,
                                        "query": kw,
                                        "title": ln[:120],
                                        "content": f"[自动DOM提取] {ln}",
                                        "author": ch_name,
                                        "metric_primary": "页面实时抓取",
                                        "metric_secondary": f"检索词: {kw}",
                                        "price": "见详情",
                                        "url": target_url,
                                    }
                                )
                    for item in captured_items[:8]:
                        ok = radar_cli.insert_signal(
                            conn=conn,
                            channel=item["platform"],
                            source_tier="浏览器XHR自动拦截",
                            category=kw,
                            query_term=kw,
                            title=item["title"],
                            content=item["content"],
                            author_or_app=item["author"],
                            metric_primary=item["metric_primary"],
                            metric_secondary=item["metric_secondary"],
                            rating_or_price=item["price"],
                            source_url=item["url"],
                        )
                        if ok:
                            added_total += 1
                except Exception as exc:
                    print(f"[WARN] 自动抓取页面超时或需先执行 --login 扫码 ({ch_name} - {kw}): {exc}")

        context.close()

    radar_cli.clean_and_tag_signals(conn)
    dump_db_to_jsonl(conn, BASE_DIR)
    from export_dashboard import export_all
    export_all(conn, BASE_DIR)
    print(f"[AUTO-BROWSER] 完成！本次自动入库新信号: {added_total} 条，已刷新看板。")
    return added_total


def main():
    parser = argparse.ArgumentParser(description="蝉妈妈/闲鱼/小红书 Playwright XHR 自动采集器")
    parser.add_argument("--login", action="store_true", help="打开 Chrome 扫码登录一次并永久保存 Cookie")
    parser.add_argument("--collect", action="store_true", help="复用已保存的登录态全自动拦截 XHR 数据包入库")
    parser.add_argument("--targets", default="chanmama,xianyu,xhs", help="目标平台: chanmama,xianyu,xhs")
    parser.add_argument("--keywords", default="知识动画代做,学习规划表,提词器,AI直播搭建", help="逗号分隔的搜索词")
    parser.add_argument("--headless", action="store_true", help="无头静默运行")
    args = parser.parse_args()

    mode = "login" if args.login else "collect"
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    run_browser_collector(mode=mode, targets=targets, keywords=keywords, headless=args.headless)


if __name__ == "__main__":
    main()
