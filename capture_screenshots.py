#!/usr/bin/env python3
"""Capture screenshots of the FIDUS app for PDF documentation."""
import asyncio
import os

async def main():
    from playwright.async_api import async_playwright
    
    os.makedirs("/app/screenshots", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        # 1. Login screen
        print("Capturing login screen...")
        await page.goto("http://localhost:3000/login", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/01_login.png")
        print("  -> Saved 01_login.png")
        
        # 2. Login and go to dashboard
        print("Logging in...")
        email_input = page.locator('input').first
        await email_input.fill("carlos.demo@test.com")
        password_input = page.locator('input').nth(1)
        await password_input.fill("Fidus26@")
        await page.wait_for_timeout(500)
        sign_in_btn = page.get_by_text("Sign In", exact=True)
        await sign_in_btn.click(force=True, timeout=10000)
        await page.wait_for_timeout(5000)
        
        # Dashboard
        print("Capturing dashboard...")
        await page.screenshot(path="/app/screenshots/02_dashboard.png")
        print("  -> Saved 02_dashboard.png")
        
        # 3. Invest tab
        print("Capturing investment simulator...")
        invest_tab = page.get_by_text("Invest", exact=True)
        await invest_tab.click(force=True, timeout=5000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/03_invest.png")
        print("  -> Saved 03_invest.png")
        
        # 4. Info tab
        print("Capturing info screen...")
        info_tab = page.get_by_text("Info", exact=True)
        await info_tab.click(force=True, timeout=5000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/04_info.png")
        print("  -> Saved 04_info.png")
        
        # 5. Settings tab
        print("Capturing settings screen...")
        settings_tab = page.get_by_text("Settings", exact=True)
        await settings_tab.click(force=True, timeout=5000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/05_settings.png")
        print("  -> Saved 05_settings.png")
        
        # 6. Terms screen
        print("Capturing terms screen...")
        await page.goto("http://localhost:3000/terms", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/06_terms.png")
        print("  -> Saved 06_terms.png")
        
        # 7. Terms Log
        print("Capturing terms log...")
        await page.goto("http://localhost:3000/terms-log", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/app/screenshots/07_terms_log.png")
        print("  -> Saved 07_terms_log.png")
        
        await browser.close()
    
    print("\nAll screenshots captured successfully!")
    for f in sorted(os.listdir("/app/screenshots")):
        size = os.path.getsize(f"/app/screenshots/{f}")
        print(f"  {f} ({size:,} bytes)")

asyncio.run(main())
