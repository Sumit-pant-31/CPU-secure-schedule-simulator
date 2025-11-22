# security/anomaly_detector.py

def detect_and_mitigate(processes, burst_threshold=8, priority_threshold=2):
    """
    Detect rogue processes and mitigate them.
    
    Parameters:
    - processes: list of process dicts
    - burst_threshold: burst time above which a process may be considered rogue
    - priority_threshold: priority below which process can be demoted
    """
    for p in processes:
        p['is_rogue'] = False  # default

        # --- Detection Rules ---
        if p['burst'] > burst_threshold:
            p['is_rogue'] = True
        if p.get('priority', 0) < priority_threshold:
            p['is_rogue'] = True

        # --- Mitigation Strategies ---
        if p['is_rogue']:
            #  Throttling: reduce effective burst by 50%
            p['burst'] = max(1, p['burst'] // 2)

            #  Priority Demotion: increase numerical priority (lower priority)
            if 'priority' in p:
                p['priority'] = min(10, p['priority'] + 3)

            #  Optional Termination: if still too high, mark as terminated
            if p['burst'] > burst_threshold:
                p['terminated'] = True
            else:
                p['terminated'] = False
        else:
            p['terminated'] = False

    return processes