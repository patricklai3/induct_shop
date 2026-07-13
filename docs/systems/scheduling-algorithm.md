---
layout: post
title: "Scheduling Algorithm Module"
category: "systems"
---

# Scheduling Algorithm Module

The Scheduling Algorithm module is a decoupled, pure Python module designed to handle complex computations for scheduling automotive repairs, minimizing variance between promised and actual pickup times, and managing shop capacity constraints.

## Architecture

To ensure rapid iteration and testability without tight coupling to the Frappe ORM, the scheduling logic is built around plain data models (e.g., Python `dataclasses`) rather than native Frappe `DocTypes`.

### Key Components

- **`models.py`**: Contains pure domain models (`Job`, `Technician`, `Station`) representing the entities involved in scheduling. This abstraction layer prevents Frappe dependencies from leaking into the core algorithm.
- **`core.py`**: Houses the `SchedulingAlgorithm` class, which serves as the main entry point for the scheduling logic (e.g., Monte Carlo simulations or constraint solvers). It accepts the pure domain models as input and returns a computed schedule layout.

## Location

The module is housed within the main application package:
`induct_shop/induct_shop/scheduling/`

## Integration Strategy

Integration with Frappe is intended to be managed externally to this core module. Data from Frappe `DocTypes` (such as `Work Order`, `Employee`, `Workstation`) should be parsed and mapped to the pure domain models (`models.py`) before being passed into the algorithm. The resulting schedule output must then be parsed back into Frappe records for persistence and UI rendering.
