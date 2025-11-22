def run_priority(processes):
    """
    Priority Scheduling (Lower number = Higher priority)
    """
    processes.sort(key=lambda x: (x['arrival'], x['priority']))
    completed = []
    ready = []
    time = 0

    while len(completed) < len(processes):
        for p in processes:
            if p not in completed and p['arrival'] <= time and p not in ready:
                ready.append(p)
        if not ready:
            time += 1
            continue
        ready.sort(key=lambda x: x['priority'])
        current = ready.pop(0)
        current['start'] = time
        time += current['burst']
        current['finish'] = time
        current['turnaround'] = current['finish'] - current['arrival']
        current['waiting'] = current['turnaround'] - current['burst']
        completed.append(current)
    return {"processes": completed}
