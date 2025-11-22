# demo_security_demo.py
from scheduler import fcfs, roundrobin
from security import anomaly_detector
from metrics import metrics
from visualization import charts

# Example processes (some rogue)
processes = [
    {"pid": "P1", "arrival": 0, "burst": 12, "priority": 1},  # Rogue: high burst + low priority
    {"pid": "P2", "arrival": 1, "burst": 4, "priority": 3},   # Normal
    {"pid": "P3", "arrival": 2, "burst": 10, "priority": 2},  # Rogue: high burst
    {"pid": "P4", "arrival": 3, "burst": 3, "priority": 4},   # Normal
]

print("Generated Processes:")
for p in processes:
    print(p)

# Apply security
processes_secure = anomaly_detector.detect_and_mitigate([p.copy() for p in processes])

print("\nAfter Security Mitigation:")
for p in processes_secure:
    print(p)

# Run a scheduler (FCFS in this demo)
result = fcfs.run_fcfs(processes_secure)

# Compute metrics
metrics_data = metrics.compute(result["processes"])
print("\nMetrics:")
for k, v in metrics_data.items():
    print(f"{k}: {v:.2f}")

# Visualize
charts.plot_gantt_chart(result["processes"], title="FCFS with Security Demo")
charts.plot_metrics_dashboard(metrics_data, algorithm_name="FCFS with Security")
