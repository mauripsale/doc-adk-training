import os
import re

targets = [
    "blog-pipeline", "travel-planner", "content-publisher", "essay-refiner",
    "a2a-orchestrator", "research-specialist", "personal-tutor", "doc-processor",
    "observability-agent", "content-moderator", "custom-mcp-server", "ui-agent",
    "custom-streaming-app", "customer-support-cloud", "gke-echo-agent",
    "cloud-mcp-server", "deploy-manual", "capstone-shopping-system",
    "web-agent", "personalization-agent", "orchestrator-agent",
    "best-practices-agent", "retry-agent", "skills-agent", "greeting-skill",
    "echo-agent", "shopping-agent", "calculator-agent", "fact-finder-agent",
    "visual-catalog", "chuck-norris-agent", "research-assistant", "greeting-agent",
    "finance-assistant", "support-router", "multi-model-agent", "haiku-poet-agent",
    "haiku-analyzer-agent", "mcp-agent", "cloud-shopping-agent", "multi-tool-agent"
]

found = []
for root, _, files in os.walk('training'):
    for file in files:
        if file.endswith('.md') or file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                for t in targets:
                    if t in content:
                        found.append((path, t))

for p, t in found:
    print(f"{p}: {t}")
