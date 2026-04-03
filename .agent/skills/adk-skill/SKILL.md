---
name: adk-skill
description: Use this skill for developing agents using the Google Agent Development Kit (ADK) in Python. Provides guidelines, best practices, and documentation.
---
# Google Agent Development Kit (ADK) Skill

This skill provides up-to-date documentation and best practices for creating AI agents using the Google Agent Development Kit (ADK).

## ⚠️ Mandatory Startup Action

To ensure you are using the most current guidelines, you MUST update the ADK documentation every time you start working on an ADK-related task.

1. **Update the documentation:**
   Run the update script using the relative path:
   ```bash
   bash .agent/skills/adk-skill/scripts/update_docs.sh
   ```
2. **Read the updated documentation:**
   After the script completes, read the reference file at:
   `.agent/skills/adk-skill/references/adk-docs.txt`

## Resources

*   `scripts/update_docs.sh`: Downloads the latest `llms-full.txt` from the official ADK Python repository.
*   `references/adk-docs.txt`: The full ADK documentation. Consult this file for syntax, agent types, multi-agent systems, and model integrations.
