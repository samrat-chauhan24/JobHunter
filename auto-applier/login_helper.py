import os
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.join(os.getcwd(), "user_job_profile")

SITES = [
    "https://wellfound.com",
    "https://internshala.com",
    "https://www.hirist.tech",
    "https://www.naukri.com/campus",
]


def run():
    print("\n" + "=" * 60)
    print("JobHunter Login Helper")
    print("=" * 60)
    print(f"Using profile: {PROFILE_DIR}")
    print()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
            ignore_default_args=["--enable-automation"],
            no_viewport=True,
        )

        # Reuse an existing page if available
        if context.pages:
            context.pages[0].close()

        for url in SITES:
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")

        print("\n✅ Login helper is ready.")
        print("Verify that you are logged into each site.")
        print("When finished, close the browser or press Enter here.")

        input("\nPress Enter to exit...")

        context.close()


if __name__ == "__main__":
    run()