
import traceback
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
# from app.core.browser_queue import browser_lock
from app.core.browser import new_page


async def search_wellfound(data):

    # async with browser_lock:

        page = await new_page()

        try:

            print(f"\n[{data['requestId']}] Opening Wellfound...")

            await page.goto(
                "https://wellfound.com/jobs",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            await page.wait_for_selector(
                '[data-test="SearchBar"]',
                timeout=30000,
            )

            print("✓ Jobs page loaded")

            # =====================================================
            # SEARCH KEYWORD
            # =====================================================

            role_button = page.locator(
                '[data-test="SearchBar-RoleSelect-FocusButton"]'
            )

            await role_button.click(timeout=10000)

            textbox = page.locator(
                'input[id^="react-select-"][aria-autocomplete="list"]'
            ).last

            await textbox.wait_for(
                state="visible",
                timeout=10000,
            )

            #

            try:
                await textbox.press("Meta+A")
            except Exception:
                await textbox.press("Control+A")

            await textbox.press("Backspace")

            await textbox.type(
                data["keyword"],
                delay=40,
            )

            print(f"✓ Typed: {data['keyword']}")

            await textbox.press("Enter")

            print("✓ Search submitted")

            await page.wait_for_timeout(1500)

            try:
                await page.wait_for_load_state(
                    "networkidle",
                    timeout=10000,
                )
            except Exception:
                pass

            print("✓ Search completed")

            # =====================================================
            # JOB CARDS
            # =====================================================

            card_selector = 'a[class*="styles_jobLink__"][href^="/jobs/"]'

            print("\nLoading all jobs...")

            previous_count = 0
            stable_rounds = 0
            MAX_SCROLLS = 40

            for scroll in range(MAX_SCROLLS):

                job_cards = page.locator(card_selector)

                current_count = await job_cards.count()

                print(f"Scroll {scroll + 1}: {current_count} jobs")

                if current_count == previous_count:
                    stable_rounds += 1
                else:
                    stable_rounds = 0

                if stable_rounds >= 2:
                    print("✓ No new jobs detected")
                    break

                previous_count = current_count

                await page.evaluate("""
                    window.scrollTo(
                        0,
                        document.body.scrollHeight
                    )
                """)

                await page.wait_for_timeout(1500)

            total_jobs = await job_cards.count()

            print(f"Final Job Count: {total_jobs}")

            print(f"Found {total_jobs} job cards")

            jobs = []

            for i in range(total_jobs):

                try:

                    card = job_cards.nth(i)

                    # -----------------------------------------
                    # URL
                    # -----------------------------------------

                    href = await card.get_attribute("href")

                    if not href:
                        continue

                    url = (
                        href
                        if href.startswith("http")
                        else f"https://wellfound.com{href}"
                    )

                    job_slug = href.split("/jobs/")[-1]

                    job_id = job_slug.split("-")[0]

                    # -----------------------------------------
                    # Title
                    # -----------------------------------------

                    try:
                        title = await card.locator(
                            'span[class*="styles_title__"]'
                        ).inner_text()
                    except Exception:
                        title = None

                    # -----------------------------------------
                    # Locations
                    # -----------------------------------------

                    try:
                        locations = await card.locator(
                            'span[class*="styles_location__"]'
                        ).all_inner_texts()
                    except Exception:
                        locations = []

                    work_mode = None
                    location = None

                    if len(locations) == 1:
                        location = locations[0]

                    elif len(locations) >= 2:
                        work_mode = locations[0]
                        location = locations[1]

                    # -----------------------------------------
                    # Salary
                    # -----------------------------------------

                    try:
                        salary = await card.locator(
                            'span[class*="styles_compensation__"]'
                        ).inner_text()
                    except Exception:
                        salary = None

                    # -----------------------------------------
                    # Posted
                    # -----------------------------------------

                    posted = None

                    try:

                        spans = await card.locator("span").all_inner_texts()

                        for span in spans:

                            if "posted" in span.lower():

                                posted = span

                                break

                    except Exception:

                        pass

                    # -----------------------------------------
                    # Recruiter Active
                    # -----------------------------------------

                    recruiter_active = False

                    try:

                        spans = await card.locator("span").all_inner_texts()

                        recruiter_active = any(
                            "recruiter recently active" in s.lower()
                            for s in spans
                        )

                    except Exception:

                        pass

                    # -----------------------------------------
                    # Save
                    # -----------------------------------------
                    if not title:
                        continue

                    jobs.append({

                        "provider": "Wellfound",

                        "jobId": job_id,

                        "title": title,

                        "url": url,

                        "location": location,

                        "workMode": work_mode,

                        "salary": salary,

                        "posted": posted,

                        "recruiterActive": recruiter_active,

                    })

                    print(f"[{i+1}/{total_jobs}] {title}")

                except Exception as e:

                    print(f"[Card {i}] Failed")

                    traceback.print_exc()

            print()

            print("=" * 60)
            print(f"Extracted {len(jobs)} jobs")
            print("=" * 60)

            return {
                "requestId": data["requestId"],
                "status": "SUCCESS",
                "provider": "Wellfound",
                "count": len(jobs),
                "jobs": jobs,
            }


        except PlaywrightTimeoutError as e:

            print(e)

            return {
                "status": "FAILED",
                "provider": "Wellfound",
                "count": 0,
                "jobs": [],
                "error": str(e),
            }

        except Exception as e:

            traceback.print_exc()

            return {
                "status": "FAILED",
                "provider": "Wellfound",
                "count": 0,
                "jobs": [],
                "error": str(e),
            }
            
        finally: 
            await page.close()