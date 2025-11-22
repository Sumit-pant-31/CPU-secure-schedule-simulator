# metrics/metrics.py

"""
Robust metrics computation for scheduling simulator.

This module computes:
 - average_waiting_time
 - average_turnaround_time
 - throughput (processes per unit time)
 - cpu_utilization (percentage, 0..100)
 - detection_rate (fraction of processes flagged as rogue)

Compatible input forms:
 - Per-process single-record outputs (start/finish present)
 - Multi-segment outputs (Round Robin) where each segment is a dict with pid/start/finish
 - Uses keys: pid, arrival_time or arrival, burst_time or burst, start, finish, is_rogue
"""

def compute(processes):
    if not processes:
        return {
            "average_waiting_time": 0.0,
            "average_turnaround_time": 0.0,
            "throughput": 0.0,
            "cpu_utilization": 0.0,
            "detection_rate": 0.0
        }

    # Group segments / entries by PID
    grouped = {}
    for p in processes:
        pid = p.get("pid") or str(p.get("pid", "unknown"))
        if pid not in grouped:
            grouped[pid] = {
                "arrival_time": p.get("arrival_time", p.get("arrival", None)),
                "burst_time": p.get("burst_time", p.get("burst", 0)),
                "priority": p.get("priority", None),
                "is_rogue": bool(p.get("is_rogue", False)),
                "segments": []   # (start, finish) pairs
            }
        # collect segment if available
        if p.get("start") is not None and p.get("finish") is not None:
            grouped[pid]["segments"].append((p["start"], p["finish"]))

    # Compute per-process waiting & turnaround using segments when possible
    total_wait = 0.0
    total_turn = 0.0
    completed_count = 0
    rogue_count = 0

    first_arrival = None
    last_finish = None
    busy_time = 0.0

    for pid, info in grouped.items():
        arrival = info["arrival_time"]
        burst = info["burst_time"] if info["burst_time"] is not None else 0

        if arrival is None:
            # If arrival missing, assume 0
            arrival = 0

        segments = sorted(info["segments"])

        if segments:
            # compute process completion and waiting based on segments
            start_first = segments[0][0]
            finish_last = segments[-1][1]
            turnaround = finish_last - arrival
            waiting = turnaround - burst
            # accumulate busy time from segments
            for s, f in segments:
                busy_time += max(0, f - s)
            completed = True
        else:
            # No segments: fallback - assume process executed once from arrival for burst_time
            # We cannot determine waiting/turnaround precisely; assume turnaround = burst
            # waiting = 0 (best-effort fallback)
            turnaround = burst
            waiting = 0.0
            # busy time add burst
            busy_time += burst
            # for simulation bounds, treat finish_last as arrival + burst
            finish_last = arrival + burst
            start_first = arrival
            completed = True

        total_wait += waiting
        total_turn += turnaround
        if info["is_rogue"]:
            rogue_count += 1
        if completed:
            completed_count += 1

        # update global timeline bounds
        if first_arrival is None or start_first < first_arrival:
            first_arrival = start_first
        if last_finish is None or finish_last > last_finish:
            last_finish = finish_last

    # safety for timeline
    if first_arrival is None:
        first_arrival = 0
    if last_finish is None:
        last_finish = first_arrival

    total_sim_time = last_finish - first_arrival
    if total_sim_time <= 0:
        # if zero or negative (degenerate), set to sum of bursts or 1 to avoid division by zero
        sum_bursts = sum(info.get("burst_time", 0) for info in grouped.values())
        total_sim_time = max(sum_bursts, 1.0)

    n = len(grouped)
    avg_wait = (total_wait / n) if n else 0.0
    avg_turn = (total_turn / n) if n else 0.0
    throughput = (completed_count / total_sim_time) if total_sim_time > 0 else 0.0
    cpu_util = (busy_time / total_sim_time) * 100.0
    # clamp cpu_util between 0 and 100
    if cpu_util < 0:
        cpu_util = 0.0
    if cpu_util > 100:
        cpu_util = 100.0

    detection_rate = (rogue_count / n) if n else 0.0

    return {
        "average_waiting_time": round(avg_wait, 3),
        "average_turnaround_time": round(avg_turn, 3),
        "throughput": round(throughput, 3),
        "cpu_utilization": round(cpu_util, 2),
        "detection_rate": round(detection_rate, 3)
    }
