"""
NotifierAgent: drafts emails and writes outputs to disk.
"""
import os
import json

class NotifierAgent:
    def __init__(self, config, tools, session):
        self.config = config
        self.tools = tools
        self.session = session
        self.output_dir = config.get("output_dir", "outputs")

    async def notify_top_matches(self, matches):
        project = self.config.get("project_name", "notify_demo")
        path = os.path.join(self.output_dir, project)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "ranked_internships.json"), "w", encoding="utf8") as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)

        emails_dir = os.path.join(path, "emails")
        os.makedirs(emails_dir, exist_ok=True)
        for i, m in enumerate(matches):
            subj = f"Application: {m.get('title','')} at {m.get('company','')}"
            body = self.tools.email_template(m)
            fname = os.path.join(emails_dir, f"{i+1}_{m.get('company','').replace(' ','_')}.txt")
            with open(fname, "w", encoding="utf8") as ef:
                ef.write("Subject: " + subj + "\n\n")
                ef.write(body)
        print(f"[Notifier] wrote {len(matches)} drafts to {path}")
