"""
SearchAgent: wrapper around scraping and API tools.
"""
import asyncio
import inspect
from typing import List, Any, Dict


class SearchAgent:
    def __init__(self, config: dict, tools: Any, session: Any):
        self.config = config or {}
        self.tools = tools
        self.session = session
        self.sources: List[str] = self.config.get("sources", ["example.com"])

    async def _maybe_call(self, fn, *args, **kwargs):
        """
        Call fn with args; await if it returns an awaitable, otherwise return directly.
        This makes the agent tolerant of sync or async tool implementations.
        """
        result = fn(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    async def _search_source(self, source: str) -> List[Dict]:
        print(f"[SearchAgent] searching {source}")
        try:
            s = (source or "").strip()
            if not s:
                return []

            # Support special source identifiers like "remotive"
            if s.lower() in ("remotive", "remotive.com", "remotive_api"):
                # tools.fetch_remotive_jobs expects (config, max_jobs) in your original comment
                if hasattr(self.tools, "fetch_remotive_jobs"):
                    max_jobs = self.config.get("max_jobs_per_source", 50)
                    postings = await self._maybe_call(self.tools.fetch_remotive_jobs, self.config, max_jobs)
                    return postings or []
                else:
                    print("[SearchAgent] tools has no fetch_remotive_jobs, falling back to scrape_site")

            # Next try safe_scrape_site if available (sitemap-based)
            if hasattr(self.tools, "safe_scrape_site"):
                postings = await self._maybe_call(self.tools.safe_scrape_site, s, self.config)
                if postings:
                    return postings
                else:
                    print(f"[SearchAgent] safe_scrape_site returned no postings for {s}, falling back to stub.")

            # Fallback to demo stub scrape_site
            if hasattr(self.tools, "scrape_site"):
                postings = await self._maybe_call(self.tools.scrape_site, s, self.config)
                return postings or []

            # nothing available
            return []
        except Exception as e:
            print(f"[SearchAgent] error searching {source}: {e}")
            return []

    async def search_all_sources(self) -> List[Dict]:
        """
        Search all configured sources concurrently and return a flattened list of postings.
        """
        tasks = [asyncio.create_task(self._search_source(s)) for s in self.sources]
        results = await asyncio.gather(*tasks)
        flat: List[Dict] = [p for r in results for p in (r or [])]
        return flat
