import asyncio
import os
from playwright.async_api import async_playwright

EMAIL = os.environ["LOGIN_EMAIL"]
PASSWORD = os.environ["LOGIN_PASSWORD"]

LOGIN_URL = "https://sports.mitwpu.edu.in/login"
SLOT_URL = "https://sports.mitwpu.edu.in/sports/b4e13520-6b4f-4d88-abb0-03b6bf6650d4/slots/5792a435-0f22-4e76-96e8-0cee9ca393b7/seats"

async def book_slot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # ── Step 1: Login ──────────────────────────────────────────────
        print("Going to login page...")
        await page.goto(LOGIN_URL)

        await page.wait_for_selector("#email", state="visible")
        await page.wait_for_selector("#password", state="visible")
        print("Login form ready.")

        await page.fill("#email", EMAIL)
        await page.fill("#password", PASSWORD)

        await page.wait_for_timeout(10000)
        await page.screenshot(path="debug_before_login.png")
        print("Filled credentials. Clicking login...")

        await page.click('button[type="submit"]')

        await page.wait_for_url(lambda url: "login" not in url, timeout=15000)
        print(f"Logged in! URL: {page.url}")
        await page.wait_for_timeout(10000)
        await page.screenshot(path="debug_after_login.png")

        # ── Step 2: Go to swimming slot page ──────────────────────────
        print("Navigating to swimming slot...")
        await page.goto(SLOT_URL)

        await page.wait_for_selector("button.bg-emerald-500", state="visible", timeout=15000)
        await page.wait_for_timeout(10000)
        await page.screenshot(path="debug_seats.png")
        print("Seats loaded.")

        # ── Step 3: Click first available green seat ───────────────────
        seats = await page.query_selector_all("button.bg-emerald-500")
        print(f"Found {len(seats)} available seat(s). Clicking first...")
        await seats[0].click()

        await page.wait_for_selector("#terms", state="visible", timeout=10000)
        await page.wait_for_timeout(10000)
        await page.screenshot(path="debug_modal.png")
        print("Modal opened.")

        # ── Step 4: Check Terms & Conditions ──────────────────────────
        await page.click("#terms")
        await page.wait_for_timeout(10000)
        print("T&C checked.")

        # ── Step 5: Click Confirm ──────────────────────────────────────
        confirm_btn = await page.wait_for_selector("button:has-text('Confirm')", state="visible", timeout=5000)
        await confirm_btn.click()

        await page.wait_for_timeout(10000)
        await page.screenshot(path="booking_result.png")
        print("✅ Swimming slot booked! Check booking_result.png")

        await browser.close()

asyncio.run(book_slot())
