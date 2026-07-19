import traceback

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.core.browser import new_page
from app.core.browser_queue import browser_lock


async def search_internshala(data):

    # async with browser_lock:

        page = await new_page()

        try:

            print(f"\n[{data['requestId']}] Opening Internshala...")

            await page.goto(
                "https://internshala.com/jobs",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            print("✓ Internshala opened")

            # =====================================================
            # PROFILE
            # =====================================================

            profile = page.locator(
                "#select_category_chosen input.chosen-search-input"
            )

            await profile.wait_for(
                state="visible",
                timeout=10000,
            )

            await profile.click()

            await profile.fill("")

            await profile.type(
                data["keyword"],
                delay=15,
            )

            print(f"✓ Typed Profile : {data['keyword']}")

            option = page.locator(
                ".chosen-results li.active-result"
            ).first

            await option.wait_for(
                state="visible",
                timeout=3000,
            )

            await profile.press("ArrowDown")
            await profile.press("Enter")

            print("✓ Profile selected")

            await page.wait_for_timeout(100)

            # =====================================================
            # LOCATIONS
            # =====================================================

            locations = [
                "Noida",
                "Delhi",
                "Gurgaon",
            ]

            location = page.locator(
                "#city_sidebar_chosen input.chosen-search-input"
            )

            await location.wait_for(
                state="visible",
                timeout=10000,
            )

            for city in locations:

                await location.click()

                await location.fill("")

                await location.type(
                    city,
                    delay=15,
                )

                print(f"✓ Typed Location : {city}")

                option = page.locator(
                    ".chosen-results li.active-result"
                ).first

                await option.wait_for(
                    state="visible",
                    timeout=3000,
                )

                await location.press("ArrowDown")
                await location.press("Enter")

                print(f"✓ Selected : {city}")

                await page.wait_for_timeout(75)

            # =====================================================
            # WORK FROM HOME
            # =====================================================

            remote = page.locator("#remote_job_check_box")

            await remote.wait_for(
                state="visible",
                timeout=10000,
            )

            await remote.click()

            print("✓ Work From Home selected")

            await page.wait_for_timeout(75)

            # =====================================================
            # EXPERIENCE
            # =====================================================

            experience = page.locator(
                "#select_experience_chosen input.chosen-search-input"
            )

            await experience.wait_for(
                state="visible",
                timeout=10000,
            )

            await experience.click()

            await experience.fill("")

            await experience.type(
                "Fresher",
                delay=15,
            )

            print("✓ Typed Experience : Fresher")

            option = page.locator(
                ".chosen-results li.active-result"
            ).first

            await option.wait_for(
                state="visible",
                timeout=3000,
            )

            await experience.press("ArrowDown")
            await experience.press("Enter")

            print("✓ Selected Experience : Fresher")

            await page.wait_for_timeout(100)

            # =====================================================
            # LOAD ALL JOBS
            # =====================================================

            card_selector = 'div[id^="individual_internship_"]'

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

                await cards.nth(current_count - 1).scroll_into_view_if_needed()

                await page.wait_for_timeout(800)

            print(f"Final Job Count : {previous_count}")

            cards = page.locator(card_selector)

            total_jobs = await cards.count()

            print(f"Found {total_jobs} jobs")



            # =====================================================
            # JOBS
            # =====================================================

            jobs = []

            for i in range(total_jobs):

                try:

                    card = cards.nth(i)

                    

                    job = await card.evaluate("""
                    (card) => {

                        const q = (selector) => card.querySelector(selector);
                        const qa = (selector) => [...card.querySelectorAll(selector)];

                        const text = (selector) => {
                            const el = q(selector);
                            return el ? el.textContent.trim() : null;
                        };

                        let posted = null;

                        const detail = q(".detail-row-2-container");

                        if (detail) {

                            const text = detail.textContent.toLowerCase();

                            const match = text.match(
                                /(today|yesterday|\d+\s+(minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)\s+ago|just now)/
                            );

                            if (match) {
                                posted = match[0];
                            }
                        }

                        const experience = (() => {

                            const icon = q(".ic-16-briefcase");

                            if (!icon) return null;

                            const span = icon.parentElement.querySelector("span");

                            return span ? span.textContent.trim() : null;

                        })();

                        return {

                            href: card.dataset.href,

                            jobId: card.getAttribute("internshipid"),

                            title: text("a.job-title-href"),

                            company: text("p.company-name"),

                            location: text(".row-1-item.locations"),

                            stipend: text(".stipend"),

                            experience,

                            description: text(".about_job .text"),

                            posted,

                            skills: qa(".job_skill")
                                .map(e => e.textContent.trim())
                                .filter(Boolean)

                        };

                    }
                    """)

                    # ----------------------------------
                    # POSTED FILTER
                    # ----------------------------------

                    posted = job["posted"]

                    if posted:

                        if "day" in posted:

                            try:

                                days = int(posted.split()[0])

                                if days >= 3:

                                    continue

                            except:

                                pass

                        elif (
                            "week" in posted
                            or "month" in posted
                            or "year" in posted
                        ):

                            continue

                    jobs.append({

                        "provider": "Internshala",

                        "jobId": job["jobId"],

                        "company": job["company"],

                        "title": job["title"],

                        "url": (
                            f"https://internshala.com{job['href']}"
                            if job["href"]
                            else None
                        ),

                        "location": job["location"],

                        "stipend": job["stipend"],

                        "experience": job["experience"],

                        "description": job["description"],

                        "skills": job["skills"],

                        "posted": posted,

                    })

                    if len(jobs) % 20 == 0:
                        print(f"Extracted {len(jobs)} jobs...")

                except Exception:

                    traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "SUCCESS",

                "provider": "Internshala",

                "count": len(jobs),

                "jobs": jobs,

            }

        except PlaywrightTimeoutError as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Internshala",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }

        except Exception as e:

            traceback.print_exc()

            return {

                "requestId": data["requestId"],

                "status": "FAILED",

                "provider": "Internshala",

                "count": 0,

                "jobs": [],

                "error": str(e),

            }

        finally:

            await page.close()