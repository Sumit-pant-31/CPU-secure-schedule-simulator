import random

def generate_processes(num_processes=6):
    """Automatically generate random processes."""
    processes = []
    for i in range(num_processes):
        pid = f"P{i+1}"
        arrival = random.randint(0, 5)
        burst = random.randint(2, 8)
        priority = random.randint(1, 3)
        processes.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "priority": priority
        })
    return processes


def generate_processes_manual():
    """Take process details manually from user."""
    processes = []
    try:
        n = int(input("Enter number of processes: "))
        for i in range(n):
            print(f"\n➡ Enter details for Process P{i+1}")
            arrival = int(input("Arrival Time: "))
            burst = int(input("Burst Time: "))
            priority = int(input("Priority (lower = higher priority): "))
            processes.append({
                "pid": f"P{i+1}",
                "arrival": arrival,
                "burst": burst,
                "priority": priority
            })
    except ValueError:
        print("⚠️ Invalid input. Please enter integer values only.")
    return processes


if __name__ == "__main__":
    print("Choose process generation method:")
    print("1. Manual input")
    print("2. Random generation (default)")
    
    choice = input("Enter choice (1/2): ").strip()
    if choice == "1":
        processes = generate_processes_manual()
    else:
        processes = generate_processes()
    
    print("\nGenerated Processes:")
    for p in processes:
        print(p)
