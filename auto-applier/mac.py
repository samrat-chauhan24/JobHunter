import time
import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SHEET_URL = os.getenv("SHEET_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TABS_TO_PROCESS = ["ToBeApplied"]

groq_client = Groq(api_key=GROQ_API_KEY)

def get_sheet(tab_name):
    print(f"Connecting to Google Sheets (Tab: {tab_name})...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open_by_url(SHEET_URL).worksheet(tab_name)

RESUME_CONTEXT = """
Candidate Name: Samrat Chauhan
Email: chauhansamrat835@gmail.com
Phone: +91-7668795490
GitHub: github.com/samrat-chauhan24
LinkedIn: linkedin.com/in/samratchauhan

Profile Summary:
Third-year Computer Science (AI & ML) student with hands-on experience building AI-powered Full-Stack Web and Mobile applications using React.js, React Native, FastAPI, LangChain, LangGraph, and RAG. Experienced in developing intelligent automation workflows, AI agents, production-grade frontend architectures, and scalable REST APIs with a strong foundation in Data Structures and Algorithms using Java. :contentReference[oaicite:0]{index=0}

Technical Skills:
- AI & Generative AI: LangChain, LangGraph, Retrieval-Augmented Generation (RAG), AI Agents, Vector Databases, Prompt Engineering, LLM Integration
- Frontend: React.js, Next.js, React Native, Tailwind CSS, HTML5, CSS3, Responsive UI
- Backend: FastAPI, Node.js, REST APIs
- Databases: PostgreSQL, MongoDB, Firebase
- Languages: Java, Python, JavaScript (ES6+), TypeScript, SQL
- Automation & Tools: n8n, Docker, Git, GitHub, Postman, VS Code

Projects:
1. JuryAI:
   AI-powered legal assistant with React Native and React.js frontends backed by FastAPI, LangGraph, and RAG. Supports structured legal responses, country-specific guidance, comparison mode, persistent chat history, and reusable cross-platform UI architecture.

2. Leet'O Tracker AI:
   AI-powered coding analytics platform built using Next.js, FastAPI, PostgreSQL, LangGraph, and n8n. Generates personalized performance insights, revision schedules, interview recommendations, and automated coding reports.

3. PickMyPhone AI (Ongoing):
   AI-powered smartphone recommendation platform using React.js, FastAPI, PostgreSQL, LangChain, LangGraph, and n8n. Provides personalized recommendations based on user preferences with automated catalog updates and intelligent search. :contentReference[oaicite:1]{index=1}

Education:
B.Tech in Computer Science & Engineering (AI & ML)
Meerut Institute of Engineering and Technology (2023–2027)
CGPA: 7.0/10. :contentReference[oaicite:2]{index=2}

Achievements:
- Top 10 team (out of 350+ teams) at TRIKON 3.0 Hackathon for building an AI-powered application within 36 hours.
- Participated in Cognizant Technoverse 2026 Hackathon.
- Solved 120+ Data Structures & Algorithms problems on LeetCode using Java. :contentReference[oaicite:3]{index=3}

Default Form Answers:
- Total Years of Experience: '1' (or 'Fresher / Entry Level' if text)
- Current CTC / Salary: '0'
- Expected CTC / Salary: '400000' (4 LPA)
- Notice Period: 'Immediate Joiner' or '0 days'
- Availability / Joining status: 'Immediate'
- Visa Sponsorship needed: 'No'
- Relocation: 'Yes' (Willing to relocate)
"""

def ask_llm_for_answer(question_text):
    system_prompt = f"""
    You are a highly advanced job application form-filling AI engine.
    Analyze the user's question and answer it accurately based on the following complete candidate profile:
    {RESUME_CONTEXT}
    
    CRITICAL RULES:
    1. If the question asks for years of experience, output ONLY '1'.
    2. If it asks for expected salary, output ONLY '400000'.
    3. If it asks for current salary/CTC, output ONLY '0'.
    4. If it asks about notice period, output ONLY 'Immediate Joiner'.
    5. For simple Yes/No choices, return ONLY 'Yes' or 'No'.
    6. For text descriptions or specific text options, be as brief and direct as possible. Do not use full sentences or punctuation unless necessary.
    """
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Form Question: {question_text}"}
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.1, 
            max_tokens=25
        )
        return chat_completion.choices[0].message.content.strip().replace(".", "")
    except Exception as e:
        print(f"    ⚠️ Groq API Error: {e}")
        return "Yes"

def generate_cover_note(job_title, company):
    system_prompt = f"""
    Write a highly concise, impressive, and recruiter-friendly application note (maximum 3 short sentences) 
    for the position of {job_title} at {company} based strictly on this profile:
    {RESUME_CONTEXT}
    Tone: Professional and high-value. Sign off directly as 'Samrat Chauhan'. No placeholder brackets.
    """
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0.6, 
            max_tokens=120
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"I am a final-year CS (AI/ML) student with strong experience in MERN, Next.js, and multi-agent AI systems. I am highly interested in the {job_title} role at {company}. - Samrat Chauhan"

def handle_generic_form_elements(page, job_title, company):
    try:
        all_inputs = page.locator("input[type='text'], input:not([type]), textarea, input[type='number']")
        for i in range(all_inputs.count()):
            field = all_inputs.nth(i)
            if field.is_visible() and field.is_editable():
                placeholder = (field.get_attribute("placeholder") or "").lower()
                name_attr = (field.get_attribute("name") or "").lower()
                id_attr = (field.get_attribute("id") or "").lower()
                
                label_text = ""
                if id_attr:
                    label_el = page.locator(f"label[for='{id_attr}']").first
                    if label_el.is_visible(): label_text = label_el.inner_text()
                
                context_string = f"{placeholder} {name_attr} {id_attr} {label_text}"
                
                if any(k in context_string.lower() for k in ["cover", "note", "why", "statement"]):
                    answer = generate_cover_note(job_title, company)
                else:
                    answer = ask_llm_for_answer(context_string if len(context_string.strip()) > 3 else "Value Required")
                
                field.fill(str(answer))

        selection_containers = page.locator("fieldset, div.form-group, div.question-container, div[role='radiogroup']")
        for i in range(selection_containers.count()):
            container = selection_containers.nth(i)
            if container.is_visible():
                header = container.locator("legend, label, p, h1, h2, h3").first
                question = header.inner_text() if header.is_visible() else "Select Option"
                
                target_choice = ask_llm_for_answer(f"Based on the options, choose the best keyword choice for: {question}")
                
                options = container.locator("label, div[role='radio'], span")
                for j in range(options.count()):
                    opt = options.nth(j)
                    if opt.is_visible() and target_choice.lower() in opt.inner_text().lower():
                        opt.evaluate("el => el.click()") 
                        break
                        
    except Exception as e:
        print(f"    ⚠️ Dynamic form fill component encountered an issue: {e}")

def apply_adzuna(page, url, job_title, company):
    print(f"  -> Navigating to Adzuna Job...")
    try:
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        
        apply_button = page.locator("a:has-text('Apply'), button:has-text('Apply')").first
        if apply_button.is_visible():
            href = apply_button.get_attribute("href")
            if href:
                if href.startswith("/"): href = "https://www.adzuna.in" + href
                page.goto(href)
                page.wait_for_timeout(2000)
                return True
            else:
                apply_button.evaluate("el => el.click()") 
                page.wait_for_timeout(2000)
                return True
        return False
    except Exception as e:
        print(f"  -> ❌ Adzuna Error: {e}")
        return False

def apply_linkedin(page, url, job_title, company):
    print(f"  -> Navigating to LinkedIn Job...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        
        if "linkedin.com/jobs/view" not in page.url:
            return False
            
        easy_apply_btn = page.locator("role=button[name='Easy Apply'i]")
        if easy_apply_btn.first.is_visible():
            easy_apply_btn.first.evaluate("el => el.click()")
            
            for step in range(6):
                page.wait_for_timeout(1000)
                handle_generic_form_elements(page, job_title, company)
                
                next_btn = page.locator("button:has-text('Next'), button:has-text('Review')").first
                submit_btn = page.locator("button:has-text('Submit application')").first
                
                if submit_btn.is_visible():
                    submit_btn.evaluate("el => el.click()") 
                    page.wait_for_timeout(2500)
                    close_btn = page.locator("button[aria-label='Dismiss']").first
                    if close_btn.is_visible(): close_btn.evaluate("el => el.click()")
                    return True
                elif next_btn.is_visible():
                    next_btn.evaluate("el => el.click()")
                else:
                    return False
            return True
        return False
    except Exception as e:
        print(f"  -> ❌ LinkedIn Error: {e}")
        return False

def apply_naukri(page, url, job_title, company):
    print(f"  -> Navigating to Naukri Job...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000) # Give Naukri UI time to render buttons
        
        # Check for the external company site redirect first
        external_apply = page.locator("button:has-text('Apply on company site'), a:has-text('Apply on company site')").first
        if external_apply.is_visible():
            print("  -> ⚠️ Job requires applying on company site. Skipping to avoid complex redirects.")
            return False
            
        # Standard Apply button filter
        apply_btn = page.locator("button:has-text('Apply')").filter(has_not_text="company site").first
        if apply_btn.is_visible():
            apply_btn.evaluate("el => el.click()") 
            page.wait_for_timeout(2500)
            
            # Catch common Naukri popup (Update Profile / Chatbot)
            update_btn = page.locator("button:has-text('Update and Apply')").first
            if update_btn.is_visible():
                update_btn.evaluate("el => el.click()")
                page.wait_for_timeout(2000)
                
            return True
        return False
    except Exception as e:
        print(f"  -> ❌ Naukri Error: {e}")
        return False

def apply_wellfound(page, url, job_title, company):
    print(f"  -> Navigating to Wellfound Job...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        
        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
        if apply_btn.is_visible():
            apply_btn.evaluate("el => el.click()")
            page.wait_for_timeout(1500)
            
            location_warning = page.locator("text='This job does not support'")
            if location_warning.first.is_visible():
                relocate_radio = page.locator("label:has-text('relocate')").first
                currently_in_radio = page.locator("label:has-text('currently in')").first
                
                if relocate_radio.is_visible(): 
                    relocate_radio.evaluate("el => el.click()")
                elif currently_in_radio.is_visible(): 
                    currently_in_radio.evaluate("el => el.click()")
                    
                page.wait_for_timeout(1000)
                
                # Handle the dynamic location dropdown
                dropdown_placeholder = page.locator("text='-'").first
                if dropdown_placeholder.is_visible():
                    # Click the dropdown box to open the list
                    dropdown_placeholder.click(force=True)
                    page.wait_for_timeout(500)
                    # Use keyboard simulation to select the very first city in the list
                    page.keyboard.press("ArrowDown")
                    page.wait_for_timeout(200)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(500)
            
            textarea = page.locator("textarea").first
            if textarea.is_visible():
                is_disabled = textarea.evaluate("el => el.disabled")
                if not is_disabled:
                    cover_note = generate_cover_note(job_title, company)
                    textarea.fill(cover_note)
            
            submit_btn = page.locator("button:has-text('Send application')").first
            if submit_btn.is_visible():
                is_disabled = submit_btn.evaluate("el => el.disabled")
                if not is_disabled:
                    submit_btn.evaluate("el => el.click()")
                    page.wait_for_timeout(3000) 
                    return True
                else:
                    print("  -> ⚠️ Job requires manual fields (Button Disabled). Skipping.")
                    return False
        return False
    except Exception as e:
        print(f"  -> ❌ Wellfound Error: {e}")
        return False

def apply_internshala(page, url, job_title, company):
    print(f"  -> Navigating to Internshala Job...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        apply_btn = page.locator("button:has-text('Apply now')").first
        if apply_btn.is_visible():
            apply_btn.evaluate("el => el.click()")
            page.wait_for_timeout(1500)
            
            textarea = page.locator("textarea").first
            if textarea.is_visible():
                is_disabled = textarea.evaluate("el => el.disabled")
                if not is_disabled:
                    cover_note = generate_cover_note(job_title, company)
                    textarea.fill(cover_note)
                
            proceed_btn = page.locator("button:has-text('Proceed to application')").first
            if proceed_btn.is_visible(): 
                proceed_btn.evaluate("el => el.click()")
                
            page.wait_for_timeout(3500)
            return True
        return False
    except Exception as e:
        print(f"  -> ❌ Internshala Error: {e}")
        return False

def apply_hirist(page, url, job_title, company):
    print(f"  -> Navigating to Hirist Job...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
        if apply_btn.is_visible():
            apply_btn.evaluate("el => el.click()") 
            page.wait_for_timeout(2500)
            return True
        return False
    except Exception as e:
        print(f"  -> ❌ Hirist Error: {e}")
        return False

def apply_generic_portal(page, url, job_title, company):
    print(f"  -> Navigating to Unknown/Generic Career Portal...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        input_mappings = {
            r"(first.*name|full.*name|name)": "Samrat Chauhan",
            r"(email)": "chauhansamrat837@gmail.com",
            r"(phone|mobile|contact)": "+917668795490",
            r"(linkedin)": "https://linkedin.com/in/samratchauhan",
            r"(github)": "https://github.com/samrat-chauhan24",
            r"(portfolio|website)": "https://github.com/samrat-chauhan24"
        }
        
        all_inputs = page.locator("input, textarea")
        for i in range(all_inputs.count()):
            field = all_inputs.nth(i)
            if not field.is_visible() or not field.is_editable(): continue
                
            placeholder = (field.get_attribute("placeholder") or "").lower()
            name_attr = (field.get_attribute("name") or "").lower()
            id_attr = (field.get_attribute("id") or "").lower()
            
            label_text = ""
            if id_attr:
                label_el = page.locator(f"label[for='{id_attr}']").first
                if label_el.is_visible(): label_text = label_el.inner_text().lower()
            
            combined_metadata = f"{placeholder} {name_attr} {id_attr} {label_text}"
            
            matched = False
            for pattern, value in input_mappings.items():
                if re.search(pattern, combined_metadata):
                    field.fill(value)
                    matched = True
                    break
            
            if not matched and (field.get_attribute("type") == "text" or field.tag_name() == "textarea"):
                question_prompt = label_text if label_text else (placeholder if placeholder else "Job Question")
                if any(k in combined_metadata for k in ["cover", "note", "why"]):
                    answer = generate_cover_note(job_title, company)
                else:
                    answer = ask_llm_for_answer(question_prompt)
                field.fill(str(answer))

        checkboxes = page.locator("input[type='checkbox']")
        for i in range(checkboxes.count()):
            cb = checkboxes.nth(i)
            if cb.is_visible() and not cb.is_checked(): 
                cb.evaluate("el => el.click()")

        handle_generic_form_elements(page, job_title, company)

        resume_filename = "Samrat_Chauhan_Resume1.pdf"
        if os.path.exists(resume_filename):
            file_inputs = page.locator("input[type='file']")
            for i in range(file_inputs.count()):
                f_input = file_inputs.nth(i)
                f_accept = (f_input.get_attribute("accept") or "").lower()
                if "pdf" in f_accept or "resume" in (f_input.get_attribute("name") or "").lower():
                    f_input.set_input_files(resume_filename)
                    break

        submit_btn = page.locator(
            "button:has-text('Submit'), button:has-text('Apply'), "
            "input[type='submit'], button:has-text('Submit Application')"
        ).first
        
        if submit_btn.is_visible():
            submit_btn.evaluate("el => el.click()") 
            page.wait_for_timeout(3000)
            return True
        return False
            
    except Exception as e:
        print(f"  -> ❌ Generic Portal Error: {e}")
        return False

def apply_jsearch(page, url, job_title, company):
    print(f"  -> Navigating to JSearch Link...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000) 
        
        final_url = page.url
        print(f"  -> JSearch Redirected to: {final_url}")
        
        if "adzuna" in final_url: return apply_adzuna(page, final_url, job_title, company)
        elif "linkedin.com" in final_url: return apply_linkedin(page, final_url, job_title, company)
        elif "naukri.com" in final_url: return apply_naukri(page, final_url, job_title, company)
        elif "wellfound.com" in final_url or "angel.co" in final_url: return apply_wellfound(page, final_url, job_title, company)
        elif "internshala.com" in final_url: return apply_internshala(page, final_url, job_title, company)
        elif "hirist.com" in final_url or "hirist.tech" in final_url: return apply_hirist(page, final_url, job_title, company)
        else:
            return apply_generic_portal(page, final_url, job_title, company)
    except Exception as e:
        print(f"  -> ❌ JSearch Error: {e}")
        return False

def main():
    print("\nLaunching Playwright with your secure profile...")
    
    with sync_playwright() as p:
        # MAC COMPATIBLE PLAYWRIGHT SETUP
        context = p.chromium.launch_persistent_context(
            user_data_dir="./user_job_profile",
            headless=False, 
            # Removed --start-maximized and added explicit viewport size for Mac
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0]

        for tab_name in TABS_TO_PROCESS:
            print(f"\n==========================================")
            print(f" 📂 NOW PROCESSING TAB: {tab_name}")
            print(f"==========================================")
            
            try:
                sheet = get_sheet(tab_name)
                records = sheet.get_all_records()
                headers = sheet.row_values(1)
                
                if "applied" in headers:
                    applied_col_index = headers.index("applied") + 1
                else:
                    continue

                for i, row in enumerate(records, start=2):
                    url = row.get("applyUrl", "") or row.get("jobUrl", "")
                    status = row.get("applied", "")
                    
                    if url and str(status).strip().upper() != "TRUE":
                        job_title = row.get("title", "Unknown Job")
                        company = row.get("company", "Unknown Company")
                        print(f"\nProcessing Row {i}: {job_title} at {company}")
                        
                        success = False
                        
                        if "jsearch" in url or "j-search" in url: 
                            success = apply_jsearch(page, url, job_title, company)
                        elif "adzuna" in url: success = apply_adzuna(page, url, job_title, company)
                        elif "linkedin.com" in url: success = apply_linkedin(page, url, job_title, company)
                        elif "naukri.com" in url: success = apply_naukri(page, url, job_title, company)
                        elif "wellfound.com" in url or "angel.co" in url: success = apply_wellfound(page, url, job_title, company)
                        elif "internshala.com" in url: success = apply_internshala(page, url, job_title, company)
                        elif "hirist.com" in url or "hirist.tech" in url: success = apply_hirist(page, url, job_title, company)
                        else: 
                            success = apply_generic_portal(page, url, job_title, company)
                        
                        if success:
                            sheet.update_cell(i, applied_col_index, "TRUE") 
                            print(f"  -> 📝 Successfully updated Google Sheet (Row {i}) to 'TRUE'!")
                            
                        page.wait_for_timeout(1500)
                        
            except Exception as e:
                print(f"  ❌ Error processing tab {tab_name}: {e}")

        print("\n🎉 Finished checking all pending jobs across all tabs.")
        context.close()

if __name__ == "__main__":
    main()