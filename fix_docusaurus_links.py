import os
import re

# 2. Fix the link resolving issue `Can't resolve './module21.5-custom-agents'`
# Docusaurus complains about links that don't match the Docusaurus URL structure.
# In README.md we wrote `./training/module21.5-custom-agents/` but Docusaurus might want `./module21.5-custom-agents/`
# because README.md is copied to training/README.md during the build step!
# Wait, look at the action:
# `cp README.md timetable-*.md variant-*.md CONTRIBUTING.md training/`
# `sed -i 's|(./training/|(./|g' training/*.md`
# The sed command should have fixed it: `(./training/` -> `(./`.
# Let's check `README.md` again.
with open('README.md', 'r') as f:
    readme_content = f.read()

# Let's see if we added a trailing slash or something weird.
print("Link to 21.5 in README:", re.search(r'module21\.5.*', readme_content).group(0))

# Docusaurus doesn't like paths to directories without an explicit index.md or README.md inside them
# OR it doesn't like dots in directory names for some routing reasons.
# Wait, the error is: `Module not found: Error: Can't resolve './module21.5-custom-agents' in '.../training'`
# But `module21.5-custom-agents/README.md` exists!
