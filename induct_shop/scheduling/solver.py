from typing import List, Dict, Any
from ortools.sat.python import cp_model
from .models import Job, Technician, Station

class CPSATSolver:
    def __init__(self, horizon_minutes: int = 43200):
        self.model = cp_model.CpModel()
        self.horizon = horizon_minutes 
        
    def solve(
        self, 
        jobs: List[Job], 
        technicians: List[Technician], 
        stations: List[Station]
    ) -> Dict[str, Any]:
        """
        Creates the CP-SAT formulation and solves for an optimal schedule.
        Returns a dict describing the schedule layout.
        """
        operation_vars = {}
        optional_intervals = {}
        job_ends = {}
        
        # 1. Create Variables
        for job in jobs:
            job_op_ends = []
            for op in job.operations:
                start_var = self.model.NewIntVar(0, self.horizon, f"start_{op.id}")
                end_var = self.model.NewIntVar(0, self.horizon, f"end_{op.id}")
                duration = op.flat_rate_minutes # In a full integration, use BayesianEstimator here
                
                op_presence_literals = []
                
                for tech in technicians:
                    if not all(cap in tech.capabilities for cap in op.required_capabilities):
                        continue
                        
                    for station in stations:
                        if not all(cap in station.capabilities for cap in op.required_capabilities):
                            continue
                            
                        # Valid tech/station combo
                        presence_var = self.model.NewBoolVar(f"presence_{op.id}_{tech.id}_{station.id}")
                        interval_var = self.model.NewOptionalIntervalVar(
                            start_var, duration, end_var, presence_var, 
                            f"interval_{op.id}_{tech.id}_{station.id}"
                        )
                        optional_intervals[(op.id, tech.id, station.id)] = (presence_var, interval_var)
                        op_presence_literals.append(presence_var)
                
                if not op_presence_literals:
                    # Operation cannot be routed. Infeasible.
                    return {"status": "INFEASIBLE (No valid routing)", "assignments": []}
                
                # Constraint: Alternative Assignment. Exactly one combination must be true.
                self.model.AddExactlyOne(op_presence_literals)
                operation_vars[op.id] = (start_var, duration, end_var)
                job_op_ends.append(end_var)
            
            # Job end is the max of all its operation ends
            job_end_var = self.model.NewIntVar(0, self.horizon, f"job_end_{job.id}")
            self.model.AddMaxEquality(job_end_var, job_op_ends)
            job_ends[job.id] = job_end_var
            
            # Constraint: Precedence & Work Order Contiguity
            for op2 in job.operations:
                for op1_id in op2.predecessors:
                    op1 = next((o for o in job.operations if o.id == op1_id), None)
                    if not op1: continue
                    
                    op1_start, op1_dur, op1_end = operation_vars[op1.id]
                    op2_start, op2_dur, op2_end = operation_vars[op2.id]
                    
                    # Standard Precedence: Op1 finishes before Op2 starts
                    self.model.Add(op1_end <= op2_start)
                    
                    # Contiguity Constraint: If Op1 and Op2 are in the same station, they must be contiguous
                    for station in stations:
                        for tech1 in technicians:
                            for tech2 in technicians:
                                key1 = (op1.id, tech1.id, station.id)
                                key2 = (op2.id, tech2.id, station.id)
                                
                                if key1 in optional_intervals and key2 in optional_intervals:
                                    pres1, _ = optional_intervals[key1]
                                    pres2, _ = optional_intervals[key2]
                                    
                                    # Enforce Op2 starts exactly when Op1 ends IF both are present at this station
                                    both_present = self.model.NewBoolVar(f"both_{op1.id}_{op2.id}_{station.id}")
                                    self.model.AddBoolAnd([pres1, pres2]).OnlyEnforceIf(both_present)
                                    self.model.AddBoolOr([pres1.Not(), pres2.Not()]).OnlyEnforceIf(both_present.Not())
                                    
                                    self.model.Add(op2_start == op1_end).OnlyEnforceIf(both_present)

        # Constraint: Disjunctive Resources (NoOverlap)
        for tech in technicians:
            tech_intervals = [interval for (op_id, t_id, s_id), (pres, interval) in optional_intervals.items() if t_id == tech.id]
            if tech_intervals:
                self.model.AddNoOverlap(tech_intervals)
                
        for station in stations:
            station_intervals = [interval for (op_id, t_id, s_id), (pres, interval) in optional_intervals.items() if s_id == station.id]
            if station_intervals:
                self.model.AddNoOverlap(station_intervals)
                
        # Objective: Minimize Makespan (simplification for demonstration)
        makespan = self.model.NewIntVar(0, self.horizon, "makespan")
        if job_ends:
            self.model.AddMaxEquality(makespan, list(job_ends.values()))
        else:
            self.model.Add(makespan == 0)
            
        self.model.Minimize(makespan)

        solver = cp_model.CpSolver()
        # Time limit so web application doesn't hang forever
        solver.parameters.max_time_in_seconds = 5.0
        status = solver.Solve(self.model)

        schedule = {
            "status": solver.StatusName(status),
            "makespan": solver.ObjectiveValue() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
            "assignments": []
        }
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for (op_id, t_id, s_id), (pres, interval) in optional_intervals.items():
                if solver.Value(pres):
                    start_var, dur, end_var = operation_vars[op_id]
                    schedule["assignments"].append({
                        "operation_id": op_id,
                        "job_id": next(j.id for j in jobs for op in j.operations if op.id == op_id),
                        "technician_id": t_id,
                        "station_id": s_id,
                        "start": solver.Value(start_var),
                        "duration": dur,
                        "end": solver.Value(end_var)
                    })
                    
        return schedule
