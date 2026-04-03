import re

# 1. Fix the MDX parsing error in module37 lab.md
filepath = 'training/module37-advanced-personalized-shopping-agent/lab.md'
with open(filepath, 'r') as f:
    content = f.read()

# The issue is that the injected code is outside the indentation block of the code snippet!
# ```python
#     from google.adk.agents import Agent
#     from google.adk.a2a.utils.agent_to_a2a import to_a2a
# from dotenv import load_dotenv
# load_dotenv()

# We need to properly indent the dotenv load_dotenv calls or put them in the right place.
# Actually, the error `Could not parse expression with acorn` in MDX often happens when you have unescaped `{}` 
# inside JSX or unindented code inside a markdown list item. 
# Here the code block is indented inside a list item.
# Let's fix the indentation of the injected lines.

content = content.replace('from dotenv import load_dotenv\nload_dotenv()', '    from dotenv import load_dotenv\n    load_dotenv()')

with open(filepath, 'w') as f:
    f.write(content)
print(f"Fixed indentation in {filepath}")

