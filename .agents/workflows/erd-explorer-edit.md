---
description: 
---

> **Task:** Expand the Interactive ERD Visualization.
> **Objective:** Read the Theory of Operations documentation to find doctypes related to `[Insert Topic, e.g., Parts Harvesting]`, and update the visualization to reflect these connections.
> 
> **Workflow Steps:**
> 1. **Context:** Search `d:\induct-TOO\theory_of_operations\*.md` for mentions of `[Insert Topic]` to extract relevant doctypes, their fields, and their relational dependencies.
> 2. **Review Schema:** View `d:\induct-TOO\src\erd_visualization\data_schema.js` to understand the existing `DATA_SCHEMA`. 
> 3. **Format:** Create the new doctypes using the standard structure: `{ id: '...', name: '...', category: '...', fields: ['...'] }`. *Note: Do not define a `level` property; the visualization engine uses an automated Reverse Topological Sorting algorithm for layout.*
> 4. **Connections:** Create the relational connections in `DATA_SCHEMA.connections` using `{ from: '...', to: '...', type: 'relation', workflow: '...' }` (or `type: 'workflow'` for primary flow edges).
>     * **Rule A (DAG Enforcement):** Connections must flow consistently in a logical direction (e.g., `Appointment -> WorkOrder` across all workflows) to prevent circular dependencies. Cycles will break the Topological Sort layout engine.
>     * **Rule B (Cross-Workflow Isolation):** If linking to a core node from another workflow (e.g., linking a Harvesting WorkOrder to an ARMS Appointment), tag the single relation edge with the current workflow parameter (`workflow: 'harvesting'`). This elegantly pulls in the cross-workflow node without cluttering the visualization with its entire original tree.
> 5. **UI & Formatting:** If a new workflow is an acronym (e.g., `arms`), ensure you update the label formatting logic and edge color assignments in `app.js` so it renders in fully capitalized form (e.g., "ARMS") with a distinct color profile.
> 6. **Update:** Use file editing tools (e.g., `multi_replace_file_content`) to surgically inject the new doctypes and connections into `data_schema.js`.
> 7. **Verify:** Conclude your turn and instruct the user to refresh the browser.