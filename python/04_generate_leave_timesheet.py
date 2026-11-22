import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(7)
RAW = Path(__file__).resolve().parent.parent / "data_raw"
TODAY = pd.Timestamp("2026-11-05")

att = pd.read_csv(RAW / "attendance.csv", usecols=["emp_id", "att_date", "status"],
                  parse_dates=["att_date"]).drop_duplicates(["emp_id", "att_date"])
emp = pd.read_csv(RAW / "employee.csv", usecols=["emp_id", "dept_name", "left_company"])

# =====================================================
# PART 1: LEAVE REQUESTS
# =====================================================
# Group consecutive "Leave" days of one employee into a single request
lv = att[att.status == "Leave"].sort_values(["emp_id", "att_date"]).copy()
prev = lv.groupby("emp_id").att_date.shift().fillna(lv.att_date - pd.Timedelta(days=10))
gap = np.busday_count(prev.values.astype("datetime64[D]"),
                      lv.att_date.values.astype("datetime64[D]"))
lv["grp"] = (gap != 1).cumsum()

req = lv.groupby("grp").agg(emp_id=("emp_id", "first"),
                            start_date=("att_date", "min"),
                            end_date=("att_date", "max"),
                            days=("att_date", "size")).reset_index(drop=True)
n = len(req)
req["leave_type_id"] = rng.choice([1, 2, 3], n, p=[.35, .40, .25])   # Casual, Sick, Earned
sick = (req.leave_type_id == 2).to_numpy()
lead = np.where(sick, rng.integers(0, 2, n), rng.integers(1, 15, n))
req["request_date"] = req.start_date - pd.to_timedelta(lead, unit="D")
lag = np.where(sick, rng.integers(0, 3, n), rng.integers(0, 5, n))
req["approval_date"] = req.request_date + pd.to_timedelta(lag, unit="D")
req["status"] = "Approved"

def bday(dt_array):
    return np.busday_offset(dt_array.astype("datetime64[D]"), 0, roll="forward")

# Future requests: Pending (for the manager approval page)
active = emp[emp.left_company == 0].emp_id.sample(80, random_state=5).to_numpy()
st = bday((TODAY + pd.to_timedelta(rng.integers(3, 40, 80), unit="D")).values)
dd = rng.integers(1, 4, 80)
en = np.busday_offset(st, dd - 1)
pend = pd.DataFrame({"emp_id": active, "start_date": pd.to_datetime(st),
                     "end_date": pd.to_datetime(en), "days": dd,
                     "leave_type_id": rng.choice([1, 3], 80, p=[.6, .4]),
                     "request_date": TODAY - pd.to_timedelta(rng.integers(0, 7, 80), unit="D"),
                     "approval_date": pd.NaT, "status": "Pending"})

# Past requests that were rejected
rej_emp = emp.emp_id.sample(40, random_state=6).to_numpy()
rs = bday(pd.to_datetime("2025-03-01") + pd.to_timedelta(rng.integers(0, 570, 40), unit="D").values)
rd = rng.integers(1, 4, 40)
rej = pd.DataFrame({"emp_id": rej_emp, "start_date": pd.to_datetime(rs),
                    "end_date": pd.to_datetime(np.busday_offset(rs, rd - 1)), "days": rd,
                    "leave_type_id": rng.choice([1, 3], 40),
                    "status": "Rejected"})
rej["request_date"] = rej.start_date - pd.to_timedelta(rng.integers(2, 10, 40), unit="D")
rej["approval_date"] = rej.request_date + pd.to_timedelta(rng.integers(1, 4, 40), unit="D")

leave = pd.concat([req, pend, rej], ignore_index=True).sort_values("start_date").reset_index(drop=True)
leave.insert(0, "leave_id", range(1, len(leave) + 1))
leave = leave[["leave_id", "emp_id", "leave_type_id", "start_date", "end_date",
               "days", "status", "request_date", "approval_date"]]
leave.to_csv(RAW / "leave_request.csv", index=False)

# =====================================================
# PART 2: TIMESHEETS
# =====================================================
# HR and Finance do internal work, so they are not on client projects
elig = emp[~emp.dept_name.isin(["HR", "Finance"])].emp_id.to_numpy()
m = len(elig)

# Employee profiles: 8% bench, 7% over-allocated, rest normal
r = rng.random(m)
prof = pd.DataFrame({"emp_id": elig,
                     "mu": np.select([r < .08, r > .93], [5.0, 9.8], 8.0),
                     "p_bill": np.select([r < .08, r > .93], [.15, .90], .85)})

# Project assignment: everyone has a main project, 40% also have a second one
p1 = rng.integers(1, 26, m)
p2 = rng.integers(1, 26, m)
p2 = np.where(p2 == p1, (p2 % 25) + 1, p2)
has2 = rng.random(m) < 0.4
assign = pd.concat([
    pd.DataFrame({"emp_id": elig, "project_id": p1, "share": np.where(has2, .7, 1.0)}),
    pd.DataFrame({"emp_id": elig[has2], "project_id": p2[has2], "share": .3}),
])

work = att[att.status.isin(["Present", "WFH", "Work From Home"]) &
           att.emp_id.isin(elig)].merge(prof, on="emp_id")
work["total_h"] = np.clip(rng.normal(work.mu, 0.5), 1, 12)

ts = work.merge(assign, on="emp_id")
ts["hours_logged"] = np.maximum(np.round(ts.total_h * ts.share * 4) / 4, 0.25)
ts["is_billable"] = (rng.random(len(ts)) < ts.p_bill).astype(int)

age = (TODAY - ts.att_date).dt.days.to_numpy()
u = rng.random(len(ts))
ts["approval_status"] = np.where(age > 14, np.where(u < .98, "Approved", "Rejected"),
                                 np.where(u < .5, "Approved", "Pending"))

ts = ts.rename(columns={"att_date": "ts_date"})[
    ["emp_id", "ts_date", "project_id", "hours_logged", "is_billable", "approval_status"]]
ts.to_csv(RAW / "timesheet.csv", index=False)

# =====================================================
# PATTERN CHECKS
# =====================================================
print("leave_request.csv:", len(leave), "rows")
print(leave.status.value_counts().to_string())
print("\nLeave requests by type (1 Casual, 2 Sick, 3 Earned):")
print(leave.leave_type_id.value_counts().sort_index().to_string())
print("Avg days per request:", round(leave.days.mean(), 2))

print("\ntimesheet.csv:", len(ts), "rows")
util = ts.groupby("emp_id").apply(lambda g: (g.hours_logged * g.is_billable).sum() / g.hours_logged.sum())
print("Employees with utilization < 40% (bench):", int((util < .4).sum()), "of", len(util))
print("Overall utilization:", round(float(util.mean()), 2))