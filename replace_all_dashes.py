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
        # to avoid partial matches, though our targets are pretty specific.
        pattern = r'\b' + re.escape(target) + r'\b'
        underscored = target.replace('-', '_')
        new_content = re.sub(pattern, underscored, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('training'):
    for file in files:
        if file.endswith('.md') or file.endswith('.py') or file.endswith('.yaml') or file.endswith('.txt'):
            replace_in_file(os.path.join(root, file))

