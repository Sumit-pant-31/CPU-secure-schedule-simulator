# main.py
from process_generator import generate_processes
from scheduler import fcfs, sjf, srtf, rr, priority
from security import anomaly_detector
from metrics import metrics
from visualization import charts

def run_scheduler(algorithm, processes, quantum=3, secure=False):
    """
    Run the selected scheduler with optional security.
    Returns a dict with process results.
    """
    # Copy list to avoid mutation
    proc_copy = [p.copy() for p in processes]

    # Apply security layer if needed
    if secure:
        proc_copy = anomaly_detector.detect_and_mitigate(proc_copy)

    # Select scheduler
    if algorithm == "FCFS":
        result = fcfs.run_fcfs(proc_copy)
    elif algorithm == "SJF":
        result = sjf.run_sjf(proc_copy)
    elif algorithm == "SRTF":
        result = srtf.run_srtf(proc_copy)
    elif algorithm == "RR":
        result = rr.run_rr(proc_copy, quantum=quantum)
    elif algorithm == "PRIORITY":
        result = priority.run_priority(proc_copy)
    else:
        raise ValueError("Invalid algorithm")

    # Compute metrics
    result["metrics"] = metrics.compute(result["processes"])
    return result

def display_results(result, algorithm):
    print(f"\n===== {algorithm} Scheduling Results =====")
    print("PID | Arrival | Burst | Priority | Waiting | Turnaround | Rogue | Terminated")
    for p in result["processes"]:
        print(f"{p['pid']:>3} | {p['arrival']:>7} | {p['burst']:>5} | {p.get('priority',0):>8} | "
              f"{p.get('waiting',0):>7} | {p.get('turnaround',0):>10} | "
              f"{str(p.get('is_rogue',False)):>5} | {str(p.get('terminated',False)):>10}")

    print("\n📈 Metrics:")
    for k, v in result["metrics"].items():
        print(f"  {k}: {v:.2f}")

    # Visualization
    charts.plot_gantt_chart(result["processes"], title=f"{algorithm} Gantt Chart")
    charts.plot_metrics_dashboard(result["metrics"], algorithm_name=algorithm)

if __name__ == "__main__":
    print("🔹 Secure Process Scheduler Simulator 🔹")

    # User input
    algorithm = input("Select algorithm (FCFS/SJF/SRTF/RR/PRIORITY): ").strip().upper()
    secure_mode = input("Enable security layer? (y/n): ").lower() == 'y'
    quantum = 3
    if algorithm == "RR":
        q_input = input("Enter time quantum (default 3): ")
        quantum = int(q_input) if q_input.isdigit() else 3

    # Generate processes
    num_proc = input("Enter number of processes (default 6): ")
    num_proc = int(num_proc) if num_proc.isdigit() else 6
    processes = generate_processes(num_processes=num_proc)

    print("\nGenerated Processes:")
    for p in processes:
        print(p)

    # Run scheduler
    result = run_scheduler(algorithm, processes, quantum=quantum, secure=secure_mode)

    # Display results
    display_results(result, algorithm)

    print("\n✅ Simulation complete!")
