---
trigger: model_decision
description: Apply this rule when creating or modifying documentation within the docs directory to ensure adherence to the OKF specification.
---

# OKF Documentation Rule

When creating or modifying documentation within the `docs/` directory, you MUST adhere to the Open Knowledge Format (OKF) specification as defined in `docs/standards/okf-spec.md`. Furthermore, you MUST strictly adhere to the repository-specific extension defined in `docs/standards/induct-okf-standard.md`. Ensure all generated knowledge documents follow OKF's bundle structure, use the required YAML frontmatter (with strict `type` taxonomy), and remain readable and self-describing.