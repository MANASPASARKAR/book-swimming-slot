import asyncio
import os
import resend
from playwright.async_api import async_playwright

EMAIL = os.environ["LOGIN_EMAIL"]
PASSWORD = os.environ["LOGIN_PASSWORD"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_APP_PASSWORD = os.environ["SENDER_APP_PASSWORD"]
RECEIVER_EMAIL = os.environ["RECEIVER_EMAIL"]

LOGIN_URL = "https://sports.mitwpu.edu.in/login"
SLOT_URL = "https://sports.mitwpu.edu.in/sports/b4e13520-6b4f-4d88-abb0-03b6bf6650d4/slots/5792a435-0f22-4e76-96e8-0cee9ca393b7/seats"

resend.api_key =  "re_XySPLEDJ_7b9APNmef3YVhLGYqCcWPGtR"

def send_email():
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "impasarkarmanas@gmail.com",
        "subject": "Swimming Slot Booked ✅",
        "html": "<p>Your swimming slot has been booked successfully.</p>"
    })

async def book_slot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # ── Step 1: Login ──────────────────────────────────────────
            print("Going to login page...")
            await page.goto(LOGIN_URL)

            await page.wait_for_selector("#email", state="visible")
            await page.wait_for_selector("#password", state="visible")
            print("Login form ready.")

            await page.fill("#email", EMAIL)
            await page.fill("#password", PASSWORD)

            await page.wait_for_timeout(3000)
            await page.screenshot(path="debug_before_login.png", full_page=True)
            print("Filled credentials. Clicking login...")

            await page.click('button[type="submit"]')
            await page.wait_for_url(lambda url: "login" not in url, timeout=15000)
            print(f"Logged in! URL: {page.url}")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="debug_after_login.png", full_page=True)

            # ── Step 2: Go to swimming slot page ──────────────────────
            print("Navigating to swimming slot...")
            await page.goto(SLOT_URL)
            await page.wait_for_timeout(5000)  # let slots render
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="debug_seats.png", full_page=True)
            print("Slots page loaded.")

            # ── Step 3: Check if any seats are available ───────────────
            seats = await page.query_selector_all("button.bg-emerald-500")
            print(f"Found {len(seats)} available seat(s).")

            if len(seats) == 0:
                send_email(
                    subject="⚠️ Swimming Booking — No Seats Available",
                    body="The script ran successfully but found no available seats for the 5:00 PM slot. All spots are already booked."
                )
                print("No seats available. Exiting.")
                await browser.close()
                return

            print("Clicking first available seat...")
            await seats[0].click()

            # ── Step 4: Wait for modal ─────────────────────────────────
            await page.wait_for_selector("#terms", state="visible", timeout=10000)
            await page.wait_for_timeout(2000)
            await page.screenshot(path="debug_modal.png", full_page=True)
            print("Modal opened.")

            # ── Step 5: Check Terms & Conditions ──────────────────────
            await page.click("#terms")
            await page.wait_for_timeout(1000)
            print("T&C checked.")

            # ── Step 6: Click Confirm ──────────────────────────────────
            confirm_btn = await page.wait_for_selector("button:has-text('Confirm')", state="visible", timeout=5000)
            await confirm_btn.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="booking_result.png", full_page=True)
            print("✅ Swimming slot booked!")

            send_email(
                subject="✅ Swimming Slot Booked — 5:00 PM",
                body="Your swimming slot for 5:00 PM - 5:45 PM has been successfully booked. See you at the pool!"
            )

        except Exception as e:
            print(f"ERROR: {e}")
            await page.screenshot(path="debug_error.png", full_page=True)

            send_email(
                subject="❌ Swimming Booking Failed",
                body=f"The swimming booking script ran but failed with the following error:\n\n{e}\n\nCheck the screenshots in GitHub Actions for more details."
            )

        await browser.close()

asyncio.run(book_slot())            
