
import math
import subprocess
from statistics import median

SAMPLES = 50
REPEAT = 100000

# 1) C Compilation
subprocess.run(["gcc", "tau1_C.c", "-O2", "-o", "tau1"], check=True)

# 2) C code execution
result = subprocess.run(["./tau1", str(SAMPLES), str(REPEAT)], capture_output=True,text=True,check=True)

times = [float(line) for line in result.stdout.splitlines() if line.strip()]
times.sort()

# Statistics
n = len(times)
tmin = times[0]
tmax = times[-1]
q2 = median(times)
q1 = median(times[:n // 2])
q3 = median(times[(n + 1) // 2:])

wcet = tmax
C1 = math.ceil(wcet)

print("=== Benchmark tau1 ===")
print("Min  =", tmin)
print("Q1   =", q1)
print("Q2   =", q2)
print("Q3   =", q3)
print("Max  =", tmax)
print("WCET =", wcet)
print("C1   =", C1)

# Tasks : (name, C, T)
tasks = [
    ("tau1", C1, 10),
    ("tau2", 3, 10),
    ("tau3", 2, 20),
    ("tau4", 2, 20),
    ("tau5", 2, 40),
    ("tau6", 2, 40),
    ("tau7", 3, 80),
]

# Schedulability test with U = C/T on every tasks
U = sum(C / T for name, C, T in tasks)

print("\n=== Schedulability test ===")
print("U =", U)
print("U <= 1 :", "YES" if U <= 1 else "NO")

# 6) Hyperperiod
H = 80

# 7) Job dictionnary creation
jobs = []

for name, C, T in tasks:
    for k in range(H // T):
        release = k * T #End date
        deadline = release + T #Limit date

        jobs.append({
            "name": f"{name}_J{k + 1}",
            "C": C,
            "release": release,
            "deadline": deadline
        })

# 8) Non-Preemptive EDF Schedule
time = 0
waiting_total = 0
schedule = []
done_jobs = []

while jobs:
    available = [job for job in jobs if job["release"] <= time] #We get the jobs that have already been executed

    if not available:
        next_release = min(job["release"] for job in jobs)
        schedule.append(("IDLE", time, next_release))
        time = next_release
        continue

    job = min(available, key=lambda x: x["deadline"])   #Assignation of the job to do using the EDF planning

    start = time
    finish = start + job["C"] #Non-Preemptive, so the job always finish after the start + C

    waiting_total += start - job["release"]

    job["start"] = start
    job["finish"] = finish
    job["response"] = finish - job["release"]
    job["ok"] = finish <= job["deadline"]

    schedule.append((job["name"], start, finish))

    done_jobs.append(job) # In order to stock the jobs and their assigned datas to print the response time
    jobs.remove(job)
    time = finish

# Schedule printing
print("\n=== Schedule ===")
for name, start, finish in schedule:
    print(f"{name:10s} [{start:2d}, {finish:2d})")

print("\n=== Response times ===")
print("Total waiting time =", waiting_total)
for job in done_jobs:
    status = "OK" if job["ok"] else "MISS"
    D = job["deadline"] - job["release"]

    print(
        f"{job['name']:8s} "
        f"R={job['response']:2d} "
        f"D={D:2d} "
        f"finish={job['finish']:2d} "
        f"deadline={job['deadline']:2d} "
        f"-> {status}"
    )

#%%

# Second planning but tau5 can miss its deadline, its the same schedule but with a different constraint.

jobs_tau5 = []

for task_name, C, T in tasks:                   # New initialization
    for k in range(H // T):
        release = k * T
        deadline = release + T

        jobs_tau5.append({
            "name": f"{task_name}_J{k + 1}",
            "task": task_name,
            "C": C,
            "release": release,
            "deadline": deadline
        })

time = 0
waiting_total_tau5 = 0
schedule_tau5 = []
done_jobs_tau5 = []

while jobs_tau5:
    available = [job for job in jobs_tau5 if job["release"] <= time]

    if not available:
        next_release = min(job["release"] for job in jobs_tau5)
        schedule_tau5.append(("IDLE", time, next_release))
        time = next_release
        continue
        
    job = min(available,key=lambda x: (x["deadline"] + (20 if x["task"] == "tau5" else 0),x["C"])) #Penalty if the task is tau5

    start = time
    finish = start + job["C"]

    waiting_total_tau5 += start - job["release"]

    job["start"] = start
    job["finish"] = finish
    job["response"] = finish - job["release"]
    job["ok"] = finish <= job["deadline"]

    schedule_tau5.append((job["name"], start, finish))
    done_jobs_tau5.append(job)

    jobs_tau5.remove(job) # Same as the first EDF, we remove in order to not stack every tasks.
    time = finish

feasible_except_tau5 = True

for job in done_jobs_tau5:
    if job["task"] != "tau5" and job["ok"] == False:
        feasible_except_tau5 = False

print("\n=== Schedule where tau5 may miss deadline ===")
print("Feasible for all tasks except tau5:", "YES" if feasible_except_tau5 else "NO")
print("Total waiting time =", waiting_total_tau5)

for name, start, finish in schedule_tau5:
    print(f"{name:10s} [{start:2d}, {finish:2d})")

print("\n=== Response times with tau5 relaxed ===")

for job in done_jobs_tau5:
    status = "OK" if job["ok"] else "MISS"
    D = job["deadline"] - job["release"]

    print(
        f"{job['name']:8s} "
        f"R={job['response']:2d} "
        f"D={D:2d} "
        f"finish={job['finish']:2d} "
        f"deadline={job['deadline']:2d} "
        f"-> {status}"
    )