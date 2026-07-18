import traceback

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.core.browser import new_page
from app.core.browser_queue import browser_lock


async def search_naukri(data):

    # async with browser_lock:

        page = await new_page()

        try:

            print(f"\n[{data['requestId']}] Opening Naukri...")

            await page.goto(
                "https://www.naukri.com/campus",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            print("✓ Naukri opened")

            # =====================================================
            # OPEN SEARCH BAR
            # =====================================================

            search_bar = page.locator("#ni-gnb-searchbar")

            await search_bar.wait_for(
                state="visible",
                timeout=10000,
            )

            await search_bar.click()

            print("✓ Search bar opened")

            await page.wait_for_timeout(500)

            # =====================================================
            # KEYWORD
            # =====================================================

            keyword = page.locator(
                "input.suggestor-input[placeholder*='keyword']"
            )

            await keyword.wait_for(state="visible", timeout=10000)

            await keyword.click()
            await keyword.fill(data["keyword"])

            print(f"✓ Keyword: {data['keyword']}")

            # =====================================================
            # JOB TYPE
            # =====================================================

            dropdown = page.locator(".dropdownMainContainer")

            await dropdown.wait_for(
                state="visible",
                timeout=10000,
            )

            await dropdown.click()

            await page.get_by_text(
                "Job",
                exact=True,
            ).click()

            await page.wait_for_timeout(500)

            print("✓ Job type selected")

            print(f"✓ Keyword: {data['keyword']}")

            # =====================================================
            # LOCATION
            # =====================================================

            location = page.get_by_placeholder("Enter location")

            await location.wait_for(
                state="visible",
                timeout=10000,
            )

            await location.click()

            # Clear any existing value
            await location.fill("")

            # Type both locations
            await location.fill("Noida, Gurugram, Delhi / NCR")

            # Commit the value
            await location.press("Tab")

            # Let React update its state
            await page.wait_for_timeout(500)

            print("✓ Locations: Noida, Gurugram")

            # =====================================================
            # SEARCH
            # =====================================================

            current_url = page.url

            search_button = page.get_by_role(
                "button",
                name="Search",
            )

            await search_button.click()

            print("✓ Search clicked")

            await page.wait_for_url(
                lambda url: url != current_url,
                timeout=30000,
            )

            await page.wait_for_load_state("domcontentloaded")

            print("✓ Search completed")

            # =====================================================
            # SORT BY DATE
            # =====================================================

            sort_dropdown = page.locator(
                "#filter-sort"
            )

            await sort_dropdown.wait_for(
                state="visible",
                timeout=10000,
            )

            await sort_dropdown.click()

            await page.get_by_text(
                "Date",
                exact=True,
            ).click()

            print("✓ Sorted by Date")

            await page.wait_for_load_state("domcontentloaded")

            await page.wait_for_timeout(2000)

            print("✓ Results ready")

            # =====================================================
            # JOBS
            # =====================================================

            card_selector = ".srp-jobtuple-wrapper"

            await page.wait_for_selector(
                card_selector,
                timeout=15000,
            )

            cards = page.locator(card_selector)

            total_jobs = await cards.count()

            print(f"\nFound {total_jobs} jobs\n")

            jobs = []

            for i in range(total_jobs):

                try:

                    card = cards.nth(i)

                    # -----------------------------------------
                    # JOB ID
                    # -----------------------------------------

                    job_id = await card.get_attribute("data-job-id")

                    # -----------------------------------------
                    # URL
                    # -----------------------------------------

                    try:

                        anchor = card.locator("a.title")

                        url = await anchor.get_attribute("href")

                    except Exception:

                        url = None

                    # -----------------------------------------
                    # TITLE
                    # -----------------------------------------

                    try:

                        title = await card.locator(
                            "a.title"
                        ).inner_text()

                        title = title.strip()

                    except Exception:

                        title = None

                    # -----------------------------------------
                    # COMPANY
                    # -----------------------------------------

                    try:

                        company = await card.locator(
                            "a.comp-name"
                        ).inner_text()

                        company = company.strip()

                    except Exception:

                        company = None

                    # -----------------------------------------
                    # EXPERIENCE
                    # -----------------------------------------

                    try:

                        experience = await card.locator(
                            "span.expwdth"
                        ).inner_text()

                        experience = experience.strip()

                    except Exception:

                        experience = None

                    # -----------------------------------------
                    # LOCATION
                    # -----------------------------------------

                    try:

                        location = await card.locator(
                            "span.locWdth"
                        ).inner_text()

                        location = location.strip()

                    except Exception:

                        location = None

                    # -----------------------------------------
                    # DESCRIPTION
                    # -----------------------------------------

                    try:

                        description = await card.locator(
                            "span.job-desc"
                        ).inner_text()

                        description = description.strip()

                    except Exception:

                        description = None

                    # -----------------------------------------
                    # POSTED
                    # -----------------------------------------

                    try:

                        posted = await card.locator(
                            "span.job-post-day"
                        ).inner_text()

                        posted = posted.strip()

                    except Exception:

                        posted = None

                    # -----------------------------------------
                    # SKILLS
                    # -----------------------------------------

                    try:

                        skills = await card.locator(
                            ".tuple-tags-container a, .tuple-tags-container span"
                        ).all_inner_texts()

                        skills = [skill.strip() for skill in skills if skill.strip()]

                    except Exception:

                        skills = []

                    # -----------------------------------------
                    # SAVE
                    # -----------------------------------------

                    jobs.append({

                        "provider": "Naukri",

                        "jobId": job_id,

                        "company": company,

                        "title": title,

                        "url": url,

                        "location": location,

                        "experience": experience,

                        "description": description,

                        "posted": posted,

                        "skills": skills,

                    })

                    print(
                        f"[{i+1}/{total_jobs}] {title}"
                    )

                except Exception:

                    print(f"[Card {i+1}] Failed")

                    traceback.print_exc()

            print()

            print("=" * 60)
            print(f"Extracted {len(jobs)} jobs")
            print("=" * 60)

            return {

                "requestId": data["requestId"],

                "status": "SUCCESS",

                "provider": "Naukri",

                "count": len(jobs),

                "jobs": jobs,

            }

        except PlaywrightTimeoutError as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Naukri",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }

        except Exception as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Naukri",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }
        finally:

            await page.close()

        