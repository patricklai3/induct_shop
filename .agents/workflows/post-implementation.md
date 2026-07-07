---
description: Post-Implementation Documentation
---

Primary Directive: After implementing any new feature, modifying an existing feature, or completing a significant coding task, you must systematically document the changes in the project's documentation directory before concluding your task.

Workflow Steps:

1. Identify the Target Docs Directory
   - Locate the `docs` directory relevant to the application or workspace where the changes were made (e.g., `apps/induct_shop/docs/`).

2. Create or Update Documentation
   - Create a new markdown file for new features, or update existing documentation files for modifications.
   - The documentation should clearly explain:
     - The purpose of the feature and what it accomplishes.
     - How users or developers can utilize the new functionality.
     - Technical details such as newly created DocTypes, API changes, or workflow integrations.
     - Any required prerequisites or configurations.

3. Align with Established Standards
   - Review existing documentation in the `docs` directory.
   - Adhere strictly to any established documentation frameworks (e.g., Open Knowledge Format - OKF) and maintain consistent formatting, styling, and terminology.

4. Update Logs and Changelogs
   - If you modified application features or code, update the application changelog located at the app root (e.g., `apps/induct_shop/CHANGELOG.md`).
   - If you added or modified OKF documentation files, record this directory update in `docs/log.md` (e.g., `apps/induct_shop/docs/log.md`) categorized under the current date (in `YYYY-MM-DD` format).

5. Final Verification
   - Before completing your task and notifying the user, verify that all implemented features have corresponding and accurate documentation within the `docs` directory.
   - Ensure the appropriate changelog/log files have been updated based on your changes.

6. Clean up Temporary Files
   - Remove any temporary scripts, data files, or scratchpads created during the feature implementation to keep the workspace clean.