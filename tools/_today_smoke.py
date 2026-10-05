# -*- coding: utf-8 -*-
"""今日看板前端冒烟：打开 Web UI → 点「今日」tab → 验证渲染"""
import datetime
import sys

from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto("http://127.0.0.1:8899", wait_until="networkidle", timeout=15000)
        # 点「今日」tab
        pg.click("text=今日")
        pg.wait_for_timeout(1200)
        # 验证渲染内容
        body = pg.inner_text("body")
        ok_tab = "今日工作" in body
        # 日期取当天，不写死 —— 写死会在第二天必然失败
        # （外部审查 2026-09-28 点名此处："硬编码的 2026 年 9 月 10 日日期"）
        today = datetime.date.today().isoformat()
        ok_date = today in body
        ok_event = "打卡碎片" in body
        print(f"tab可见={ok_tab} 日期({today})={ok_date} 碎片={ok_event}")
        print(f"console errors: {len(errors)}")
        if errors:
            print("  ".join(errors[:5]))
        pg.screenshot(path="tools/_today_smoke.png", full_page=False)
        b.close()
        if not (ok_tab and ok_date):
            sys.exit(1)
        print("SMOKE PASS")


if __name__ == "__main__":
    main()
