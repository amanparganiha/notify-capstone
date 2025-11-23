Notify — Internship Automation Agent

Automated multi-agent system that discovers internships from legal sources, ranks them intelligently, and drafts ready-to-send emails — all with one command.

This project is my submission for the Google AI Agents Intensive — Capstone Project.

⭐ 1. Overview

Finding internships is slow and repetitive. You open multiple job boards, read descriptions, check duplicates, filter by relevance, and then manually write emails.

Notify automates all of this.

It is a multi-agent pipeline built with Python that:

Fetches internship listings from legal sources

Cleans and deduplicates them

Scores + ranks them using a hybrid scoring engine

Drafts personalized email templates

Stores session state + previous results

Outputs JSON + email drafts in a clean structured format

🚀 2. Features
Multi-Agent System

Coordinator Agent – Orchestrates tasks

Search Agent – Fetches data from Remotive (legal public API)

Matcher Agent – Normalizes, dedupes, scores postings

Notifier Agent – Generates email drafts + structured output

Technical Components

Parallel & sequential agents

Custom tools

Safe API-based sourcing

Memory (InMemorySession + MemoryBank)

Config-driven operation

Ready for ADK/Gemini LLM scoring

Outputs

ranked_internships.json

Email drafts in /outputs/<project>/emails/

🧠 3. Architecture
                  ┌────────────────────┐
                  │    User Config     │
                  └─────────┬──────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Coordinator   │
                    └──────┬────────┘
   ┌───────────────────────┼────────────────────────┐
   ▼                       ▼                        ▼
SearchAgent        MatcherAgent           NotifierAgent
(fetch data)     (score + rank)         (draft emails)
   │                       │                        │
   └───────────────────────┴────────────────────────┘
                            ▼
                     Output Directory

⚙️ 4. Installation
Clone
git clone https://github.com/yourusername/notify-capstone
cd notify-capstone

Create environment
python -m venv .venv


Activate:

Windows:

.venv\Scripts\activate


Mac/Linux:

source .venv/bin/activate

Install dependencies
pip install -r requirements.txt

🎛️ 5. Configuration

Edit examples/demo_config.json

{
  "project_name": "notify_demo",
  "session_id": "demo1",
  "sources": ["remotive"],
  "keywords": ["machine learning", "intern"],
  "top_k": 10,
  "output_dir": "outputs",
  "remotive_category": "software-dev",
  "remotive_search": "intern",
  "max_jobs_per_source": 100,
  "intern_only": true
}

▶️ 6. Run Notify
python run_notify.py --config examples/demo_config.json


Expected output:

[Coordinator] starting search phase
[SearchAgent] searching remotive
[Remotive] fetched 100 jobs (intern-prefiltered)
[Coordinator] filtered to intern-only postings: 6
[Notifier] wrote 6 drafts to outputs\notify_demo

Outputs generated:
/outputs/notify_demo/
    ranked_internships.json
    /emails/
        1_<company>.txt
        ...

🛠️ 7. How It Works
SearchAgent

Fetches jobs using Remotive API (legal & public)

Extracts title, company, description, URL

Computes _is_intern boolean using NLP pattern matching

MatcherAgent

Normalization

Deduplication

Hybrid scoring with:

Internship check

Keyword match

Remote/stipend bonuses

Senior-role penalties

Sorted ranked list returned

NotifierAgent

Creates clean email drafts:

personalized

editable

plain-text

Saves JSON + emails to output folder

Memory

InMemorySession stores run state

Ready for long-term memory via SQLite (MemoryBank)

🔍 8. LLM Scoring (Optional)

Enable richer agent evaluation by setting:

export OPENAI_API_KEY="..."


or Gemini/ADK environment.

🖥️ 9. Demo Notebook

A runnable notebook is provided at:

notebooks/demo_run.ipynb

It:

Loads config

Calls pipeline

Displays ranked table + drafts

🌐 10. Deployment (Optional)

This repo includes instructions to deploy on:

Vertex AI Agent Engine

Cloud Run

Docker

(See docs/deploy.md)

📁 11. Project Structure
notify-capstone/
│── agentpack/
│    ├── coordinator.py
│    ├── search_agent.py
│    ├── matcher_agent.py
│    ├── notifier_agent.py
│    ├── tools.py
│    ├── memory.py
│── examples/
│    └── demo_config.json
│── outputs/
│── run_notify.py
│── README.md
│── requirements.txt
│── notebooks/
│── docs/

🙌 12. Credits

Built as part of the Google AI Agents Intensive (Nov 2025).
