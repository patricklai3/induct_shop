---
description: Generate standardized implementation checklist from technical specification
---

# Generate Implementation Checklist from Spec

Primary Directive: Transform an approved technical specification document into a standardized, staged build-and-verify implementation checklist adhering to `induct_shop` repository conventions.

---

## Workflow Steps

### Phase 1: Input Validation & Context Review

1. **Verify Input Specification File**:
   - Ensure the input specification document (e.g. `docs/development/<name>-spec.md` or `docs/systems/<name>.md`) is fully drafted and approved.
   - Verify it contains valid OKF frontmatter (`type: Specification` or `type: System`).
   - Read and extract key sections: Executive Summary, Architecture/Domain Model, Data Schemas, Detailed Design, and Dependency/Integration points.

2. **Identify Target Checklist Location & File Name**:
   - Place active checklists in `docs/development/`.
   - Naming convention: `<feature>-checklist.md` (e.g., `testing-methodology-checklist.md`, `standalone-diagnostic-scheduling-checklist.md`).

---

### Phase 2: Stage Decomposition & Structuring

1. **Decompose Spec into Sequential Stages**:
   - Break down the implementation into logical, incremental stages ordered strictly by dependency (e.g., Schema/Database → Core Logic/APIs → Integrations → UI/Client Scripts → Tests & Verification → Documentation).
   - Each stage must represent a verifiable unit of work.

2. **Standard Stage Header Template**:
   Each stage MUST follow this exact structure:

   ```markdown
   ## Stage N: <Stage Title>

   **Goal**: <Concise 1-sentence statement of what this stage achieves>
   **Spec Reference**: <Section reference from spec, e.g. §3.1, §4>
   **Files**: `<path/to/file1>`, `<path/to/file2>`

   - [ ] **N.1 <Sub-item Title>**:
     - Sub-bullet detail with explicit instructions on what to change or create.
   - [ ] **N.2 <Sub-item Title>**:
     - Detail instructions...

   ### Stage N Acceptance Criteria
   - **Automated Testing Criteria**:
     - Exact test command, function call, or database query verification.
   - **Manual Review Criteria**:
     - Desk/UI verification steps (or `N/A — fully automated.`).
   ```

---

### Phase 3: Applying Standardized Refinements

Always incorporate these repository-specific refinements into the generated checklist:

1. **Mandatory Metadata Block (Frontmatter)**:
   Include valid OKF frontmatter at the top of the checklist:
   ```yaml
   ---
   type: Specification
   title: "<Feature Name> Implementation Checklist"
   description: "Staged development checklist tracking implementation, schema updates, automated tests, manual verification, and documentation."
   status: Active
   tags: [checklist, <feature-tag>, development, tracking]
   timestamp: <ISO-8601-Timestamp>
   references:
     - <relative-path-to-spec>
   ---
   ```

2. **Preamble Link**:
   Include a clear lead block referencing the spec document:
   ```markdown
   # <Feature Name> Implementation Checklist

   This checklist tracks the staged implementation of <feature description>, as specified in [<spec-filename>](./<spec-filename>).
   ```

3. **Stage-Level File & Spec Traceability**:
   - Every stage **MUST** explicitly state **Spec Reference** (§ section) and **Files** touched to ensure implementing agents have precise scope without re-scanning the entire spec.

4. **Explicit Acceptance Criteria Split**:
   - Always provide both `- **Automated Testing Criteria**:` and `- **Manual Review Criteria**:` for every stage.
   - If manual review is not applicable, explicitly write: `N/A — fully automated.`

5. **Dependency Map (Required for ≥ 4 Stages)**:
   - If the checklist has 4 or more stages, include a standard Mermaid dependency graph (`graph TD`) at the end of the document prior to any appendices.

6. **Deferred Stages Convention**:
   - If any stage specified in the architectural vision is explicitly deferred to a future phase (e.g. UI/dashboard phases):
     - Mark stage title with `[Deferred]`: `## Stage N — [Deferred] <Stage Title>`
     - Use `- [ ] *(Deferred)* <Task item>` for bullet points.
     - Include a `> [!NOTE]` callout linking to the stashed UI spec or tracking issue.

---

### Phase 4: Output Generation & Final Verification

1. **Write Checklist File**:
   - Write the complete markdown checklist to the target path (e.g. `docs/development/<feature>-checklist.md`).

2. **OKF Metadata Validation**:
   - Confirm YAML frontmatter has valid `type: Specification`, timestamp, status, and relative reference links.

3. **Update Index/Log**:
   - Record document creation in `docs/log.md` under the current date (`YYYY-MM-DD`).
