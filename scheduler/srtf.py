def run_srtf(processes):
    """
    Shortest Remaining Time First (Preemptive)
    """
    processes.sort(key=lambda x: x['arrival'])
    n = len(processes)
    remaining = [p['burst'] for p in processes]
    completed = 0
    time = 0
    last_proc = -1

    while completed < n:
        # Pick process with minimum remaining time
        ready = [i for i, p in enumerate(processes) if p['arrival'] <= time and remaining[i] > 0]
        if not ready:
            time += 1
            continue
        idx = min(ready, key=lambda i: remaining[i])

        if last_proc != idx:
            processes[idx]['start'] = time
            last_proc = idx

        remaining[idx] -= 1
        time += 1

        if remaining[idx] == 0:
            completed += 1
            processes[idx]['finish'] = time
            processes[idx]['turnaround'] = time - processes[idx]['arrival']
            processes[idx]['waiting'] = processes[idx]['turnaround'] - processes[idx]['burst']

    return {"processes": processes}
