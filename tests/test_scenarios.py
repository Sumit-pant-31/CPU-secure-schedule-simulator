# tests/test_scenarios.py
from process_generator import generate_processes
from scheduler import fcfs, sjf, srtf, rr, priority
from security import anomaly_detector
from metrics import metrics
from visualization import charts

def run_test_scenario(algorithm="FCFS", num_processes=6, secure=False, quantum=3):
    # Generate processes
    processes = generate_processes(num_processes=num_processes)
    print("\nGenerated Processes:")
    for p in processes:
        print(p)

    # Apply security layer if needed
    if secure:
        processes = anomaly_detector.detect_and_mitigate(processes)

    # Run selected scheduler
    if algorithm == "FCFS":
        result = fcfs.run_fcfs(processes)
    elif algorithm == "SJF":
        result = sjf.run_sjf(processes)
    elif algorithm == "SRTF":
        result = srtf.run_srtf(processes)
    elif algorithm == "RR":
        result = rr.run_rr(processes, quantum=quantum)
    elif algorithm == "PRIORITY":
        result = priority.run_priority(processes)
    else:
        raise ValueError("Invalid algorithm name")

    # Compute metrics
    metrics_data = metrics.compute(result["processes"])
    print("\nMetrics:")
    for k, v in metrics_data.items():
        print(f"{k}: {v:.2f}")

    # Visualize
    charts.plot_gantt_chart(result["processes"], title=f"{algorithm} Gantt Chart")
    charts.plot_metrics_dashboard(metrics_data, algorithm_name=algorithm)


# Example: Run multiple test scenarios
if __name__ == "__main__":
    print("=== Test Scenario 1: FCFS without Security ===")
    run_test_scenario(algorithm="FCFS", num_processes=5, secure=False)

    print("\n=== Test Scenario 2: Round Robin with Security ===")
    run_test_scenario(algorithm="RR", num_processes=6, secure=True, quantum=3)
