#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专项 2：GitHub Trending 与前沿科技雷达采集器 (Tech Radar)
核心目标：
1. 实时抓取 GitHub 近期飙升的 AI / Agent / 开发者工具 / 自动化工作流开源项目；
2. 结合 Hacker News 高分 Show HN 工具动态；
3. 按团队『两问过滤法』输出结构化评估：
   - 向内提效（Internal Efficiency）：能否直接集成进团队的 Codex + DeepSeek Harness 工作流？
   - 向外变现（Commercialization）：能否汉化/封装成面向中国互联网买家的变现工具？
"""

import datetime
import json
import pathlib
import re
import ssl
import urllib.parse
import urllib.request
from typing import Any, Dict, List

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
OUT_JSON = BASE_DIR / "data" / "tech_radar.json"
SSL_CTX = ssl._create_unverified_context()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def eval_repo_value(name: str, desc: str, topics: List[str]) -> Dict[str, str]:
    text = f"{name} {desc} {' '.join(topics)}".lower()
    if any(k in text for k in ["agent", "mcp", "codex", "claude", "harness", "cli", "skill", "prompt", "workflow"]):
        return {
            "category": "Agent 与编码工作流",
            "internal_use": "高优引入：可直接作为团队 Codex / DeepSeek Harness 的外部 MCP 工具或 Skill 模板参考，减少重复手写脚手架。",
            "commercial_idea": "国内许多中小开发团队不会配置复杂 Agent Harness，可提取其核心工作流封装为开箱即用的垂直行业自动化脚本包。",
        }
    if any(k in text for k in ["video", "audio", "tts", "voice", "subtitle", "animation", "manim", "remotion", "ocr", "pdf"]):
        return {
            "category": "多模态与文档生产力",
            "internal_use": "组件复用：可直接接入团队现有的视频/文档处理管线（如 LawFlow 或知识动画生成引擎），降低底层研发耗时。",
            "commercial_idea": "极易变现：海外开源多模态工具通常只有英文 CLI 界面，包装一层中文极简 GUI 或小程序即可在闲鱼/小红书按买断制或包月售卖。",
        }
    if any(k in text for k in ["scrape", "crawler", "browser", "playwright", "data", "search", "rag"]):
        return {
            "category": "数据采集与检索增强",
            "internal_use": "增强雷达：可用于升级本仓库 (Market Radar) 的底层网页解析与正文提取能力。",
            "commercial_idea": "可面向跨境电商或市场部门封装为垂直行业竞品监控桌面小工具。",
        }
    return {
        "category": "前沿开源工具",
        "internal_use": "技术视野储备：关注其架构设计与轻量化实现思路，按需引入团队工具箱。",
        "commercial_idea": "观察其在海外社区的付费转化模式，评估是否存在中国本土化平替空间。",
    }


def fetch_github_trending_repos() -> List[Dict[str, Any]]:
    """通过 GitHub Search API 抓取近期高星飙升的 AI / Agent / 生产力工具仓库"""
    since_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    queries = [
        f"created:>{since_date} (agent OR mcp OR harness OR workflow OR llm) stars:>50",
        f"pushed:>{since_date} (remotion OR video-generation OR pdf-extractor OR playwright-mcp) stars:>100",
    ]
    repos: Dict[str, Dict[str, Any]] = {}
    for q in queries:
        try:
            url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
                {"q": q, "sort": "stars", "order": "desc", "per_page": 8}
            )
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=12, context=SSL_CTX) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            for item in data.get("items", []):
                full_name = item.get("full_name", "")
                if not full_name or full_name in repos:
                    continue
                desc = item.get("description") or "暂无描述"
                topics = item.get("topics") or []
                ev = eval_repo_value(full_name, desc, topics)
                repos[full_name] = {
                    "source": "GitHub Trending / 近期飙升",
                    "name": full_name,
                    "description": desc[:220],
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "language": item.get("language") or "Multi",
                    "url": item.get("html_url", f"https://github.com/{full_name}"),
                    "updated_at": (item.get("pushed_at") or "")[:10],
                    "category": ev["category"],
                    "internal_use": ev["internal_use"],
                    "commercial_idea": ev["commercial_idea"],
                }
        except Exception as exc:
            print(f"[WARN] GitHub API 抓取异常: {exc}")
    return sorted(repos.values(), key=lambda x: x["stars"], reverse=True)[:12]


def fetch_hn_show_tools() -> List[Dict[str, Any]]:
    """通过 Hacker News Algolia API 抓取近期高赞 Show HN AI/开发工具"""
    items: List[Dict[str, Any]] = []
    try:
        url = "https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
            {"query": "Show HN AI tool agent CLI", "tags": "show_hn", "numericFilters": "points>30", "hitsPerPage": 6}
        )
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            points = hit.get("points", 0)
            comments = hit.get("num_comments", 0)
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            ev = eval_repo_value(title, title, ["show_hn"])
            items.append(
                {
                    "source": "Hacker News (Show HN)",
                    "name": title.replace("Show HN:", "").strip(),
                    "description": f"海外独立开发者近期展示项目（{points} 赞 / {comments} 条讨论），反映一线工具需求风向。",
                    "stars": points,
                    "forks": comments,
                    "language": "Web/CLI",
                    "url": link,
                    "updated_at": (hit.get("created_at") or "")[:10],
                    "category": ev["category"],
                    "internal_use": ev["internal_use"],
                    "commercial_idea": ev["commercial_idea"],
                }
            )
    except Exception as exc:
        print(f"[WARN] Hacker News 抓取异常: {exc}")
    return items


def main():
    gh_list = fetch_github_trending_repos()
    hn_list = fetch_hn_show_tools()
    all_items = gh_list + hn_list
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(
            {
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total": len(all_items),
                "items": all_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[TECH-RADAR] 采集完成：GitHub飙升项目={len(gh_list)}, HackerNews工具={len(hn_list)} -> 已写入 {OUT_JSON}")


if __name__ == "__main__":
    main()
