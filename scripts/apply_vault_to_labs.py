#!/usr/bin/env python3
"""
Applies SolutionVault component to all lab.md files across all 45 training modules,
embedding the reference solution content directly from lab-solution.md.
"""

import os
import glob
import re

def apply_solution_vault():
    modules = sorted(glob.glob('training/module*'))
    print(f"Discovered {len(modules)} training modules.")
    
    updated_count = 0
    skipped_count = 0

    for m in modules:
        mod_name = os.path.basename(m)
        lab_path = os.path.join(m, 'lab.md')
        sol_path = os.path.join(m, 'lab-solution.md')

        if not os.path.exists(lab_path) or not os.path.exists(sol_path):
            print(f"[-] Skipping {mod_name}: lab.md or lab-solution.md missing.")
            skipped_count += 1
            continue

        match = re.match(r'module(\d+(_\d+)?)-', mod_name)
        if not match:
            print(f"[-] Could not parse module key from {mod_name}")
            skipped_count += 1
            continue
        mod_key = match.group(1)

        lab_content = open(lab_path, 'r', encoding='utf-8').read()
        sol_content = open(sol_path, 'r', encoding='utf-8').read()

        # Strip frontmatter from solution
        sol_body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', sol_content, flags=re.DOTALL).strip()

        # Format vault block
        vault_block = f"""<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="{mod_key}">

{sol_body}

</SolutionVault>
"""

        # Check if legacy pattern exists in lab.md
        pattern = r'(<hr/?>\s*###\s*🕵️.*|###\s*🕵️\s*Hidden Solution.*)'
        m_match = re.search(pattern, lab_content, re.DOTALL)
        if m_match:
            new_lab_content = lab_content[:m_match.start()].rstrip() + "\n\n" + vault_block
            with open(lab_path, 'w', encoding='utf-8') as f:
                f.write(new_lab_content)
            print(f"[+] Updated {mod_name} with <SolutionVault moduleNumber=\"{mod_key}\">")
            updated_count += 1
        elif '<SolutionVault' in lab_content:
            print(f"[=] {mod_name} already has SolutionVault.")
            skipped_count += 1
        else:
            # If no legacy pattern, append vault at the bottom
            new_lab_content = lab_content.rstrip() + "\n\n" + vault_block
            with open(lab_path, 'w', encoding='utf-8') as f:
                f.write(new_lab_content)
            print(f"[+] Appended <SolutionVault moduleNumber=\"{mod_key}\"> to {mod_name}")
            updated_count += 1

    print(f"\nDone! Updated: {updated_count}, Skipped/Existing: {skipped_count}")

if __name__ == '__main__':
    apply_solution_vault()
