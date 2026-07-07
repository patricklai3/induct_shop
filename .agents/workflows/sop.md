---
description: Context-Aware SOP Generation (Integrated Operations)
---

Primary Directive: Before generating any process documentation, you must evaluate and confirm the current stage of the software or tool development. Your output must strictly align with the corresponding stage to ensure you are appropriately mapping the process, framing the draft, or finalizing the steps. Furthermore, you must actively scan the workspace for existing Theory of Operation documents to ensure all generated processes are grounded in the company's established operational framework.

Phase 1: Evaluation, Confirmation, and Contextual Review
Before initiating a draft, you must query the user or evaluate the provided context to categorize the project into one of three stages:


Stage 1 (Before Tech): Is the software completely unbuilt, requiring a definition of how the work should flow? 


Stage 2 (During Tech): Is the development team currently building interfaces and wireframes? 


Stage 3 (After Tech): Is the software interface locked in or currently in a stable beta version? 


Workspace Context Requirement: Regardless of the development stage, you must identify and ingest any Theory of Operation documents available in the workspace. These documents explain core company operations and must serve as the foundational logic for any SOP or process map you generate.

Modularity and Independent SOPs Requirement: When generating a process map or SOP, you must evaluate if a step in the workflow represents a distinct, reusable sub-process (e.g., scheduling an appointment for a quotation that requires an inspection). If it does, you must NOT document the granular steps of that sub-process within the current SOP. Instead, create a new, independent SOP file for that sub-process and link to it from the current document.

Phase 2: Stage-Specific Execution Guidelines
Once the stage is confirmed, execute the documentation based strictly on the following parameters:

If Stage 1: Before Development (Process Mapping)


Objective: You should not write an SOP; instead, you must design a Process Map or a Target Operating Model.


Focus: Define the "What" and "Why" to establish the desired workflow. Explicitly identify who needs to approve items, what data must be collected, and where the decision points exist. Ensure all identified workflows explicitly align with the principles outlined in the provided Theory of Operation documents.


Output: Format deliverables as flowcharts, business requirements, and high-level steps.


Constraint: Maintain the principle that the software should be built to support the process, not dictate it. No UI-specific instructions may be written at this stage.

If Stage 2: During Development (The Concurrent Draft)


Objective: Begin framing out the actual SOP document concurrently with the development team's work.


Focus: Build the foundational structure of the SOP, including the Purpose, Scope, and Prerequisites. Cross-reference the Purpose and Scope with the Theory of Operation documents to ensure organizational alignment.


Output: Draft the high-level steps, purposefully leaving placeholders for the specific clicks and interface interactions.


Constraint: Act as a feedback loop; if drafting the steps reveals a cumbersome workflow (e.g., a simple task taking 15 clicks), advise the user to provide feedback to the developers so the interface can be fixed before finalization.

If Stage 3: After Development (The Final SOP)


Objective: Finalize the document to specifically explain "How" to execute the flow in the new software.


Focus: Transition to writing highly specific, active-voice instructions (e.g., "Click the blue Submit button in the top right corner").


Output: Detail the exact buttons to click and ensure there are designated places to capture and annotate final screenshots for the document.