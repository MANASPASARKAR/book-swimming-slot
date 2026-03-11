import asyncio
import os
from playwright.async_api import async_playwright

# --- Config from environment variables (GitHub Secrets) ---
EMAIL = os.environ["LOGIN_EMAIL"]
PASSWORD = os.environ["LOGIN_PASSWORD"]
SLOT_URL = "https://sports.mitwpu.edu.in/sports/b4e13520-6b4f-4d88-abb0-03b6bf6650d4/slots/5792a435-0f22-4e76-96e8-0cee9ca393b7/seats"
LOGIN_URL = "https://sports.mitwpu.edu.in/login"

async def book_slot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ── Step 1: Login ──────────────────────────────────────────────
        print("Navigating to login page...")
        await page.goto(LOGIN_URL, wait_until="networkidle")

        print("Filling credentials...")
        await page.fill('input[type="email"], input[name="email"]', EMAIL)
        await page.fill('input[type="password"], input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')

        await page.wait_for_load_state("networkidle")
        print(f"Current URL after login: {page.url}")

        # ── Step 2: Go directly to the swimming slot ───────────────────
        print("Navigating to swimming slot...")
        await page.goto(SLOT_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)  # let seats render
        print(f"Slot page URL: {page.url}")

        # ── Step 3: Click the first available (green) seat ────────────
        # Try common patterns for green/available seats
        green_seat_selectors = [
            ".seat.available",
            ".seat-available",
            "[class*='available']",
            "[class*='green']",
            "[class*='open']",
            "button.available",
            ".slot-seat:not(.booked):not(.disabled)",
        ]

        seat_clicked = False
        for selector in green_seat_selectors:
            seats = await page.query_selector_all(selector)
            if seats:
                print(f"Found {len(seats)} available seat(s) with selector: {selector}")
                await seats[0].click()
                seat_clicked = True
                print("Clicked first available seat.")
                await page.wait_for_timeout(1500)
                break

        if not seat_clicked:
            # Fallback: take a screenshot to debug
            await page.screenshot(path="debug_seats.png")
            print("ERROR: Could not find any green/available seat. Screenshot saved.")
            await browser.close()
            return

        # ── Step 4: Confirm booking ────────────────────────────────────
        confirm_selectors = [
            "button:has-text('Confirm')",
            "button:has-text('Book')",
            "button:has-text('Confirm Booking')",
            "button:has-text('Proceed')",
            "[class*='confirm']",
        ]

        confirmed = False
        for selector in confirm_selectors:
            btn = await page.query_selector(selector)
            if btn:
                await btn.click()
                confirmed = True
                print(f"Clicked confirm button: {selector}")
                await page.wait_for_timeout(2000)
                break

        if confirmed:
            await page.screenshot(path="booking_success.png")
            print("✅ Booking confirmed! Screenshot saved as booking_success.png")
        else:
            await page.screenshot(path="debug_confirm.png")
            print("ERROR: Could not find confirm button. Screenshot saved.")

        await browser.close()

asyncio.run(book_slot())
