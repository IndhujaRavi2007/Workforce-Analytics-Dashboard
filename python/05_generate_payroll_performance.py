import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(11)
RAW = Path(__file__).resolve().parent.parent / "data_raw"
TODAY = pd.Timestamp("2026-11-05")

emp = pd.read_csv(RAW / "employee.csv", parse_dates=["hire_date", "termination_date"])
dept_id = {"Sales": 1, "Engineering": 2, "HR": 3, "Finance": 4,
           "Operations": 5, "Support": 6, "Marketing": 7}

# =====================================================
# PART 1: PAYROLL (employee x month)
# =====================================================
att = pd.read_csv(RAW / "attendance.csv",
                  usecols=["emp_id", "att_date", "check_in", "check_out", "status"],
                  parse_dates=["att_date", "check_in", "check_out"]
                  ).drop_duplicates(["emp_id", "att_date"])
worked = (att.check_out - att.check_in).dt.total_seconds() / 3600
att["ot"] = (worked - 8).clip(lower=0).fillna(0)
att["absent"] = (att.status == "Absent").astype(int)
att["month"] = att.att_date.dt.to_period("M").dt.to_timestamp()
monthly = att.groupby(["emp_id", "month"]).agg(
    ot_hours=("ot", "sum"), absent_days=("absent", "sum")).reset_index()

months = pd.DataFrame({"month": pd.date_range("2025-01-01", "2026-10-01", freq="MS")})
pay = emp[["emp_id", "salary", "hire_date", "termination_date",
           "dept_name", "performance_rating"]].merge(months, how="cross")
pay["month_end"] = pay.month + pd.offsets.MonthEnd(0)

# prorate the joining / leaving month
start = pay.hire_date.where(pay.hire_date > pay.month, pay.month)
term = pay.termination_date.fillna(pay.month_end)
end = term.where(term < pay.month_end, pay.month_end)
pay["frac"] = ((end - start).dt.days + 1) / pay.month.dt.days_in_month
pay = pay[pay.frac > 0].merge(monthly, on=["emp_id", "month"], how="left").fillna(
    {"ot_hours": 0, "absent_days": 0})

pay["basic_pay"] = (pay.salary / 12 * pay.frac).round(2)
pay["overtime_pay"] = (pay.ot_hours * pay.salary / 2080 * 1.5).round(2)   # same formula as the DAX/SQL overtime cost
pay["leave_deduction"] = (pay.absent_days * pay.salary / 12 / 22).round(2)  # loss of pay for absences
pct = np.where(pay.performance_rating == 4, 0.05, 0.025)
pay["bonus"] = np.where(pay.month.dt.month == 3, pay.salary * pct, 0).round(2)  # annual bonus in March
sales = pay.dept_name.isin(["Sales", "Marketing"]).to_numpy()
has_inc = sales & (rng.random(len(pay)) < 0.7)
pay["incentive"] = np.where(has_inc, pay.basic_pay * rng.uniform(0.02, 0.15, len(pay)), 0).round(2)
pay["net_pay"] = (pay.basic_pay + pay.overtime_pay + pay.bonus
                  + pay.incentive - pay.leave_deduction).round(2)

payroll = pay.rename(columns={"month": "pay_month"})[
    ["emp_id", "pay_month", "basic_pay", "overtime_pay", "leave_deduction",
     "bonus", "incentive", "net_pay"]]
payroll.to_csv(RAW / "payroll.csv", index=False)

# =====================================================
# PART 2: PERFORMANCE (employee x quarter)
# =====================================================
qs = pd.DataFrame({"quarter_start": pd.date_range("2025-01-01", "2026-07-01", freq="QS")})
perf = emp.merge(qs, how="cross")
perf["qend"] = perf.quarter_start + pd.DateOffset(months=3) - pd.Timedelta(days=1)
perf = perf[(perf.hire_date <= perf.qend) &
            (perf.termination_date.isna() | (perf.termination_date >= perf.quarter_start))].copy()
n = len(perf)

ot_yes = (perf.overtime_flag == "Yes").to_numpy()
leaving = (perf.termination_date.notna() &
           ((perf.termination_date - perf.quarter_start).dt.days < 180)).to_numpy()
base = np.where(perf.performance_rating == 4, 78, 66)
kpi = np.clip(base + 3 * (perf.job_satisfaction - 2.5) - 4 * ot_yes
              - 6 * leaving + rng.normal(0, 6, n), 20, 100)
goal = np.clip(kpi + rng.normal(0, 8, n), 10, 100)
prod = np.clip(0.5 * kpi + 0.5 * goal - 3 * ot_yes + rng.normal(0, 4, n), 10, 100)
potential = np.clip(0.5 * kpi + 15 - 0.4 * (perf.age - 30) + rng.normal(0, 10, n), 0, 100)
sentiment = np.clip(1.5 + 0.7 * perf.job_satisfaction - 0.5 * ot_yes
                    - 0.6 * leaving + rng.normal(0, 0.4, n), 1, 5)

perf["kpi_score"] = kpi.round(1)
perf["goal_completion_pct"] = goal.round(1)
perf["productivity_score"] = prod.round(1)
perf["rating"] = pd.cut(kpi, [0, 40, 55, 70, 85, 100.01], labels=False) + 1
perf["potential_score"] = potential.round(1)
perf["sentiment_score"] = sentiment.round(2)
perf[["emp_id", "quarter_start", "kpi_score", "goal_completion_pct", "productivity_score",
      "rating", "potential_score", "sentiment_score"]].to_csv(RAW / "performance.csv", index=False)

