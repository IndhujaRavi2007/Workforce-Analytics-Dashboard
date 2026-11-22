import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(42)
RAW = Path(__file__).resolve().parent.parent / "data_raw"

emp = pd.read_csv(RAW / "employee.csv", parse_dates=["hire_date", "termination_date"])

# ---------- 1. Employee-level setup ----------
emp["shift_id"] = rng.choice([1, 2, 3], len(emp), p=[.25, .60, .15])   # 1 Morning, 2 General, 3 Night
coords = {"Chennai": (13.0827, 80.2707), "Bengaluru": (12.9716, 77.5946),
          "Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090)}
emp["office_lat"] = emp.location.map(lambda c: coords[c][0])
emp["office_lon"] = emp.location.map(lambda c: coords[c][1])
start_hour = {1: 6, 2: 9, 3: 21}

# ---------- 2. Shift roster (through 6 weeks into the future) ----------
TODAY = pd.Timestamp("2026-11-05")
dates = pd.DataFrame({"date": pd.bdate_range("2025-01-01", "2026-12-17")})
roster = emp[["emp_id", "shift_id", "hire_date", "termination_date"]].merge(dates, how="cross")
roster = roster[(roster.date >= roster.hire_date) &
                (roster.termination_date.isna() | (roster.date <= roster.termination_date))].copy()

n = len(roster)
requested = rng.random(n) < 0.03
future = (roster.date > TODAY).to_numpy()
approved = rng.random(n) < 0.75
roster["swap_status"] = np.where(~requested, "None",
                         np.where(future, "Pending", np.where(approved, "Approved", "Rejected")))
roster["is_swapped"] = (roster.swap_status == "Approved").astype(int)
roster["shift_id"] = np.where(roster.is_swapped == 1, (roster.shift_id % 3) + 1, roster.shift_id)

roster[["date", "emp_id", "shift_id", "is_swapped", "swap_status"]].rename(
    columns={"date": "roster_date"}).to_csv(RAW / "shift_roster.csv", index=False)
print("shift_roster.csv:", n, "rows")

# ---------- 3. Attendance (only up to today) ----------
att = roster[roster.date <= TODAY].merge(
    emp[["emp_id", "overtime_flag", "job_satisfaction", "office_lat", "office_lon"]], on="emp_id")
n = len(att)
dow = att.date.dt.dayofweek.to_numpy()
night = (att.shift_id == 3).to_numpy()
ot_yes = (att.overtime_flag == "Yes").to_numpy()

# status: Monday/Friday spike, low job satisfaction -> more absence
p_abs = 0.03 + 0.03 * np.isin(dow, [0, 4]) + att.job_satisfaction.map({1: .03, 2: .015, 3: 0, 4: 0}).to_numpy()
u_abs, u = rng.random(n), rng.random(n)
att["status"] = np.select([u_abs < p_abs, u < 0.07, u < 0.16], ["Absent", "Leave", "WFH"], "Present")
present = (att.status == "Present").to_numpy()
works = att.status.isin(["Present", "WFH"]).to_numpy()

# late minutes: night shift is later
late = np.clip(rng.normal(np.where(night, 20, 5), 12), 0, None).astype(int)
late = np.where(present, late, 0)

# worked hours: overtime employees and night shift work longer
hours = np.clip(rng.normal(8.1, 0.8, n) + 1.3 * ot_yes + 0.7 * night, 4, 14)
extreme = present & (rng.random(n) < 0.005)             # planted anomaly: >12 hours
hours = np.where(extreme, rng.uniform(12.5, 15, n), hours)

# check-in / check-out timestamps
start = att.date + pd.to_timedelta(att.shift_id.map(start_hour), unit="h")
check_in = start + pd.to_timedelta(late, unit="m")
check_out = check_in + pd.to_timedelta(hours, unit="h")
fmt = "%Y-%m-%d %H:%M:%S"
att["check_in"] = np.where(works, check_in.dt.strftime(fmt), None)
att["check_out"] = np.where(works, check_out.dt.strftime(fmt), None)

# method: WFH uses GPS; QR has the most anomalies
att["method_id"] = rng.choice([1, 2, 3, 4], n, p=[.35, .25, .15, .25])
att.loc[att.status == "WFH", "method_id"] = 3

# GPS with location-mismatch anomalies
p_mis = att.method_id.map({1: .002, 2: .002, 3: .01, 4: .03}).to_numpy()
mismatch = present & (rng.random(n) < p_mis)
jump = rng.uniform(0.3, 0.8, n) * rng.choice([-1, 1], n)
att["gps_lat"] = np.where(works, att.office_lat + rng.normal(0, 0.002, n) + mismatch * jump, np.nan).round(5)
att["gps_long"] = np.where(works, att.office_lon + rng.normal(0, 0.002, n) + mismatch * jump, np.nan).round(5)

# ---------- 4. Dirty data on purpose (for the ETL to clean) ----------
wfh_idx = att[att.status == "WFH"].sample(frac=0.4, random_state=1).index
att.loc[wfh_idx, "status"] = "Work From Home"
miss_idx = att[att.status == "Present"].sample(frac=0.005, random_state=2).index
att.loc[miss_idx, "check_out"] = None
dups = att.sample(frac=0.005, random_state=3)

out = pd.concat([att, dups])[["emp_id", "date", "shift_id", "method_id", "check_in",
                              "check_out", "status", "gps_lat", "gps_long"]]
out = out.rename(columns={"date": "att_date"})
out.to_csv(RAW / "attendance.csv", index=False)

# ---------- 5. Pattern checks ----------
print("attendance.csv:", len(out), "rows")
chk = att.assign(dow=att.date.dt.day_name(), late=late)
print("\nAbsent by weekday:\n", chk[chk.status == "Absent"].groupby("dow").size())
print("\nAvg late minutes by shift:\n", chk[chk.status == "Present"].groupby("shift_id").late.mean().round(1))
print("\nGPS mismatches by method:\n", pd.Series(mismatch).groupby(att.method_id.to_numpy()).sum())