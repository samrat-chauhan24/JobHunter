import traceback

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.core.browser import new_page

from app.core.browser_queue import browser_lock

async def search_hirist(data):

    async with browser_lock:

        page = await new_page()

        try:

            print(f"\n[{data['requestId']}] Opening Hirist...")

            await page.goto(
                "https://www.hirist.tech",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            print("✓ Hirist opened")

            # =====================================================
            # OPEN SEARCH MODAL
            # =====================================================

            search_icon = page.locator('img[src*="search"]')

            await search_icon.wait_for(
                state="visible",
                timeout=10000,
            )

            await search_icon.click()

            print("✓ Search icon clicked")

            await page.wait_for_timeout(1000)

            keyword = page.locator('input[name="query"]')

            await keyword.wait_for(
                state="visible",
                timeout=10000,
            )

            print("✓ Search modal visible")

            # =====================================================
            # KEYWORD
            # =====================================================

            await keyword.fill(data["keyword"])

            print(f"✓ Keyword: {data['keyword']}")

            # =====================================================
            # SEARCH
            # =====================================================

            search_button = page.get_by_role(
                "button",
                name="Search",
            )

            await search_button.click()

            print("✓ Search clicked")

            await page.wait_for_selector(
                '[data-testid^="job-list-"]',
                timeout=30000,
            )

            await page.wait_for_timeout(1000)


            print("✓ Search completed")
            # =====================================================
            # LOAD ALL JOBS
            # =====================================================

            card_selector = '[data-testid^="job-list-"]'

            print("\nLoading all jobs...")

            previous_count = 0
            stable_rounds = 0
            MAX_SCROLLS = 40

            for scroll in range(MAX_SCROLLS):

                cards = page.locator(card_selector)
                current_count = await cards.count()

                print(f"Scroll {scroll + 1}: {current_count} jobs")

                if current_count == previous_count:
                    stable_rounds += 1
                else:
                    stable_rounds = 0

                if stable_rounds >= 3:
                    print("✓ No new jobs detected")
                    break

                previous_count = current_count

                # Scroll the last loaded card into view
                await cards.nth(current_count - 1).scroll_into_view_if_needed()

                await page.wait_for_timeout(2000)

            print(f"Final Job Count: {previous_count}")

            cards = page.locator(card_selector)
            total_jobs = await cards.count()

            print(f"Found {total_jobs} job cards")

            # =====================================================
            # JOBS
            # =====================================================

            card_selector = '[data-testid^="job-list-"]'


            jobs = []

            for i in range(total_jobs):

                try:

                    card = cards.nth(i)


                    # -----------------------------------------
                    # URL
                    # -----------------------------------------

                    anchor = card.locator("xpath=ancestor::a[1]")

                    href = await anchor.get_attribute("href")

                    if href:

                        url = (
                            href
                            if href.startswith("http")
                            else f"https://www.hirist.tech{href}"
                        )

                    else:

                        url = None

                    job_id = href.split("/")[-1] if href else None


                    # -----------------------------------------
                    # TITLE + COMPANY
                    # -----------------------------------------

                    title = await card.locator(
                        '[data-testid="job_title"]'
                    ).inner_text()

                    title = title.strip()

                    company = None


                    # -----------------------------------------
                    # EXPERIENCE
                    # -----------------------------------------

                    try:

                        experience = await card.locator(
                            '[data-testid="job_experience"]'
                        ).inner_text()

                    except Exception:

                        experience = None


                    # -----------------------------------------
                    # LOCATION
                    # -----------------------------------------

                    try:

                        location = await card.locator(
                            '[data-testid="job_location"]'
                        ).inner_text()

                    except Exception:

                        location = None


                    # -----------------------------------------
                    # POSTED
                    # -----------------------------------------

                    try:

                        posted = await card.locator(
                            '[data-testid="date_posted_mobile"]'
                        ).inner_text()

                    except Exception:

                        posted = None


                    # -----------------------------------------
                    # TAGS / SKILLS
                    # -----------------------------------------

                    try:

                        skills = await card.locator(
                            '[data-testid^="job_tag_"]'
                        ).all_inner_texts()

                    except Exception:

                        skills = []


                    # -----------------------------------------
                    # SAVE
                    # -----------------------------------------

                    jobs.append({

                        "provider": "Hirist",

                        "jobId": job_id,

                        # "company": company,

                        "title": title,

                        "url": url,

                        "location": location,

                        "experience": experience,

                        "posted": posted,

                        "skills": skills,

                    })


                    print(
                        f"[{i+1}/{total_jobs}] {title}"
                    )

                except Exception:

                    print(f"[Card {i}] Failed")

                    traceback.print_exc()

            print()

            print("=" * 60)
            print(f"Extracted {len(jobs)} jobs")
            print("=" * 60)

            return {

                "requestId": data["requestId"],

                "status": "SUCCESS",

                "provider": "Hirist",

                "count": len(jobs),

                "jobs": jobs,

            }

        except PlaywrightTimeoutError as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Hirist",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }

        except Exception as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Hirist",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }

        finally:

            await page.close()