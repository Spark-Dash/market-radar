#!/usr/bin/env python3
"""Publish data and generated pages together, using the renderer already on main."""
import argparse
import hashlib
import json
import pathlib
import subprocess

from export_dashboard import render_page

BASE = pathlib.Path(__file__).resolve().parent.parent
REPO = "repos/donghyq/market-radar"
PAGE_FILES = ("index.html", "docs/index.html")
RENDERER_FILES = (
    "scripts/export_dashboard.py", "scripts/template.html", "scripts/dashboard_app.js",
    "scripts/research_workstation.js", "scripts/workstation.css",
)
DATA_FILES = (
    "inbox/chanmama_xianyu_xhs_signals.csv", "exports/signals_full.csv",
    "data/signals/signals_master.jsonl", "data/tech_radar.json", "data/persona_stats.json",
)


def api(path, method="GET", payload=None):
    args = ["gh", "api", "-X", method, f"{REPO}/{path}"]
    if payload is not None:
        args += ["--input", "-"]
    return json.loads(subprocess.run(
        args, input=json.dumps(payload) if payload is not None else None,
        text=True, stdout=subprocess.PIPE, check=True,
    ).stdout)


def git_blob_sha(content):
    return hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()


def prepare_files(root, remote):
    drift = [path for path in RENDERER_FILES
             if not (root / path).is_file() or git_blob_sha((root / path).read_bytes()) != remote.get(path)]
    if drift:
        raise ValueError("本地渲染代码与 main 不一致，请先同步代码：" + "、".join(drift))

    html = (root / PAGE_FILES[0]).read_text(encoding="utf-8")
    bundle = json.loads(html.split("const DATA = ", 1)[1].split(";\n</script>", 1)[0])
    if html != render_page(bundle) or html.encode() != (root / PAGE_FILES[1]).read_bytes():
        raise ValueError("本地页面未使用当前渲染代码生成，请重新导出看板再同步。")

    files = [*DATA_FILES, *PAGE_FILES]
    for folder in ("data/ideas", "data/archives"):
        files.extend(str(p.relative_to(root)) for p in sorted((root / folder).glob("*.json")))
    changed = []
    for rel in files:
        path = root / rel
        if path.is_file():
            content = path.read_bytes()
            if git_blob_sha(content) != remote.get(rel):
                changed.append({"path": rel, "mode": "100644", "type": "blob", "content": content.decode("utf-8")})
    return changed


def sync(check_only=False):
    head = api("git/ref/heads/main")["object"]["sha"]
    tree = api(f"git/commits/{head}")["tree"]["sha"]
    result = api(f"git/trees/{tree}?recursive=1")
    if result["truncated"]:
        raise ValueError("未能获取完整的远端文件列表，已停止同步。")
    remote = {entry["path"]: entry["sha"] for entry in result["tree"] if entry["type"] == "blob"}
    changed = prepare_files(BASE, remote)
    if not changed:
        print("数据和页面均无变更。")
        return
    if check_only:
        print("将同步：" + "、".join(entry["path"] for entry in changed))
        return
    new_tree = api("git/trees", "POST", {"base_tree": tree, "tree": changed})["sha"]
    commit = api("git/commits", "POST", {
        "message": "chore: publish market radar data and pages", "tree": new_tree, "parents": [head],
    })["sha"]
    api("git/refs/heads/main", "PATCH", {"sha": commit, "force": False})
    print(f"已同步 {len(changed)} 个数据和页面文件：{commit[:7]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="检查渲染代码与待同步文件，不写远端")
    try:
        sync(check_only=parser.parse_args().check)
    except (ValueError, IndexError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"同步未完成：{exc}") from exc
