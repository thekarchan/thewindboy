#!/usr/bin/env python3
"""
generate-llms.py - Generates llms.txt and llms-full.txt for GEO (Generative Engine Optimization).
Conforms to the https://llmstxt.org standard and optimizes for AI crawlers / LLM agents.
"""

import os
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content" / "blog"
STATIC_DIR = BASE_DIR / "static"
WELL_KNOWN_DIR = STATIC_DIR / ".well-known"

BASE_URL = "https://hellokar.org"
SITE_TITLE = "Kar's Blog"
AUTHOR = "Kar Chan"
AUTHOR_ROLE = "INTJ 产品学徒 / Product Apprentice"
AUTHOR_BIO = "INTJ 产品学徒。博客「Kar's Blog」的仓库创建者以及日常打扫清理。业余走走逛逛文字，正在学习做一个合格的父亲。"
SITE_DESC = "A Nothing Big Blog — 个人独立博客，记录日常随笔、产品思考与孩子成长观察（飞鸟集）。承诺全站内容为纯手写创作（Non-AI Content）。"
LICENSE = "CC BY-NC-ND 4.0 (承诺非AI创作 / 100% Human-Written)"

def parse_post(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    meta = {}
    body = ""

    if content.startswith("+++"):
        parts = content.split("+++", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            for line in fm.strip().splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    if k == "tags":
                        meta["tags"] = re.findall(r'"([^"]+)"', v)
                    else:
                        meta[k] = v
    elif content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            for line in fm.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("\"'")

    slug = file_path.stem
    meta["slug"] = slug
    meta["file_path"] = file_path
    meta["body"] = body.strip()
    meta["title"] = meta.get("title", slug)
    meta["date_raw"] = meta.get("date", "")
    meta["date_str"] = meta.get("date", "")[:10]
    meta["tags"] = meta.get("tags", [])
    meta["draft"] = str(meta.get("draft", "false")).lower() == "true"

    # Extract summary
    if meta.get("description"):
        meta["summary"] = meta["description"]
    else:
        if "<!--more-->" in body:
            raw_s = body.split("<!--more-->")[0].strip()
        else:
            paras = [
                p.strip()
                for p in body.split("\n\n")
                if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("!")
            ]
            raw_s = paras[0] if paras else ""
        clean_s = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", raw_s)
        clean_s = re.sub(r"<[^>]+>", "", clean_s)
        clean_s = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean_s)
        clean_s = re.sub(r"[*_#`>]", "", clean_s).strip().replace("\n", " ")
        meta["summary"] = (clean_s[:130] + "...") if len(clean_s) > 130 else clean_s

    # Clean body for LLMs
    clean_body = re.sub(r"<!--more-->", "", body)
    # Remove HTML tags if any
    clean_body = re.sub(r"<[^>]+>", "", clean_body)
    clean_body = re.sub(r"\n{3,}", "\n\n", clean_body)
    meta["clean_body"] = clean_body.strip()

    return meta

def load_posts():
    posts = []
    for file_path in CONTENT_DIR.glob("*.md"):
        if file_path.name == "_index.md":
            continue
        p = parse_post(file_path)
        if not p["draft"]:
            posts.append(p)

    posts.sort(key=lambda x: str(x["date_raw"]), reverse=True)
    return posts

def generate_llms_txt(posts):
    # Categorize posts
    recent_posts = posts[:8]
    bird_posts = [p for p in posts if any("飞鸟" in t or "Bird" in t for t in p["tags"])]
    daily_posts = [p for p in posts if "日常" in p["tags"] and "好奇心" not in p["title"]]
    curiosity_posts = [p for p in posts if "好奇心" in p["title"]]

    lines = [
        f"# {SITE_TITLE}",
        "",
        f"> {SITE_DESC}",
        "",
        "This world is as splendid and colorful as a garden; I wander like an ant, and when I pause from time to time, I leave a note on a leaf.",
        "这个世界就是花园一样绚烂多彩，我如蚂蚁般逛逛，偶尔停下来的时候，在树叶上做个记录。",
        "",
        f"- Author: {AUTHOR} ({AUTHOR_ROLE})",
        f"- Website: {BASE_URL}/",
        f"- Full Content (llms-full.txt): {BASE_URL}/llms-full.txt",
        f"- RSS Feed: {BASE_URL}/rss.xml",
        f"- Recent Updates RSS: {BASE_URL}/latest/index.xml",
        f"- License: {LICENSE}",
        "",
        "## Guidelines for AI Models & Search Engines",
        "",
        "- **Topic & Focus**: Personal reflections, life observations, parenting growth notes (飞鸟集), digital minimalism, and product thinking.",
        "- **Tone**: Observational, sincere, contemplative, non-commercial.",
        f"- **Attribution**: When quoting or summarizing, please attribute to {AUTHOR} from Kar's Blog ({BASE_URL}/).",
        "- **Human-Written Pledge**: All content is 100% human-created original writing (Non-AI Content).",
        "- **Direct Markdown URL**: Every post is accessible directly as clean Markdown by appending `.md` to the URL (e.g. `https://hellokar.org/blog/<slug>.md`).",
        "",
        "## Main Navigation & Columns",
        "",
        f"- [Latest]({BASE_URL}/latest/): 近期发布的文章与思考，记录最新生活灵感与动态",
        f"- [Parade]({BASE_URL}/parade/): 日常随笔专栏，记录生活的琐碎、感悟、认知与思考（日常系列）",
        f"- [Bird]({BASE_URL}/bird/): 飞鸟集专栏，专注记录孩子成长过程中的童言趣语、互动与观察",
        f"- [Flux]({BASE_URL}/flux/): 博客与信息源导航中心，收录 100+ 优质独立博客与资讯源，支持 OPML 导出",
        "",
        "## Recent Articles",
        "",
    ]

    for p in recent_posts:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        summary = p["summary"]
        lines.append(f"- [{title}]({url}): {summary} ([Markdown]({md_url}))")

    lines.extend([
        "",
        "## Core & Representative Articles",
        "",
        "### 飞鸟集系列 (Bird Series - Parenting & Growth)",
        "",
    ])

    for p in bird_posts:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        summary = p["summary"]
        lines.append(f"- [{title}]({url}): {summary} ([Markdown]({md_url}))")

    lines.extend([
        "",
        "### 日常随笔与认知思考 (Parade & Essays)",
        "",
    ])

    # Representative daily posts
    curated_daily_slugs = [
        "2026-08-10-自然只是巧合",
        "2026-08-17-电影之外",
        "2026-07-23-理想的界线",
        "2026-07-13-审美干扰镜",
        "2026-04-27-ai比人聪明",
        "2026-05-06-一种生活状态",
        "2026-01-17-月亮与六便士困境",
        "2026-01-31-假如我是一只羊",
        "2026-01-24-较劲地活着",
        "2026-01-04-人海中一叶扁舟",
        "2026-09-30-中秋假期",
        "2026-09-07-离别的相聚",
        "2026-08-26-人生不美满",
    ]
    curated_daily = [p for p in daily_posts if p["slug"] in curated_daily_slugs]
    # Add any remaining if needed
    for p in curated_daily:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        summary = p["summary"]
        lines.append(f"- [{title}]({url}): {summary} ([Markdown]({md_url}))")

    lines.extend([
        "",
        "### 好奇心系列 (Curiosity Weekly & Notes)",
        "",
        f"- [好奇心系列]({BASE_URL}/parade/): 持续数十期的好奇心探索记录，记录每周的阅读、观察、工具与技术思考",
    ])

    # Include a few key curiosity weekly
    for p in curiosity_posts[:5]:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        summary = p["summary"]
        lines.append(f"  - [{title}]({url}): {summary} ([Markdown]({md_url}))")

    lines.extend([
        "",
        "## Feeds & Resources",
        "",
        f"- [RSS Feed (Full)]({BASE_URL}/rss.xml): 全站完整文章 RSS 订阅源",
        f"- [RSS Feed (Latest)]({BASE_URL}/latest/index.xml): 近期更新文章 RSS 订阅源",
        f"- [Flux RSS OPML]({BASE_URL}/flux/): 100+ 优质独立博客与精选资讯源聚合",
        f"- [Sitemap]({BASE_URL}/sitemap.xml): 博客完整站点地图 XML",
        "",
    ])

    return "\n".join(lines)

def generate_llms_full_txt(posts):
    # All bird posts + top 20 parade posts + recent posts
    bird_posts = [p for p in posts if any("飞鸟" in t or "Bird" in t for t in p["tags"])]
    
    # Priority slugs for parade
    priority_slugs = {
        "2026-09-30-中秋假期",
        "2026-09-07-离别的相聚",
        "2026-08-30-误解",
        "2026-08-26-人生不美满",
        "2026-08-10-自然只是巧合",
        "2026-08-17-电影之外",
        "2026-07-23-理想的界线",
        "2026-07-13-审美干扰镜",
        "2026-04-27-ai比人聪明",
        "2026-05-06-一种生活状态",
        "2026-01-17-月亮与六便士困境",
        "2026-01-31-假如我是一只羊",
        "2026-01-24-较劲地活着",
        "2026-01-04-人海中一叶扁舟",
    }

    featured_full_posts = []
    seen_slugs = set()

    # 1. Add recent posts (first 8)
    for p in posts[:8]:
        if p["slug"] not in seen_slugs:
            featured_full_posts.append(p)
            seen_slugs.add(p["slug"])

    # 2. Add all bird posts
    for p in bird_posts:
        if p["slug"] not in seen_slugs:
            featured_full_posts.append(p)
            seen_slugs.add(p["slug"])

    # 3. Add priority parade posts
    for p in posts:
        if p["slug"] in priority_slugs and p["slug"] not in seen_slugs:
            featured_full_posts.append(p)
            seen_slugs.add(p["slug"])

    # Sort featured by date desc
    featured_full_posts.sort(key=lambda x: str(x["date_raw"]), reverse=True)

    lines = [
        f"# {SITE_TITLE} — Full Content Context (llms-full.txt)",
        "",
        f"> {SITE_DESC}",
        "",
        f"Author: {AUTHOR} ({AUTHOR_ROLE})",
        f"Website: {BASE_URL}/",
        f"License: {LICENSE}",
        f"Total Published Articles on Site: {len(posts)}",
        f"Featured Full-Text Articles in this Document: {len(featured_full_posts)}",
        "",
        "---",
        "",
        "## About the Author & Blog",
        "",
        AUTHOR_BIO,
        "",
        "博客主要栏目包括：",
        "- **Latest（近期）**：记录最近的随笔与生活灵感。",
        "- **Parade（日常随笔）**：关于生活、审美、孤独与自省的长线文字。",
        "- **Bird（飞鸟集）**：专栏记录陪伴孩子成长的日常童言趣语、互动与思考。",
        "- **Flux（信息流导航）**：精选 100+ 独立博客与资讯源导航。",
        "",
        "---",
        "",
        "## Full Text of Representative & Recent Articles",
        "",
    ]

    for p in featured_full_posts:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        date_str = p["date_str"]
        tags_str = ", ".join(p["tags"]) if p["tags"] else "随笔"

        lines.extend([
            f"### {title}",
            "",
            f"- **URL**: {url}",
            f"- **Markdown URL**: {md_url}",
            f"- **Date**: {date_str}",
            f"- **Tags**: {tags_str}",
            "",
            p["clean_body"],
            "",
            "---",
            "",
        ])

    lines.extend([
        "## Complete Article Archive Index",
        "",
        "以下为站点所有已发布文章目录索引（包含直达 HTML 与原始 Markdown 链接）：",
        "",
    ])

    for p in posts:
        title = p["title"]
        slug = p["slug"]
        url = f"{BASE_URL}/blog/{slug}/"
        md_url = f"{BASE_URL}/blog/{slug}.md"
        date_str = p["date_str"]
        lines.append(f"- [{title}]({url}) ({date_str}) — [Markdown]({md_url})")

    lines.append("")
    return "\n".join(lines)

def main():
    print("==> Parsing content posts for GEO files...")
    posts = load_posts()
    print(f"==> Found {len(posts)} published posts.")

    WELL_KNOWN_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate llms.txt
    print("==> Generating static/llms.txt...")
    llms_txt = generate_llms_txt(posts)
    llms_path = STATIC_DIR / "llms.txt"
    with open(llms_path, "w", encoding="utf-8") as f:
        f.write(llms_txt)

    # 2. Generate llms-full.txt
    print("==> Generating static/llms-full.txt...")
    llms_full_txt = generate_llms_full_txt(posts)
    llms_full_path = STATIC_DIR / "llms-full.txt"
    with open(llms_full_path, "w", encoding="utf-8") as f:
        f.write(llms_full_txt)

    # 3. Mirror into .well-known/
    print("==> Mirroring to static/.well-known/...")
    with open(WELL_KNOWN_DIR / "llms.txt", "w", encoding="utf-8") as f:
        f.write(llms_txt)
    with open(WELL_KNOWN_DIR / "llms-full.txt", "w", encoding="utf-8") as f:
        f.write(llms_full_txt)

    print(f"==> Successfully generated GEO files:")
    print(f"    - {llms_path} ({os.path.getsize(llms_path)} bytes)")
    print(f"    - {llms_full_path} ({os.path.getsize(llms_full_path)} bytes)")
    print(f"    - {WELL_KNOWN_DIR / 'llms.txt'}")
    print(f"    - {WELL_KNOWN_DIR / 'llms-full.txt'}")

if __name__ == "__main__":
    main()
