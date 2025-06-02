# **🧭 Contribution Guidelines**

This document outlines the standards and processes all contributors must follow while contributing to the project. These rules ensure code quality, consistency, and maintainability.

-----

# **Who Can Contribute?** Everyone is welcome to contribute to SpotAxis, including but not limited to:

* **End users** who discover bugs or have ideas for new features

* **Developers** who want to improve code quality, add modules, or refactor existing functionality 

* **Testers and QA engineers** who can reproduce issues, write tests, and improve reliability

* **Technical writers and designers** who can enhance documentation, examples, or UI/UX guidance

* **Community maintainers** who triage issues, review pull requests, and welcome newcomers 

No prior experience with Git or Applicant Tracking Systems is required—your enthusiasm and fresh perspectives are highly valued.

---

# **How to contribute** 

## **1\. Repository Setup**

* Fork the main repository.

* Always work on a new branch created from the latest `develop`.

* Do **not** push directly to `main/master` or `develop`.

* Keep your fork updated with upstream changes using rebase.

---

## **2\. Branch Naming Convention**

Use this format to name your branches, which also helps GitHub auto-link to issues:

**Format:**  
 `<issue-number>-<type>-<short-description>`

**Examples:**

* `42-feat-user-login`

* `105-fix-email-validation`

* `210-chore-cleanup`

This helps with traceability and GitHub issue linking. **\[IMPORTANT\]**

---

## **3\. Code Standards**

All code formatting and linting are enforced using pre-commit hooks. Interns are **not required to memorize formatting rules**, but must ensure:

* Code passes `pre-commit` checks.

* Code is readable and modular.

* Functions and variables have meaningful names.

You will receive errors if your code doesn't meet formatting/linting rules during commit or CI.

---

## **4\. Pull Request Process**

**One PR \= One Feature or Bugfix**

* Make a small and focused PR tied to a single issue.

* Use small, logical commits to maintain traceability.

* Rebase your branch with the latest `main` before raising a PR (no merge commits).

* Link your PR to the relevant issue using keywords like `Closes #42`.

**PR Title Format:**  
 `[type] Short description (#issue_number)`

**Examples:**

* `[feat] Add JWT authentication (#42)`

* `[fix] Resolve email validator crash (#105)`

**PR Description Template:**

markdown  
CopyEdit  
`## What`  
`Short summary of changes`

`## Why`  
`Context or problem being solved`

`## Related`  
`Closes #<issue-number>`

`## Checklist`  
`- [ ] Pre-commit checks passed`  
`` - [ ] Rebased with `main` ``  
`- [ ] Commits are logically split`

---

## **5\. Commit Message Standards**

Follow the Conventional Commit format:

**Format:**  
 `<type>(optional-scope): short message`

**Examples:**

* `feat(auth): add Google login flow`

* `fix(forms): handle null email edge case`

* `chore: remove unused constants`

**Types include:**

* `feat` — for new features

* `fix` — for bugfixes

* `chore` — for cleanup tasks

* `docs` — for documentation changes

* `refactor` — code restructure without functional changes

* `test` — for testing additions/changes

Avoid vague commits like "fix bug", "update code", or "final".

---

## **6\. Code Review Process**

* All PRs must be reviewed before merging.

* Reviewers may request changes; address all comments.

* Granular commits make reviewing easier and help with rollback/debugging.

* Avoid force-pushing after a PR is raised unless rebasing.

---

## **7\. Testing Standards**

* All features must include test cases (if testable).

* Use `pytest` and follow the naming convention: `test_<module>.py`.

* For untestable changes (e.g., styling), mention that clearly in the PR.

---

## **8\. Best Practices**

* Write small, readable functions.

* Use clear variable and function names.

* Don’t submit unrelated changes in a single PR.

* Avoid premature optimization or over-abstraction.

* Raise blockers/questions early — don’t stay stuck.

---

## **9\. Tooling Setup (Python Only)**

Pre-commit hooks ensure all linting and formatting is applied before code reaches the repo. Interns must:

### **Install Pre-commit (once)**

bash  
CopyEdit  
`pip install pre-commit`  
`pre-commit install`

### **Run checks manually (optional)**

bash  
CopyEdit  
`pre-commit run --all-files`

These hooks are enforced both locally and via GitHub Actions, so skipping them is not possible.

---

## **10\. GitHub Actions**

All pull requests will trigger GitHub Actions to verify:

* Code formatting (`black`)

* Linting (`flake8`, `isort`)

* Pre-commit compliance

* (Optional) Test suite execution

* Rebase status (optional enforcement)

If your PR fails any of these checks, it **cannot be merged** until fixed.

---

## **✅ Final Checklist Before Raising a PR**

| Task | Status |
| ----- | :---- |
| Feature branch created from `develop` | ✅ |
| Branch name includes issue number | ✅ |
| `pre-commit` installed and passing | ✅ |
| Branch rebased with latest `develop` | ✅ |
| PR linked to GitHub issue | ✅ |
| Small commits for better traceability | ✅ |
| All reviewer comments addressed | ✅ |

---

## **📌 Summary**

* Use proper branch and commit naming.

* Keep PRs atomic and linked to issues.

* Use pre-commit and rebase before PR.

* Code should be self-explanatory.

* Ask for help if stuck — early and often.

---

# **Bug & Feature Request Guidelines**

#   Before filing or reviewing a request:

* Confirm you’re on the latest SpotAxis release

* Search existing issues to avoid duplicates

* Fill out all required fields in GitHub’s issue form for clarity and context

* We’ll label issues as “bug,” “enhancement,” or “documentation,” and may ask for additional details (environment, reproduction steps)

---

# **Reporting Security Issues**

#   For security vulnerabilities, please **do not** open a public issue.

---

# **Community & Support**

#   Join our Discord community for real-time chat, questions, and camaraderie:  **Discord:** https://discord.gg/AVAMpXsA 
