import os
import re

targets = [
    "visual-catalog", "chuck-norris-agent", "research-assistant",
    "fact-finder-agent", "greeting-agent", "blog-pipeline", "travel-planner",
    "content-publisher", "essay-refiner", "a2a-orchestrator", "research-specialist",
    "personal-tutor", "doc-processor", "observability-agent", "content-moderator",
    "custom-mcp-server", "ui-agent", "custom-streaming-app", "customer-support-cloud",
    "gke-echo-agent", "cloud-mcp-server", "deploy-manual", "capstone-shopping-system",
    "web-agent", "personalization-agent", "orchestrator-agent", "best-practices-agent",
    "retry-agent", "skills-agent", "greeting-skill", "echo-agent", "shopping-agent",
    "calculator-agent", "finance-assistant", "support-router", "multi-model-agent",
    "haiku-poet-agent", "haiku-analyzer-agent", "mcp-agent", "cloud-shopping-agent",
    "multi-tool-agent", "memory-agent", "streaming-agent"
]

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    for target in targets:
        # Match target word, but not if preceded by or followed by a hyphen
        # Also skip if it's inside a URL path like /doc-adk-training/module37-.../lab-solution
        # A simple way: look for the word, but skip if it's right after `module\d+-` or inside `href=`
        
        # Let's just do a manual replacement ensuring we don't break doc links
        # Actually, the Docusaurus URLs in this repo are specifically like `/doc-adk-training/module...`
        # None of the targets are exactly the module names. But wait, `capstone-shopping-system` was broken in my previous script?
        # Oh, in module37, the URL is `/doc-adk-training/module37-advanced-personalized-shopping-agent/lab-solution`.
        # `shopping-agent` is part of `module37-advanced-personalized-shopping-agent`!
        
        pattern = r'(?<!-)(?<!/module\d{2}-)(?<!/module\d{2}\.\d-)(?<!module\d{2}-advanced-personalized-)\b' + re.escape(target) + r'\b(?!-)'
        underscored = target.replace('-', '_')
        new_content = re.sub(pattern, underscored, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

replace_in_file('training/module37-advanced-personalized-shopping-agent/lab.md')

