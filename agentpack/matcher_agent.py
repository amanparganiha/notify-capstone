# agentpack/matcher_agent.py
"""
MatcherAgent: cleans, extracts features, scores and ranks internships.
Contains two methods:
 - normalize_and_dedupe(postings)
 - score_and_rank(postings)
"""
from typing import List
import re

class MatcherAgent:
    def __init__(self, config, tools, session):
        self.config = config
        self.tools = tools
        self.session = session
        self.keywords = config.get("keywords", [])

    def normalize_and_dedupe(self, postings: List[dict]) -> List[dict]:
        """
        Normalize fields and remove duplicates based on url or title+company
        """
        seen = set()
        out = []
        for p in postings:
            uid = p.get("url") or (p.get("title","") + p.get("company",""))
            if uid in seen:
                continue
            seen.add(uid)
            # Ensure fields exist and are strings
            p["title"] = (p.get("title","") or "").strip()
            p["company"] = (p.get("company","") or "").strip()
            p["description"] = (p.get("description","") or "").strip()
            out.append(p)
        return out

    def score_and_rank(self, postings: List[dict]) -> List[dict]:
        """
        Improved scoring:
        - Strong boost if posting is internship-like (posting['_is_intern'] True)
        - Penalize senior / full-time / management roles
        - Keep keyword boosts for user keywords
        - Keep small preferences for remote/stipend
        """
        senior_pattern = re.compile(r"\b(senior|lead|staff|principal|manager|director|head|sr\.?)\b", re.I)
        junior_pattern = re.compile(r"\b(intern|internship|junior|fresher|graduate|trainee)\b", re.I)

        def score(p):
            s = 0
            title = (p.get("title","") or "").lower()
            desc = (p.get("description","") or "").lower()
            text = title + " " + desc

            # Strong internship preference
            if p.get("_is_intern", False):
                s += 50

            # Keyword relevance (user-provided)
            for kw in self.keywords:
                if kw and kw.lower() in text:
                    s += 10

            # Remote / stipend small bonuses
            if "remote" in text:
                s += 4
            if "stipend" in text or "paid" in text:
                s += 3

            # Penalize senior/full-time signals
            if senior_pattern.search(text):
                s -= 20
            if "full-time" in text or "full time" in text:
                s -= 10

            # Small boost for explicit junior/intern hints
            if junior_pattern.search(text):
                s += 8

            # fallback: length / presence check to avoid empty postings
            if len(text.strip()) < 10:
                s -= 5

            return s

        for p in postings:
            p["_score"] = score(p)

        # sort descending by score, tie-breaker: prefer _is_intern True
        return sorted(postings, key=lambda x: (-x.get("_score", 0), not bool(x.get("_is_intern", False))))
