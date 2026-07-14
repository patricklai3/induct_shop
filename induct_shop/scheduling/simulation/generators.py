import random
from typing import List
from datetime import datetime
from ..models import Job, Technician, Station, Operation, BayesianState
from ..estimation import BayesianEstimator

def generate_technicians() -> List[Technician]:
    return [
        Technician(
            id="T1", name="Alice (Master)", capabilities=["brakes", "engine", "alignment", "electrical"],
            efficiency_multiplier=1.2
        ),
        Technician(
            id="T2", name="Bob (Apprentice)", capabilities=["brakes", "oil_change"],
            efficiency_multiplier=0.8
        )
    ]

def generate_stations() -> List[Station]:
    return [
        Station(id="S1", name="Bay 1 (Standard Lift)", capabilities=["brakes", "oil_change", "engine", "electrical"]),
        Station(id="S2", name="Bay 2 (Alignment Rack)", capabilities=["brakes", "alignment", "oil_change"])
    ]

def generate_jobs() -> List[Job]:
    brakes_state = BayesianEstimator.init_prior(flat_rate_minutes=60)
    op1 = Operation(
        id="OP_1", job_id="J1", name="Brake Pad Replacement",
        flat_rate_minutes=60, required_capabilities=["brakes"],
        bayesian_state=BayesianState(state_dict=brakes_state)
    )
    j1 = Job(
        id="J1", vehicle_make="Toyota", vehicle_model="Camry", vehicle_year=2015, vehicle_mileage=85000,
        promised_delivery_time=datetime(2026, 7, 14, 12, 0), operations=[op1]
    )
    
    alignment_state = BayesianEstimator.init_prior(flat_rate_minutes=45)
    brakes_state_2 = BayesianEstimator.init_prior(flat_rate_minutes=60)
    op2_a = Operation(
        id="OP_2A", job_id="J2", name="Brake Rotor Replacement",
        flat_rate_minutes=60, required_capabilities=["brakes"],
        bayesian_state=BayesianState(state_dict=brakes_state_2)
    )
    op2_b = Operation(
        id="OP_2B", job_id="J2", name="Wheel Alignment",
        flat_rate_minutes=45, required_capabilities=["alignment"],
        bayesian_state=BayesianState(state_dict=alignment_state),
        predecessors=["OP_2A"]
    )
    j2 = Job(
        id="J2", vehicle_make="Honda", vehicle_model="Civic", vehicle_year=2018, vehicle_mileage=60000,
        promised_delivery_time=datetime(2026, 7, 14, 17, 0), operations=[op2_a, op2_b]
    )
    
    return [j1, j2]
