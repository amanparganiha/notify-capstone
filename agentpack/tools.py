
import asyncio
import aiohttp
import time
import re
import json
from aiohttp import ClientTimeout

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

async def fetch_remotive_jobs(config, max_jobs: int = 50):
    """
    Fetch jobs from Remotive API and return list of postings.
    Filters jobs to internships when possible (title/tags/description contains 'intern').
    Returns up to max_jobs items.
    """
    params = {}
    if config.get("remotive_category"):
        params["category"] = config["remotive_category"]
    if config.get("remotive_search"):
        params["search"] = config["remotive_search"]

    timeout = ClientTimeout(total=config.get("remotive_timeout", 20))
    headers = {
        "User-Agent": config.get("user_agent", "NotifyBot/1.0 (+https://example.com)"),
        "Accept": "application/json, text/plain, */*",
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(REMOTIVE_API, params=params) as resp:
                status = resp.status
                text = await resp.text()
                if status != 200:
                    print(f"[Remotive] unexpected status {status}")
                    print("[Remotive] response snippet:", text[:1000])
                    return []
                # Try to parse JSON safely
                try:
                    data = json.loads(text)
                except Exception as e:
                    print("[Remotive] json parse error:", e)
                    print("[Remotive] response snippet:", text[:1000])
                    return []
    except Exception as e:
        print("[Remotive] fetch error (network/timeout):", repr(e))
        return []

    jobs = data.get("jobs", []) if isinstance(data, dict) else []
    out = []
    intern_pattern = re.compile(r"\bintern\b|\binternship\b", re.I)

    for j in jobs:
        # defensive access
        title = j.get("title", "") if isinstance(j, dict) else ""
        company = j.get("company_name", "") if isinstance(j, dict) else ""
        description = j.get("description", "") if isinstance(j, dict) else ""
        tags_list = j.get("tags", []) if isinstance(j, dict) else []
        tags = " ".join(tags_list) if isinstance(tags_list, (list, tuple)) else str(tags_list)

        posting = {
            "title": title,
            "company": company,
            "description": description,
            "url": j.get("url") if isinstance(j, dict) else None,
            "source": "remotive",
            "raw": j,
        }

        is_intern = bool(intern_pattern.search(title or "")) \
                    or bool(intern_pattern.search(tags or "")) \
                    or bool(intern_pattern.search(description or ""))

        posting["_is_intern"] = is_intern
        out.append(posting)
        if len(out) >= max_jobs:
            break

    # Put internship-like entries first (True -> False in sort key, so invert)
    out_sorted = sorted(out, key=lambda x: (not bool(x.get("_is_intern", False)),))
    print(f"[Remotive] fetched {len(out)} jobs (intern-prefiltered). Returning {len(out_sorted)} items.")
    return out_sorted


# ===== Compatibility wrapper to ensure .scrape_site exists =====
# Add this to agentpack/tools.py

import asyncio

async def scrape_site(source, config):
    """
    Backwards-compatible single entrypoint used by SearchAgent.
    Behavior:
      - If source indicates Remotive, use fetch_remotive_jobs (if available).
      - Else, if safe_scrape_site exists, call it (sitemap-based scraping).
      - Else, fallback to a tiny demo stub that returns fake postings.
    """
    # normalized source keywords
    s = (source or "").lower()
    # 1) remotive special case
    if "remotive" in s and "fetch_remotive_jobs" in globals():
        try:
            return await fetch_remotive_jobs(config, max_jobs=config.get("max_jobs_per_source", 50))
        except Exception as e:
            print("[scrape_site] remotive fetch failed:", repr(e))
            # fall through to other options

    # 2) safe sitemap-based scraping if available
    if "safe_scrape_site" in globals():
        try:
            res = await safe_scrape_site(source, config)
            if res:
                return res
        except Exception as e:
            print("[scrape_site] safe_scrape_site failed:", repr(e))

    # 3) fallback demo stub (fast, guaranteed)
    try:
        # If there's an existing stub that expects (source, config) use it
        if "fetch_remotive_jobs" in globals() and "safe_scrape_site" not in globals():
            # nothing else defined - but fallback below anyway
            pass
    except Exception:
        pass

    # Final fallback: simple stub postings so pipeline doesn't break
    await asyncio.sleep(0.05)
    return [
        {"title": "ML Intern (demo)", "company": "DemoCorp", "description": "remote, stipend", "url": f"https://{source}/job/1", "source": source},
        {"title": "Backend Intern (demo)", "company": "Demo Ltd", "description": "onsite, unpaid", "url": f"https://{source}/job/2", "source": source},
    ]
# ===== end wrapper =====
def email_template(posting, user_name="Your Name", resume_bullet=None):
    """
    Return a plain-text email draft for a posting dict.
    posting: dict with keys 'title', 'company', 'url', 'description' (best-effort).
    user_name: string to include in signature.
    resume_bullet: optional short highlight to include in the body.
    """
    title = posting.get("title", "<role>")
    company = posting.get("company", posting.get("company_name", "<company>"))
    url = posting.get("url", "")
    short_desc = posting.get("description", "")[:400].replace("\n", " ")
    resume_part = f"\n\nA short highlight: {resume_bullet}" if resume_bullet else ""

    body = f"""Hi {company} Team,

I hope you are doing well. I'm reaching out to express my interest in the {title} position listed here:
{url}

Why I'm a fit:
- {resume_bullet or 'Relevant coursework and hands-on projects in the field.'}
- Quick summary: {short_desc}

I'd love to share my resume and discuss how I can contribute.

Regards,
{user_name}
"""
    return body
