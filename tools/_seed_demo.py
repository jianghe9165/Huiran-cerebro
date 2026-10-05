#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成一份**虚构的演示数据**，用于界面截图或本地试玩。

特点：
  · 内容全部是编造的示例，不含任何真实业务数据
  · 幂等：目标库已存在时会先备份再重建
  · 零联网：不下载模型（可选索引步骤除外）

用法：
    python tools/_seed_demo.py                    # 建成 ./cyber_brain.db
    python tools/_seed_demo.py --db demo.db       # 指定库文件
    python tools/_seed_demo.py --index            # 顺便建向量索引（首次会下模型）
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORE = os.path.join(ROOT, "cyber_brain.py")

FRAGMENTS = [
    ("iron_rule", "release", "发布前必须跑脱敏检查，命中高危项一律中止提交"),
    ("iron_rule", "release", "数据库文件永不进版本库，只发布源码框架"),
    ("iron_rule", "release", "任何对外发布都先出草稿，人工确认后才生效"),
    ("decision", "retrieval", "检索采用 RRF 四路融合（全文 + 模糊 + 实体 + 语义），而非单一向量"),
    ("decision", "lifecycle", "碎片去重默认只预演，显式加参数才真正写入"),
    ("decision", "lifecycle", "合并用标记而非物理删除，保留可追溯性与可撤销性"),
    ("pitfall", "windows", "删除目录后立即用 exists() 检查会误判，需要等文件系统刷盘"),
    ("pitfall", "tooling", "替换表里不能出现单独的注释符号，会被当成待删字符串"),
    ("knowledge", "search", "FTS5 处理中文要用 trigram 分词，按 3 字滑窗建索引"),
    ("knowledge", "search", "短于 3 字的查询全文索引不命中，需要回退模糊匹配兜底"),
    ("knowledge", "search", "本地语义向量用轻量中文模型，可完全离线运行"),
    ("preference", "style", "汇报偏好：先给结论，再给细节，最后给下一步选项"),
    ("preference", "style", "破坏性操作前先列清单并二次确认"),
    ("fact", "demo", "演示库：本库内容全部为虚构示例，仅用于界面展示"),
    ("event", "daily", "完成检索层重构，四路召回接通并做了回归"),
    ("event", "daily", "补了生命周期审计与重复检测的预演开关"),
]

ENTITIES = [
    ("project", "Atlas 检索重构", "记忆检索模块"),
    ("team", "核心引擎组", "维护检索与存储"),
    ("platform", "MCP 客户端", "外部接入方"),
    ("product", "知识库模块", "负责文档分块"),
    ("person", "维护者", "项目主要作者"),
]

LINKS = [(1, 2, "owned_by"), (3, 1, "consumes"), (4, 1, "part_of"), (5, 2, "member_of")]

CONTENTS = [
    ("检索层重构设计纪要", "note", "design",
     "把召回从纯向量改为四路融合。每一路按 rank 打 1/(k+rank)，跨路累加后重排。"),
    ("去重方案评审", "decision", "review",
     "结论：默认预演，显式加参数才写入；合并走标记而非删除。"),
]

KB_DOC = (
    "长期记忆系统设计说明",
    "本系统把「记忆」与「知识」分层存放。记忆层用碎片表达原子事实，知识层用文档分块承载长文本。"
    "检索时两路并行召回，再用融合算法重排。碎片带有类型与重要性标记，生命周期管理会定期降权过期内容，"
    "并检测内容高度重叠的重复项。实体关系网用于把碎片挂到具体对象上，形成可追溯的关联。",
)


def run(args, db, quiet=False):
    cmd = [sys.executable, CORE, "--db", db] + args
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 and not quiet:
        print("   ⚠️ 失败: %s" % ((r.stderr or r.stdout or "")[:160]))
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "cyber_brain.db"))
    ap.add_argument("--index", action="store_true", help="顺便建向量索引（首次会下载模型）")
    ap.add_argument("--force", action="store_true", help="库已存在时直接重建（默认先备份）")
    a = ap.parse_args()

    db = os.path.abspath(a.db)
    print("=" * 66)
    print("生成虚构演示数据")
    print("=" * 66)
    print("  目标库: %s" % db)
    print("  ⚠️ 内容全部为编造示例，不含任何真实数据")
    print()

    if os.path.exists(db):
        if a.force:
            os.remove(db)
            print("  已删除旧库（--force）")
        else:
            bak = db + ".bak"
            os.replace(db, bak)
            print("  旧库已备份为 %s" % os.path.basename(bak))
    print()

    for ft, subj, content in FRAGMENTS:
        run(["frag", "--add", "--type", ft, "--content", content, "--subject", subj], db)
    print("  记忆碎片   %d 条" % len(FRAGMENTS))

    for et, name, org in ENTITIES:
        run(["entity", "--add", "--type", et, "--name", name, "--org", org], db)
    print("  实体       %d 个" % len(ENTITIES))

    for fr, to, rel in LINKS:
        run(["link", "--from", str(fr), "--to", str(to), "--relation", rel], db)
    print("  实体关系   %d 条" % len(LINKS))

    for title, ct, cat, body in CONTENTS:
        run(["content", "--add", "--title", title, "--body", body,
             "--type", ct, "--cat", cat], db)
    print("  内容实体   %d 条" % len(CONTENTS))

    run(["doc", "--add", "--title", KB_DOC[0], "--text", KB_DOC[1]], db)
    print("  知识库文档 1 篇")

    run(["summary", "--add", "--scope", "work",
         "--summary", "本阶段完成检索层四路融合与生命周期管理；下阶段计划补回归评测集。"], db)
    print("  滚动摘要   1 条")

    # 跑几次检索，给「检索记录」页签造数据
    for q in ("检索 融合", "去重", "中文分词", "生命周期"):
        run(["recall", q], db, quiet=True)
    print("  检索记录   4 条")

    if a.index:
        print()
        print("  建向量索引（首次会下载模型）…")
        run(["index"], db)

    print()
    print("✅ 完成。启动 Web 界面查看：")
    print("   python web_ui.py        # 默认 http://127.0.0.1:8899")
    print("   （web_ui.py 读取的是它同目录下的 cyber_brain.db）")


if __name__ == "__main__":
    main()
