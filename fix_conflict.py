import re

def fix_conflict(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to keep the solution branch version (which is what we developed in dev/solution)
    # The format of a git conflict is:
    # <<<<<<< HEAD
    # (content in main)
    # =======
    # (content in solution)
    # >>>>>>> solution
    
    # We use a regex to match the conflict markers and keep ONLY the solution part.
    # Because we're merging `solution` into `main`, the `=======` to `>>>>>>> solution` is what we want.
    
    new_content = re.sub(r'<<<<<<< HEAD.*?=======\n(.*?)\n>>>>>>> solution', r'\1', content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed conflict in {filepath}")

fix_conflict('training/module03-first-agent-echo/lab.md')
fix_conflict('training/module04-llmagent-deep-dive/lab.md')
