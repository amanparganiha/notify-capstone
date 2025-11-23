#!/usr/bin/env python3
import json
import argparse
import os
from agentpack import coordinator, tools

def load_config(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="examples/demo_config.json", help="Path to config json")
    args = p.parse_args()
    config = load_config(args.config)
    # Create tools module-like object for simple DI
    tools_module = type("T", (), {"scrape_site": tools.scrape_site, "email_template": tools.email_template})
    ranked = coordinator.run_sync(config, tools_module)
    print("\nDone. Top results:")
    for r in ranked[:5]:
        print(f"- {r.get('title')} @ {r.get('company')} (score: {r.get('_score')})")
    print(f"\nOutputs written to: {os.path.join(config.get('output_dir','outputs'), config.get('project_name','notify_demo'))}")

if __name__ == "__main__":
    main()
