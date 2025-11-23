"""
Coordinator: orchestrates sub-agents.
"""
import asyncio
from .search_agent import SearchAgent
from .matcher_agent import MatcherAgent
from .notifier_agent import NotifierAgent
from .memory import InMemorySession

class Coordinator:
    def __init__(self, config, tools):
        self.config = config
        self.tools = tools
        self.session = InMemorySession(config.get("session_id", "default"))
        self.search_agent = SearchAgent(config, tools, self.session)
        self.matcher_agent = MatcherAgent(config, tools, self.session)
        self.notifier = NotifierAgent(config, tools, self.session)

    async def run_pipeline(self):
        print("[Coordinator] starting search phase")
        try:
            search_results = await self.search_agent.search_all_sources()
        except Exception as e:
            print("[Coordinator] search phase error:", e)
            search_results = []
        print(f"[Coordinator] raw postings found: {len(search_results)}")

        normalized = self.matcher_agent.normalize_and_dedupe(search_results)
        print(f"[Coordinator] postings after dedupe: {len(normalized)}")

        ranked = self.matcher_agent.score_and_rank(normalized)
        print(f"[Coordinator] postings after scoring: {len(ranked)}")

        # --- FILTER: keep only postings flagged as internships if config requests it
        if self.config.get("intern_only", False):
            filtered = [p for p in ranked if p.get("_is_intern", False)]
            print(f"[Coordinator] filtered to intern-only postings: {len(filtered)}")
            ranked = filtered

        # persist results in session and notify top-k from the (possibly filtered) ranked list
        self.session.write("last_run_results", ranked)
        await self.notifier.notify_top_matches(ranked[: self.config.get("top_k", 5)])

        return ranked

# Sync helper for CLI
def run_sync(config, tools):
    coord = Coordinator(config, tools)
    return asyncio.run(coord.run_pipeline())
