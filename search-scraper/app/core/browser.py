from pathlib import Path

from playwright.async_api import async_playwright

playwright = None
browser_context = None

PROFILE_DIR = (
    Path(__file__)
    .parent.parent
    / "profiles"
    / "wellfound"
)


async def start_browser():

    global playwright
    global browser_context

    if browser_context is not None:
        return browser_context

    playwright = await async_playwright().start()

    browser_context = await playwright.chromium.launch_persistent_context(

        user_data_dir=str(PROFILE_DIR),

        headless=False,

        viewport={
            "width": 1440,
            "height": 900,
        },

        args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],

    )

    print("✓ Persistent Chromium Started")

    return browser_context


async def stop_browser():

    global playwright
    global browser_context

    if browser_context:
        await browser_context.close()

    if playwright:
        await playwright.stop()

    print("✓ Chromium Closed")


async def new_page():

    global browser_context

    if browser_context is None:
        await start_browser()

    page = await browser_context.new_page()

    return page