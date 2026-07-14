# Migration Plan: Single Branch to Two-Branch System (main/solution)

This document outlines the safe, step-by-step plan to migrate this repository from a single branch to a two-branch system (`main` and `solution`) without losing any history.

### The Strategy

We will rename the current branch to `solution` (since it already has all the files), and then create a new `main` branch from it, from which we will remove the solution files. This ensures a clean, spoiler-free experience for students who fork the repository.

---

### The Migration Plan

**Phase 1: Preparation and Safety (Local)**

1.  **Create a Backup Branch:** This is the most important step. We'll create a backup of the current branch exactly as it is. If anything goes wrong, we can restore everything from this backup.
    *   **Command:** `git branch backup-pre-migration`

**Phase 2: Restructure Branches (Local)**

2.  **Rename Your Current Branch to `solution`:** The current branch already contains all the files, which is exactly what the `solution` branch needs. We'll simply rename it.
    *   **Command:** `git branch -m adk-training-hub solution`

3.  **Create the `main` Branch:** We'll create the new `main` branch. It will start as an identical copy of the `solution` branch.
    *   **Command:** `git checkout -b main`

**Phase 3: Separate the Content (Local)**

4.  **Remove Solution Files from `main`:** Now, on the `main` branch, we will find and remove all `lab-solution.md` files from the repository's tracking. They will remain safe on the `solution` branch.
    *   **Command:** `find . -name "lab-solution.md" -print0 | xargs -0 git rm`

5.  **Commit the Removal:** We will commit this change to finalize the `main` branch.
    *   **Command:** `git commit -m "feat: Remove solution files for student branch"`

**Phase 4: Deploy to Remote (GitHub)**

6.  **Push the New Branches:** We will push both of the new, clean branches to the GitHub repository.
    *   **Commands:** `git push -u origin main` and `git push -u origin solution`

7.  **Delete the Old Remote Branch:** To avoid confusion, we will delete the old `adk-training-hub` branch from GitHub.
    *   **Command:** `git push origin --delete adk-training-hub`

**Phase 5: Final Configuration (Manual Step for You on GitHub)**

8.  **Set the Default Branch on GitHub:** This is a crucial step you must perform manually in the GitHub UI after the migration is complete.
    *   Go to your repository settings on GitHub.
    *   Navigate to the "Branches" section.
    *   Change the **default branch** from whatever it is now to `main`. This ensures that when students fork your repo, they get the version without solutions by default.
