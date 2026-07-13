from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Job:
    """Pure domain model representing a job to be scheduled."""
    id: str
    duration_minutes: int
    required_skills: List[str]
    # Add other relevant attributes (e.g., promised_time, dependencies)

@dataclass
class Technician:
    """Pure domain model representing a technician's availability."""
    id: str
    skills: List[str]
    available_from: datetime
    available_until: datetime

@dataclass
class Station:
    """Pure domain model representing a physical workstation."""
    id: str
    capabilities: List[str]
