# test_remotive.py
import asyncio
from agentpack.tools import fetch_remotive_jobs

cfg = {
    "remotive_category": "software-dev",   # optional
    "remotive_search": "intern",          # optional
    "remotive_timeout": 20,
    "user_agent": "NotifyBot/1.0 (+https://example.com)"
}

async def main():
    results = await fetch_remotive_jobs(cfg, max_jobs=20)
    print("Got", len(results), "results")
    for i, r in enumerate(results[:5], 1):
        print(i, "-", r.get("title"), "@", r.get("company"), "intern?", r.get("_is_intern"))

if __name__ == "__main__":
    asyncio.run(main())
