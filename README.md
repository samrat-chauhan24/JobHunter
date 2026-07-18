# JobHunter

An AI-powered job automation platform that searches jobs from multiple platforms, ranks them against a resume using LLMs, and automatically applies to the most relevant opportunities.

## Features

- 🔍 Multi-platform job search
  - Wellfound
  - Naukri
  - Hirist
  - Internshala

- 🤖 AI-powered resume matching using Groq LLMs

- 📄 Automatic resume parsing

- 📊 ATS score generation for every job

- 🧹 Job normalization, duplicate removal, and 24-hour freshness filtering

- 📑 Google Sheets-based job database and candidate queues

- 🚀 Automated job application using Playwright

- ⏰ Scheduled workflows using n8n

## Tech Stack

- **Automation:** n8n
- **Backend:** FastAPI, Python
- **Browser Automation:** Playwright
- **AI:** Groq (Llama 3.3, GPT-OSS)
- **Database:** Google Sheets
- **Resume Parsing:** PDF Extractor

## Project Structure

```
JobHunter/
├── auto-applier/
├── macOS_Launcher/
├── n8n_workflows/
└── search-scripts/
```

## Workflow

```
Search Jobs
      ↓
Normalize Jobs
      ↓
Store Database
      ↓
Rank Using Resume
      ↓
Shortlist Jobs
      ↓
Auto Apply
```

## Setup

```bash
git clone <repository-url>
cd JobHunter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install
```

Import the workflows into **n8n**, configure your credentials, start the FastAPI service, and run the launcher.

## Authors

- **Samrat Chauhan**
- **Ronak Malik**