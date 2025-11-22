# gui_app.py
import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy
import traceback

# ----- Import Scheduler Algorithms -----
from scheduler.fcfs import run_fcfs
from scheduler.sjf import run_sjf
from scheduler.srtf import run_srtf
from scheduler.roundrobin import run_roundrobin
from scheduler.priority import run_priority

# ----- Import Security -----
from security.anomaly_detector import detect_and_mitigate

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


class CPUSchedulerApp:
    def __init__(self, root):
        self.root = root
        root.title("Secure CPU Scheduler Simulator (GUI)")
        root.geometry("980x720")

        self.process_list = []
        self.last_single_result = None      # store last single algorithm result
        self.last_all_results = None        # store dict for all-mode
        self.dark_mode = tk.BooleanVar(value=False)

        # ------------ INPUT FRAME ------------
        frame = ttk.LabelFrame(root, text="Add New Process")
        frame.pack(fill="x", padx=10, pady=6)

        ttk.Label(frame, text="Arrival").grid(row=0, column=0)
        ttk.Label(frame, text="Burst").grid(row=0, column=1)
        ttk.Label(frame, text="Priority").grid(row=0, column=2)

        self.arrival_entry = ttk.Entry(frame, width=10)
        self.burst_entry = ttk.Entry(frame, width=10)
        self.priority_entry = ttk.Entry(frame, width=10)

        self.arrival_entry.grid(row=1, column=0)
        self.burst_entry.grid(row=1, column=1)
        self.priority_entry.grid(row=1, column=2)

        ttk.Button(frame, text="Add Process", command=self.add_process).grid(row=1, column=3, padx=8)

        # ------------ PROCESS TABLE ------------
        self.tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst", "Priority"), show="headings", height=8)
        for col in ("PID", "Arrival", "Burst", "Priority"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        self.tree.pack(fill="x", padx=10, pady=6)

        # ------------ OPTIONS ------------
        opt = ttk.LabelFrame(root, text="Options")
        opt.pack(fill="x", padx=10, pady=6)

        ttk.Label(opt, text="Algorithm:").pack(side="left")
        self.algo_var = tk.StringVar()
        algo_dropdown = ttk.Combobox(
            opt,
            textvariable=self.algo_var,
            values=["FCFS", "SJF", "SRTF", "Round Robin", "Priority", "All"],
            width=16
        )
        algo_dropdown.pack(side="left", padx=6)

        ttk.Label(opt, text="Quantum (RR Only):").pack(side="left")
        self.quantum_entry = ttk.Entry(opt, width=6)
        self.quantum_entry.pack(side="left", padx=6)

        self.security_var = tk.BooleanVar()
        ttk.Checkbutton(opt, text="Enable Security", variable=self.security_var).pack(side="left", padx=6)

        ttk.Checkbutton(opt, text="Dark Mode", variable=self.dark_mode, command=self.apply_dark_mode).pack(side="left", padx=6)

        ttk.Button(opt, text="Run Scheduling", command=self.run_scheduler).pack(side="right", padx=6)

        # ------------ METRICS & EXPORT FRAME ------------
        bottom = ttk.Frame(root)
        bottom.pack(fill="both", expand=True, padx=10, pady=8)

        # Metrics panel (left)
        metrics_frame = ttk.LabelFrame(bottom, text="Metrics")
        metrics_frame.pack(side="left", fill="both", expand=False, padx=6, pady=6)

        self.metrics_text = tk.Text(metrics_frame, width=36, height=14, wrap="none")
        self.metrics_text.pack(padx=6, pady=6)

        export_frame = ttk.Frame(metrics_frame)
        export_frame.pack(fill="x", padx=6, pady=6)
        ttk.Button(export_frame, text="Export Metrics CSV", command=self.export_metrics_csv).pack(side="left", padx=4)
        ttk.Button(export_frame, text="Export Last Chart PNG", command=self.export_last_chart_png).pack(side="left", padx=4)

        # Right area: instructions and small preview placeholder
        info_frame = ttk.LabelFrame(bottom, text="Preview / Info")
        info_frame.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        ttk.Label(info_frame, text="Charts open in separate windows. Use 'All' to view combined dashboard.").pack(anchor="nw", padx=6, pady=4)
        self.preview_label = ttk.Label(info_frame, text="No run yet.")
        self.preview_label.pack(anchor="nw", padx=6, pady=4)

    # ---------------- Add process ----------------
    def add_process(self):
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            pid = f"P{len(self.process_list) + 1}"
            proc = {"pid": pid, "arrival_time": arrival, "burst_time": burst, "priority": priority}
            self.process_list.append(proc)
            self.tree.insert("", tk.END, values=(pid, arrival, burst, priority))

            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for arrival/burst/priority.")

    # ---------------- normalize ----------------
    def normalize(self, plist):
        normalized = []
        for p in plist:
            q = p.copy()
            q["arrival"] = q.get("arrival_time", q.get("arrival", 0))
            q["arrival_time"] = q["arrival"]
            q["burst"] = q.get("burst_time", q.get("burst", 0))
            q["burst_time"] = q["burst"]
            q.setdefault("priority", 1)
            q.setdefault("is_rogue", False)
            q.setdefault("start", None)
            q.setdefault("finish", None)
            q.setdefault("waiting_time", 0)
            q.setdefault("turnaround_time", 0)
            q.setdefault("terminated", False)
            normalized.append(q)
        return normalized

    # ---------------- apply dark mode (sets matplotlib style only) ----------------
    def apply_dark_mode(self):
        if self.dark_mode.get():
            plt.style.use("dark_background")
        else:
            plt.style.use("default")
        # update preview label color
        self.preview_label.config(text="(Dark mode ON)" if self.dark_mode.get() else "(Dark mode OFF)")

    # ---------------- run scheduler ----------------
    def run_scheduler(self):
        if not self.process_list:
            messagebox.showerror("Error", "Add at least one process.")
            return
        algo = self.algo_var.get()
        if algo == "":
            messagebox.showerror("Error", "Select an algorithm.")
            return

        base = self.normalize(copy.deepcopy(self.process_list))
        if self.security_var.get():
            try:
                base = detect_and_mitigate(copy.deepcopy(base))
            except Exception:
                traceback.print_exc()
                messagebox.showerror("Security Error", "Security module error; check console.")
                return

        # ALL mode
        if algo == "All":
            algorithms = [
                ("FCFS", run_fcfs),
                ("SJF", run_sjf),
                ("SRTF", run_srtf),
                ("Round Robin", run_roundrobin),
                ("Priority", run_priority)
            ]
            results = {}
            metrics_summary = {}
            for name, func in algorithms:
                proc_copy = copy.deepcopy(base)
                try:
                    if name == "Round Robin":
                        raw_q = self.quantum_entry.get().strip()
                        if raw_q == "":
                            q = 2
                        else:
                            q = int(raw_q)
                        out = func(proc_copy, q)
                    else:
                        out = func(proc_copy)
                except Exception:
                    traceback.print_exc()
                    messagebox.showerror("Scheduler Error", f"{name} failed; check console.")
                    return
                scheduled = out.get("processes", out)
                results[name] = scheduled
                metrics_summary[name] = self.compute_metrics(scheduled)
            self.last_all_results = {"results": results, "metrics": metrics_summary}
            self.update_metrics_text_all(metrics_summary)
            self.show_all_charts(results)
            return

        # Single algorithm mode
        try:
            processes = copy.deepcopy(base)
            if algo == "FCFS":
                out = run_fcfs(processes)
            elif algo == "SJF":
                out = run_sjf(processes)
            elif algo == "SRTF":
                out = run_srtf(processes)
            elif algo == "Round Robin":
                raw_q = self.quantum_entry.get().strip()
                if raw_q == "":
                    q = 2
                else:
                    q = int(raw_q)
                out = run_roundrobin(processes, q)
            elif algo == "Priority":
                out = run_priority(processes)
            else:
                messagebox.showerror("Error", "Unknown algorithm selected.")
                return
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Scheduler Error", "Scheduler execution failed; check console.")
            return

        scheduled = out.get("processes", out)
        metrics = self.compute_metrics(scheduled)
        self.last_single_result = {"algo": algo, "processes": scheduled, "metrics": metrics}
        self.update_metrics_text(metrics, algo)
        self.show_gantt(scheduled, algo)

    # ---------------- compute metrics ----------------
    def compute_metrics(self, processes):
        # compute average waiting, turnaround; throughput and cpu_util (basic)
        n = 0
        total_wait = 0.0
        total_turn = 0.0
        first_start = None
        last_finish = None
        detected = 0
        for p in processes:
            # skip terminated processes
            if p.get("terminated"):
                continue
            n += 1
            # waiting_time or fallback start-arrival
            wt = p.get("waiting_time")
            if wt is None or wt == 0:
                if p.get("start") is not None and p.get("arrival_time") is not None:
                    wt = p["start"] - p["arrival_time"]
            tt = p.get("turnaround_time")
            if tt is None or tt == 0:
                if p.get("finish") is not None and p.get("arrival_time") is not None:
                    tt = p["finish"] - p["arrival_time"]
            wt = wt if wt is not None else 0
            tt = tt if tt is not None else 0
            total_wait += wt
            total_turn += tt
            if p.get("is_rogue"):
                detected += 1
            if p.get("start") is not None:
                if first_start is None or p["start"] < first_start:
                    first_start = p["start"]
            if p.get("finish") is not None:
                if last_finish is None or p["finish"] > last_finish:
                    last_finish = p["finish"]

        avg_wait = (total_wait / n) if n else 0.0
        avg_turn = (total_turn / n) if n else 0.0
        total_time = (last_finish - first_start) if (first_start is not None and last_finish is not None) else 0.0
        throughput = (n / total_time) if total_time > 0 else 0.0
        busy_time = 0.0
        for p in processes:
            if p.get("start") is not None and p.get("finish") is not None:
                busy_time += (p["finish"] - p["start"])
        cpu_util = (busy_time / total_time * 100) if total_time > 0 else 0.0
        detection_rate = (detected / n) if n else 0.0

        return {
            "average_waiting_time": round(avg_wait, 3),
            "average_turnaround_time": round(avg_turn, 3),
            "throughput": round(throughput, 3),
            "cpu_utilization": round(cpu_util, 2),
            "detection_rate": round(detection_rate, 3)
        }

    # ---------------- update metrics text (single) ----------------
    def update_metrics_text(self, metrics, algo_name):
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, f"Algorithm: {algo_name}\n")
        self.metrics_text.insert(tk.END, "-" * 30 + "\n")
        for k, v in metrics.items():
            self.metrics_text.insert(tk.END, f"{k}: {v}\n")
        self.preview_label.config(text=f"Last run: {algo_name}")

    # ---------------- update metrics text (all) ----------------
    def update_metrics_text_all(self, metrics_summary):
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, "All Algorithms Metrics\n")
        self.metrics_text.insert(tk.END, "-" * 36 + "\n")
        for algo, met in metrics_summary.items():
            self.metrics_text.insert(tk.END, f"{algo}:\n")
            for k, v in met.items():
                self.metrics_text.insert(tk.END, f"  {k}: {v}\n")
            self.metrics_text.insert(tk.END, "\n")
        self.preview_label.config(text="Last run: All algorithms")

    # ---------------- show single gantt ----------------
    def show_gantt(self, processes, algo_name):
        fig, ax = plt.subplots(figsize=(9, 3))
        idx = 0
        for p in processes:
            if p.get("start") is None or p.get("finish") is None:
                continue
            duration = p["finish"] - p["start"]
            color = "red" if p.get("is_rogue") else "blue"
            ax.broken_barh([(p["start"], duration)], (idx * 10, 9), facecolors=color)
            ax.text(p["start"] + 0.1, idx * 10 + 5, p["pid"], color="white", fontsize=8, va="center")
            idx += 1

        if idx == 0:
            messagebox.showinfo("No Data", "No valid start/finish timings to plot.")
            return

        ax.set_yticks([i * 10 + 5 for i in range(idx)])
        ax.set_yticklabels([p["pid"] for p in processes if p.get("start") is not None])
        ax.set_xlabel("Time")
        ax.set_ylabel("Processes")
        ax.set_title(f"{algo_name} Scheduling")
        ax.grid(True)
        fig.subplots_adjust(bottom=0.25)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # store last single chart fig for export
        self._last_fig = fig
        win = tk.Toplevel(self.root)
        win.title(f"{algo_name} Gantt Chart")
        canvas = FigureCanvasTkAgg(fig, win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- show all charts in dashboard ----------------
    def show_all_charts(self, results):
        win = tk.Toplevel(self.root)
        win.title("All Algorithms - Gantt Chart Dashboard")
        win.geometry("1150x900")
        canvas = tk.Canvas(win)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._last_all_figs = []
        for algo_name, processes in results.items():
            fig, ax = plt.subplots(figsize=(10, 3))
            idx = 0
            for p in processes:
                if p.get("start") is None or p.get("finish") is None:
                    continue
                duration = p["finish"] - p["start"]
                color = "red" if p.get("is_rogue") else "blue"
                ax.broken_barh([(p["start"], duration)], (idx * 10, 9), facecolors=color)
                ax.text(p["start"] + 0.1, idx * 10 + 5, p["pid"], color="white", fontsize=8)
                idx += 1
            ax.set_yticks([i * 10 + 5 for i in range(idx)])
            ax.set_yticklabels([p["pid"] for p in processes if p.get("start")])
            ax.set_xlabel("Time")
            ax.set_ylabel("Processes")
            ax.set_title(f"{algo_name} Scheduling")
            ax.grid(True)
            fig.subplots_adjust(bottom=0.25)
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas_fig = FigureCanvasTkAgg(fig, master=frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(pady=18)
            self._last_all_figs.append((algo_name, fig))
        # store last_all_results for export metrics
        self._last_all_results = results

    # ---------------- export last chart png ----------------
    def export_last_chart_png(self):
        # prefer _last_fig if single; else allow saving all figs
        if hasattr(self, "_last_fig") and self._last_fig:
            path = filedialog.asksaveasfilename(initialdir=EXPORT_DIR, defaultextension=".png",
                                                filetypes=[("PNG files", "*.png")], title="Save chart as PNG")
            if path:
                try:
                    self._last_fig.savefig(path, bbox_inches="tight")
                    messagebox.showinfo("Saved", f"Chart saved to {path}")
                except Exception:
                    traceback.print_exc()
                    messagebox.showerror("Error", "Failed to save chart. Check console.")
        elif hasattr(self, "_last_all_figs") and self._last_all_figs:
            # ask folder
            dirpath = filedialog.askdirectory(initialdir=EXPORT_DIR, title="Select folder to save all charts")
            if dirpath:
                for name, fig in self._last_all_figs:
                    safe_name = name.replace(" ", "_")
                    out = os.path.join(dirpath, f"{safe_name}.png")
                    try:
                        fig.savefig(out, bbox_inches="tight")
                    except Exception:
                        traceback.print_exc()
                messagebox.showinfo("Saved", f"All charts saved to {dirpath}")
        else:
            messagebox.showinfo("No Chart", "No chart available to export. Run a simulation first.")

    # ---------------- export metrics csv ----------------
    def export_metrics_csv(self):
        # prefer last_all_results metrics, else last_single_result
        rows = []
        if hasattr(self, "last_all_results") and self.last_all_results:
            # last_all_results is a dict {"results":..., "metrics":...} - but in run we set self.last_all_results differently
            # try to use self._last_all_results (set in show_all_charts) or last_all_results variable
            metrics_dict = None
            if hasattr(self, "_last_all_results") and self._last_all_results:
                metrics_dict = {}
                for k, v in self._last_all_results.items():
                    metrics_dict[k] = self.compute_metrics(v)
            elif self.last_all_results and "metrics" in self.last_all_results:
                metrics_dict = self.last_all_results["metrics"]
            if metrics_dict:
                for algo, met in metrics_dict.items():
                    row = {"algorithm": algo}
                    row.update(met)
                    rows.append(row)
        if not rows and self.last_single_result:
            row = {"algorithm": self.last_single_result["algo"]}
            row.update(self.last_single_result["metrics"])
            rows.append(row)

        if not rows:
            messagebox.showinfo("No Metrics", "No metrics available to export. Run a simulation first.")
            return

        path = filedialog.asksaveasfilename(initialdir=EXPORT_DIR, defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")], title="Save metrics CSV")
        if not path:
            return
        keys = ["algorithm", "average_waiting_time", "average_turnaround_time", "throughput", "cpu_utilization", "detection_rate"]
        try:
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in rows:
                    # ensure all keys present
                    out = {k: r.get(k, "") for k in keys}
                    writer.writerow(out)
            messagebox.showinfo("Saved", f"Metrics exported to {path}")
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Error", "Failed to save CSV. Check console.")

# ========================= RUN APP =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerApp(root)
    root.mainloop()