---
type: Reference
title: "Scheduling Algorithm Module"
description: "Documentation for the Predictive-Reactive Bipartite Scheduling Algorithm, encompassing Bayesian estimation and CP-SAT optimization."
status: Implemented
tags: [system, scheduling, algorithm, python, optimization]
timestamp: 2026-07-14T19:15:00Z
---

# Scheduling Algorithm Module

The Scheduling Algorithm module is a decoupled, pure Python module designed to handle complex computations for scheduling automotive repairs, minimizing variance between promised and actual pickup times, and managing shop capacity constraints.

## Architecture: Predictive-Reactive Bipartite

The system employs a Predictive-Reactive Bipartite Architecture to decouple time estimation from resource allocation.

### 1. Bayesian Estimation Layer (`estimation.py`)
This layer handles the stochastic nature of automotive repair times using **Sequential Bayesian Linear Regression** with Normal-Inverse-Gamma conjugate priors.
- **Cold Start**: Initialized using standard flat-rate times (e.g. Mitchell 1 or Motor).
- **Continuous Learning**: Employs closed-form exact mathematical updates as jobs finish, learning from the duration without requiring batch neural network retraining.
- **Risk Adjustment**: Outputs the 80th percentile of the Posterior Predictive Distribution (a Student's t-distribution) to mathematically pad estimates and prevent cascading delays.

### 2. Optimization Layer (`solver.py`)
This layer handles the deterministic combinatorial allocation using **Google OR-Tools CP-SAT**.
- Solves over a rolling horizon (e.g., 24 hours).
- Formulates jobs and operations as `IntervalVar` and `OptionalIntervalVar`.
- Enforces constraints including Topological Precedence, Disjunctive Resource limits (NoOverlap for mechanics/bays), and specific equipment matching.
- **Work Order Contiguity Constraint**: Ensures that if multiple operations belonging to the same Work Order are assigned to the same service bay, they are scheduled strictly contiguously without interleaving other jobs, minimizing unnecessary vehicle movement.

## Core Domain Models (`models.py`)

To ensure rapid iteration and testability without tight coupling to the Frappe ORM, the scheduling logic is built around plain data models (`dataclasses`).

- **`Job`**: Represents the overarching Work Order containing multiple sequential operations.
- **`Operation`**: Represents specific repair tasks with flat-rate times and required capabilities.
- **`Technician` & `Station`**: Represents the available resources and their specific capability tags.
- **`BayesianState`**: Holds the matrices for the Bayesian model state.

## Simulation Framework (`simulation/`)

The module includes an interactive terminal UI for running discrete event simulations:
- **`generators.py`**: Generates synthetic shop days including jobs, hidden technician efficiencies, and dynamic events.
- **`runner.py`**: Utilizes the `blessed` library to render an interactive step-through CLI. It renders a visual Gantt chart schedule layout and logs algorithm state changes across discrete events.

## Integration Strategy

Integration with Frappe is intended to be managed externally to this core module. Data from Frappe `DocTypes` (such as `Work Order`, `Employee`, `Workstation`) should be parsed and mapped to the pure domain models (`models.py`) before being passed into the algorithm. The resulting schedule output must then be parsed back into Frappe records for persistence and UI rendering.
