import sys
import numpy as np
from blessed import Terminal
from .generators import generate_technicians, generate_stations, generate_jobs
from ..solver import CPSATSolver
from ..estimation import BayesianEstimator

def render_schedule(term, schedule, stations, techs):
    out = []
    out.append(term.bold_green("--- Schedule Layout ---"))
    if not schedule.get("assignments"):
        out.append("No assignments or Infeasible.")
        return out
        
    # --- Visual Gantt Chart ---
    job_colors = [term.cyan, term.magenta, term.yellow, term.green, term.red]
    job_color_map = {}
    
    max_end = max(a["end"] for a in schedule["assignments"]) if schedule["assignments"] else 120
    scale = 5  # 1 character = 5 minutes
    
    # Timeline header
    timeline_header = "          |"
    for t in range(0, max_end + 30, 30):
        timeline_header += f"{t:<6}" # 30 mins / 5 = 6 chars
    out.append(term.bold_black_on_white(timeline_header))
    
    for station in stations:
        bay_name = (station.name[:9] + " ").ljust(10)
        line = f"{term.bold(bay_name)}|"
        
        s_assignments = [a for a in schedule["assignments"] if a["station_id"] == station.id]
        s_assignments.sort(key=lambda x: x["start"])
        
        current_pos = 0
        for a in s_assignments:
            start_pos = a["start"] // scale
            dur_pos = a["duration"] // scale
            
            if start_pos > current_pos:
                line += " " * (start_pos - current_pos)
                
            j_id = a["job_id"]
            if j_id not in job_color_map:
                job_color_map[j_id] = job_colors[len(job_color_map) % len(job_colors)]
            color = job_color_map[j_id]
            
            label = f" {j_id}:{a['operation_id']} "
            if len(label) > dur_pos:
                label = f" {j_id} "
            if len(label) > dur_pos:
                label = "*"
                
            block = label.center(dur_pos, "█")
            line += color(block)
            current_pos = start_pos + dur_pos
            
        out.append(line)
        
    # --- Detailed Text List ---
    out.append("\n" + term.bold_green("--- Detailed Assignments ---"))
    
    # Group by Job for better readability
    job_ids = list(set(a["job_id"] for a in schedule["assignments"]))
    job_ids.sort()
    
    for j_id in job_ids:
        color = job_color_map.get(j_id, term.normal)
        out.append(color(term.bold(f"Job {j_id}:")))
        
        j_assignments = [a for a in schedule["assignments"] if a["job_id"] == j_id]
        j_assignments.sort(key=lambda x: x["start"])
        
        for a in j_assignments:
            tech = next((t.name for t in techs if t.id == a["technician_id"]), a["technician_id"])
            bay = next((s.name for s in stations if s.id == a["station_id"]), a["station_id"])
            out.append(f"  [{a['start']:03d}m -> {a['end']:03d}m] {a['operation_id']} | Tech: {tech} | Bay: {bay}")
            
    return out

def run_interactive_simulation():
    term = Terminal()
    
    techs = generate_technicians()
    stations = generate_stations()
    jobs = generate_jobs()
    
    events = [
        {
            "name": "Start of Day", 
            "description": "All jobs arrived. Generating initial schedule based on flat-rates."
        },
        {
            "name": "Job 1 Finishes Early", 
            "description": "Tech T1 finished OP_1 in 40 mins (instead of 60).", 
            "action": "update_bayesian"
        },
        {
            "name": "Job 1 Finished, Time Advances", 
            "description": "Time advanced. The solver is now operating on a reduced horizon.", 
            "action": "advance_time"
        },
    ]
    
    current_event = 0
    solver = CPSATSolver(horizon_minutes=1440) 
    
    print(term.enter_fullscreen())
    try:
        while True:
            print(term.home + term.clear)
            
            # Reconstruct state from scratch to allow forward/backward navigation safely
            techs = generate_technicians()
            stations = generate_stations()
            jobs = generate_jobs()
            
            insights = []
            
            # Apply all actions sequentially up to the current event
            for i in range(current_event + 1):
                ev = events[i]
                if ev.get("action") == "update_bayesian":
                    job1 = next((j for j in jobs if j.id == "J1"), None)
                    if job1:
                        op1 = job1.operations[0]
                        x = np.array([1, 11, 85000, 1.2]) 
                        y_actual = 40.0
                        new_state = BayesianEstimator.update(op1.bayesian_state.state_dict, x, y_actual)
                        op1.bayesian_state.state_dict = new_state
                        
                        if i == current_event: # Only show insights for the current step
                            insights.append(term.cyan(f"Bayesian Model Updated for 'Brake Pad Replacement'."))
                            new_pred = BayesianEstimator.predict_percentile(new_state, x)
                            insights.append(term.cyan(f"New 80th percentile prediction for this exact vehicle/tech profile: {new_pred} mins"))
                        
                        op1.flat_rate_minutes = BayesianEstimator.predict_percentile(new_state, x)
                        
                elif ev.get("action") == "advance_time":
                    jobs = [j for j in jobs if j.id != "J1"]
            
            event = events[current_event]
            
            # --- Solve ---
            schedule = solver.solve(jobs, techs, stations)
            
            # --- Render ---
            print(term.bold_underline(f"Event {current_event + 1} of {len(events)}: {event['name']}"))
            print(event["description"])
            print("")
            for ins in insights:
                print(ins)
            print("")
            
            schedule_out = render_schedule(term, schedule, stations, techs)
            for line in schedule_out:
                print(line)
                
            print("\n" + term.black_on_white(" Use LEFT/RIGHT arrows to navigate. 'q' to quit. "))
            
            with term.cbreak(), term.hidden_cursor():
                val = term.inkey()
                if val.is_sequence:
                    if val.name == "KEY_RIGHT" and current_event < len(events) - 1:
                        current_event += 1
                    elif val.name == "KEY_LEFT" and current_event > 0:
                        current_event -= 1
                elif val.lower() == 'q':
                    break
    finally:
        print(term.exit_fullscreen())

if __name__ == "__main__":
    run_interactive_simulation()
