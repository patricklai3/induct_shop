from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class BayesianState:
    """Holds the mathematical state matrices for the Bayesian model."""
    state_dict: dict

@dataclass
class Operation:
    """A specific repair task within a Work Order."""
    id: str
    job_id: str
    name: str
    flat_rate_minutes: int
    required_capabilities: List[str]
    bayesian_state: BayesianState
    # Preceding operation IDs within the same job (topological order)
    predecessors: List[str] = field(default_factory=list)

@dataclass
class Job:
    """Represents a Work Order containing one or more operations."""
    id: str
    operations: List[Operation] = field(default_factory=list)

@dataclass
class Technician:
    """Technician resource profile."""
    id: str
    name: str
    capabilities: List[str]
    efficiency_multiplier: float = 1.0  # HBM could update this over time
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    is_absent: bool = False

@dataclass
class Station:
    """Physical service bay profile."""
    id: str
    name: str
    capabilities: List[str]
