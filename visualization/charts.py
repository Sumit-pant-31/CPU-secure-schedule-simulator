# visualization/charts.py
import matplotlib.pyplot as plt

def plot_gantt_chart(processes, title="Gantt Chart"):
    """
    Plots a Gantt chart for the given processes.
    Highlights rogue processes in red.
    Skips any process without 'start' or 'finish' keys.
    """
    fig, ax = plt.subplots(figsize=(10, len(processes)))

    y_labels = []
    y_ticks = []

    for i, p in enumerate(processes):
        # Skip if process doesn't have timing info
        if 'start' not in p or 'finish' not in p:
            continue

        start = p['start']
        finish = p['finish']
        duration = finish - start

        color = 'red' if p.get('is_rogue', False) else 'blue'
        ax.broken_barh([(start, duration)], (i*10, 9), facecolors=color)

        y_labels.append(p['pid'])
        y_ticks.append(i*10 + 5)

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time")
    ax.set_ylabel("Processes")
    ax.set_title(title)
    ax.grid(True)

    plt.tight_layout()
    plt.show(block=False)



def plot_metrics_dashboard(metrics_data, algorithm_name="Algorithm"):
    """
    Plots a dashboard of key metrics for the scheduling algorithm.
    """
    # Metrics to display
    metric_labels = [
        "Avg Waiting Time",
        "Avg Turnaround Time",
        "Throughput",
        "CPU Utilization",
        "Detection Rate"
    ]
    
    metric_values = [
        metrics_data.get("average_waiting_time", 0),
        metrics_data.get("average_turnaround_time", 0),
        metrics_data.get("throughput", 0),
        metrics_data.get("cpu_utilization", 0),
        metrics_data.get("detection_rate", 0)
    ]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bars = ax.bar(metric_labels, metric_values, color=['skyblue', 'skyblue', 'skyblue', 'green', 'red'])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    ax.set_title(f"{algorithm_name} Metrics Dashboard")
    ax.set_ylabel("Value")
    ax.set_ylim(0, max(metric_values)*1.2)  # Add 20% headroom
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()
