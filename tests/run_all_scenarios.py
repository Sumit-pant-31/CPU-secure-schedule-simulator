# tests/run_all_scenarios.py

from copy import deepcopy
from process_generator import generate_processes, generate_processes_manual
from scheduler import fcfs, sjf, srtf, roundrobin
from scheduler import priority as priority_scheduler  # Corrected import
from security import anomaly_detector
from metrics import metrics
from visualization import charts
import pandas as pd

# -----------------------------
# Function to run all algorithms
# -----------------------------
def run_all_algorithms(processes, quantum=3, secure_mode=False):
    algorithms = {
        "FCFS": fcfs.run_fcfs,
        "SJF": sjf.run_sjf,
        "SRTF": srtf.run_srtf,
        "RR": lambda proc: roundrobin.run_roundrobin(proc, quantum=quantum),
        "Priority": priority_scheduler.run_priority
    }

    results = {}

    for alg_name, func in algorithms.items():
        results[alg_name] = {}

        # Without Security
        proc_copy = deepcopy(processes)
        result = func(proc_copy)
        results[alg_name]["Without Security"] = {
            "processes": result["processes"],
            "metrics": metrics.compute(result["processes"])
        }

        # With Security
        proc_copy = deepcopy(processes)
        proc_copy = anomaly_detector.detect_and_mitigate(proc_copy) if secure_mode else proc_copy
        result_secure = func(proc_copy)
        results[alg_name]["With Security"] = {
            "processes": result_secure["processes"],
            "metrics": metrics.compute(result_secure["processes"])
        }

    return results

# -----------------------------
# Pretty print process table
# -----------------------------
def print_process_table(processes):
    df = pd.DataFrame(processes)
    print("\n🧮 Process Table")
    print("-" * 50)
    print(df.to_string(index=False))
    print("-" * 50)

# -----------------------------
# Visualization: All Gantt Charts Together
# -----------------------------
def visualize_all_combined(results):
    import matplotlib.pyplot as plt

    algorithms = list(results.keys())
    modes = list(next(iter(results.values())).keys())  # ['Without Security', 'With Security']

    rows = len(algorithms)
    cols = len(modes)
    fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 2.5*rows), squeeze=False)
    fig.suptitle("All Algorithms Gantt Charts", fontsize=16)

    for i, alg in enumerate(algorithms):
        for j, mode in enumerate(modes):
            ax = axes[i][j]
            proc_list = results[alg][mode]["processes"]

            y_labels = []
            y_ticks = []

            for k, p in enumerate(proc_list):
                if 'start' not in p or 'finish' not in p:
                    continue
                start = p['start']
                finish = p['finish']
                duration = finish - start
                color = 'red' if p.get('is_rogue', False) else 'blue'
                ax.broken_barh([(start, duration)], (k*10, 9), facecolors=color)
                y_labels.append(p['pid'])
                y_ticks.append(k*10 + 5)

            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_labels)
            ax.set_xlabel("Time")
            ax.set_ylabel("Processes")
            ax.set_title(f"{alg} ({mode})")
            ax.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    print("=== 🧠 Secure Scheduler Simulator ===")
    choice = input("Generate processes manually? (y/n): ").strip().lower()
    if choice == 'y':
        processes = generate_processes_manual()
    else:
        processes = generate_processes(num_processes=6)

    print_process_table(processes)

    # Run algorithms
    results = run_all_algorithms(processes, quantum=3, secure_mode=True)

    # Print metrics
    print("\n=== Metrics for All Algorithms ===\n")
    for alg, modes_data in results.items():
        for mode, data in modes_data.items():
            print(f"-> {alg} ({mode}):")
            for k, v in data["metrics"].items():
                print(f"   {k}: {v:.2f}")
            print("-"*40)

    # Visualize all Gantt charts together
    visualize_all_combined(results)
