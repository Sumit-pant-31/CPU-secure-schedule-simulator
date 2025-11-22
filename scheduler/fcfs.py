def run_fcfs(processes):
    """
    First Come First Serve Scheduling (Non-Preemptive)
    """
    processes.sort(key=lambda x: x['arrival'])
    time = 0
    for p in processes:
        if time < p['arrival']:
            time = p['arrival']
        p['start'] = time
        p['finish'] = time + p['burst']
        p['turnaround'] = p['finish'] - p['arrival']
        p['waiting'] = p['turnaround'] - p['burst']
        time = p['finish']
    return {"processes": processes}
