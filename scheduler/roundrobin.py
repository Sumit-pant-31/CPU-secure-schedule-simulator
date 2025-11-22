def run_roundrobin(processes, quantum=3):
    """
    Round Robin Scheduling (Preemptive)
    Works for GUI (multiple segments)
    Works for terminal tests (complete timeline)
    """

    # normalize
    for p in processes:
        p["arrival_time"] = p.get("arrival_time", p.get("arrival", 0))
        p["burst_time"] = p.get("burst_time", p.get("burst", 0))
        p["priority"] = p.get("priority", 1)
        p["remaining"] = p["burst_time"]
        p["start_times"] = []
        p["finish_times"] = []

    processes.sort(key=lambda x: x["arrival_time"])

    time = 0
    i = 0
    n = len(processes)
    queue = []

    while i < n or queue:

        # Add processes that have arrived
        while i < n and processes[i]["arrival_time"] <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i]["arrival_time"]
            continue

        current = queue.pop(0)

        # Run slice
        slice_start = time
        run_time = min(quantum, current["remaining"])
        time += run_time
        slice_end = time

        # Record this RR segment
        current["start_times"].append(slice_start)
        current["finish_times"].append(slice_end)

        current["remaining"] -= run_time

        # Add processes that arrived during the slice
        while i < n and processes[i]["arrival_time"] <= time:
            queue.append(processes[i])
            i += 1

        # If still pending → requeue
        if current["remaining"] > 0:
            queue.append(current)

    # Build gantt output (one entry per slice)
    gantt = []
    for p in processes:
        for s, f in zip(p["start_times"], p["finish_times"]):
            gantt.append({
                "pid": p["pid"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "priority": p["priority"],
                "start": s,
                "finish": f,
                "is_rogue": p.get("is_rogue", False)
            })

    return {"processes": sorted(gantt, key=lambda x: x["start"])}