# =====================================================
# PART 3: EXITS
# =====================================================
lv = emp[emp.left_company == 1].copy()
low_sal = emp.salary.quantile(0.33)
voluntary_map = {"Better Compensation": 1, "Work-Life Balance": 1, "Career Growth": 1,
                 "Long Commute": 1, "Manager Issues": 1, "Relocation": 1,
                 "Personal Reasons": 1, "Performance Termination": 0,
                 "Layoff / Restructuring": 0}
reasons = []
for r in lv.itertuples():
    w = {"Better Compensation": 1 + 4 * (r.salary <= low_sal),
         "Work-Life Balance": 1 + 4 * (r.overtime_flag == "Yes"),
         "Career Growth": 1 + 3 * (r.years_since_promotion >= 4),
         "Long Commute": 0.5 + 3 * (r.distance_from_home > 20),
         "Manager Issues": 1, "Relocation": 1, "Personal Reasons": 1,
         "Performance Termination": 0.5 + (r.performance_rating == 3),
         "Layoff / Restructuring": 0.5}
    p = np.array(list(w.values()), dtype=float)
    reasons.append(rng.choice(list(w.keys()), p=p / p.sum()))
lv["exit_reason"] = reasons
lv["is_voluntary"] = lv.exit_reason.map(voluntary_map)
lv["is_regretted"] = ((lv.is_voluntary == 1) &
                      ((lv.performance_rating == 4) | (lv.job_level >= 3))).astype(int)
lv["tenure_months"] = ((lv.termination_date - lv.hire_date).dt.days / 30.4).round().clip(lower=0).astype(int)
lv["replacement_cost"] = (lv.salary * 0.5).round(2)
lv = lv.rename(columns={"termination_date": "exit_date"})
lv[["emp_id", "exit_date", "exit_reason", "is_voluntary", "is_regretted",
    "tenure_months", "replacement_cost"]].to_csv(RAW / "exit.csv", index=False)

# =====================================================
# PART 4: SKILLS (+ requirements per department)
# =====================================================
dept_skills = {"Sales": [8, 5, 11, 3, 6], "Engineering": [1, 2, 14, 13, 7],
               "HR": [9, 5, 15, 6, 3], "Finance": [10, 3, 15, 2, 13],
               "Operations": [7, 3, 13, 6, 15], "Support": [11, 5, 2, 3, 7],
               "Marketing": [12, 5, 13, 4, 8]}
weak = {"Sales": 6, "Engineering": 14, "HR": 15, "Finance": 13,
        "Operations": 15, "Support": 2, "Marketing": 4}   # planted skill gap per department

req_rows = []
for d, sk in dept_skills.items():
    for i, s in enumerate(sk):
        req_rows.append((dept_id[d], s, 4 if i < 3 else 3))
pd.DataFrame(req_rows, columns=["dept_id", "skill_id", "required_level"]
             ).to_csv(RAW / "skill_requirement.csv", index=False)

rows = []
for r in emp[emp.left_company == 0].itertuples():
    core = dept_skills[r.dept_name]
    for s in core:
        if rng.random() < 0.92:
            mean = 3.1 + 0.2 * (r.job_level - 1) - (0.8 if s == weak[r.dept_name] else 0)
            rows.append((r.emp_id, s, int(np.clip(round(rng.normal(mean, 0.8)), 1, 5))))
    others = [s for s in range(1, 16) if s not in core]
    for s in rng.choice(others, 2, replace=False):
        rows.append((r.emp_id, int(s), int(np.clip(round(rng.normal(2.2, 0.8)), 1, 5))))
emp_skill = pd.DataFrame(rows, columns=["emp_id", "skill_id", "proficiency_level"])
emp_skill.to_csv(RAW / "employee_skill.csv", index=False)

# =====================================================
# PART 5: TRAINING
# =====================================================
courses = ["Leadership Basics", "Advanced Excel", "Data Analytics", "Communication Skills",
           "Compliance Essentials", "Cloud Fundamentals", "Customer Handling", "Project Management"]
act = emp[emp.left_company == 0]
cnt = rng.choice([0, 1, 2, 3], len(act), p=[.2, .35, .3, .15])
tr = act.loc[act.index.repeat(cnt), ["emp_id", "hire_date"]].reset_index(drop=True)
off = pd.to_timedelta(rng.integers(0, 674, len(tr)), unit="D")
tr["completion_date"] = np.maximum(pd.Timestamp("2025-01-01") + off, tr.hire_date)
tr["completion_date"] = tr.completion_date.where(tr.completion_date <= TODAY, TODAY)
tr["course_name"] = rng.choice(courses, len(tr))
tr["hours"] = rng.choice([4, 8, 12, 16, 24], len(tr))
tr[["emp_id", "course_name", "completion_date", "hours"]].to_csv(RAW / "training.csv", index=False)

# =====================================================
# PATTERN CHECKS
# =====================================================
print("payroll.csv:", len(payroll), "rows | total net pay:", round(payroll.net_pay.sum()))
print("performance.csv:", len(perf), "rows")
print("exit.csv:", len(lv), "rows")
print("employee_skill.csv:", len(emp_skill), "rows | training.csv:", len(tr), "rows")
print("\nAttrition rate by department:")
print(emp.groupby("dept_name").left_company.mean().round(3).sort_values(ascending=False).to_string())
print("\nExit reasons:\n", lv.exit_reason.value_counts().to_string())
print("\nLeavers hired AFTER their exit date:", int((lv.exit_date < lv.hire_date).sum()))
print("\nMarch vs February net pay (bonus spike):")
m = payroll.groupby("pay_month").net_pay.sum()
print(m.loc["2026-02-01"].round(), m.loc["2026-03-01"].round())