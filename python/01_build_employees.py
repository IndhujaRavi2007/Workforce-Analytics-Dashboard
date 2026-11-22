import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data_raw"

ibm = pd.read_csv(RAW / "WA_Fn-UseC_-HR-Employee-Attrition.csv")
print("IBM shape:", ibm.shape)

# ---------- 1. Map to 7 departments ----------
def map_dept(row):
    if row["Department"] == "Sales":
        return "Sales"
    if row["Department"] == "Human Resources":
        return "HR"
    role = row["JobRole"]
    if role in ("Research Scientist", "Laboratory Technician"):
        return "Engineering"
    if role in ("Manufacturing Director", "Healthcare Representative"):
        return "Operations"
    return "Support"

ibm["dept_name"] = ibm.apply(map_dept, axis=1)
sales_idx = ibm[ibm.dept_name == "Sales"].sample(frac=0.3, random_state=1).index
ibm.loc[sales_idx, "dept_name"] = "Marketing"
hr_idx = ibm[ibm.dept_name == "HR"].sample(frac=0.4, random_state=2).index
ibm.loc[hr_idx, "dept_name"] = "Finance"

# ---------- 2. Core employee table ----------
emp = pd.DataFrame({
    "emp_id": ibm["EmployeeNumber"],
    "name": [f"Employee {i}" for i in ibm["EmployeeNumber"]],
    "gender": ibm["Gender"].str[0],
    "age": ibm["Age"],
    "dept_name": ibm["dept_name"],
    "job_role": ibm["JobRole"],
    "job_level": ibm["JobLevel"],
    "salary": ibm["MonthlyIncome"] * 12,
    "overtime_flag": ibm["OverTime"],
    "distance_from_home": ibm["DistanceFromHome"],
    "years_at_company": ibm["YearsAtCompany"],
    "years_since_promotion": ibm["YearsSinceLastPromotion"],
    "job_satisfaction": ibm["JobSatisfaction"],
    "performance_rating": ibm["PerformanceRating"],
    "left_company": ibm["Attrition"].eq("Yes").astype(int),
})

# ---------- 3. Added columns ----------
emp["email"] = [f"emp{i}@company.com" for i in emp.emp_id]
emp["location"] = np.random.choice(["Chennai", "Bengaluru", "Mumbai", "Delhi"],
                                   len(emp), p=[.35, .30, .20, .15])
emp["employment_type"] = np.random.choice(["Full-time", "Contract", "Vendor"],
                                          len(emp), p=[.82, .13, .05])
emp["vendor_name"] = np.where(
    emp.employment_type == "Vendor",
    np.random.choice(["TeamLease", "Randstad", "Adecco"], len(emp)), None)

ref = pd.Timestamp("2026-11-05")
emp["hire_date"] = [ref - pd.Timedelta(days=int(y * 365 + np.random.randint(0, 300)))
                    for y in emp.years_at_company]
emp["hire_date"] = pd.to_datetime(emp["hire_date"]).dt.date

exit_dates = pd.to_datetime("2025-01-15") + pd.to_timedelta(
    np.random.randint(0, 650, len(emp)), unit="D")
emp["termination_date"] = np.where(emp.left_company == 1, exit_dates.date, None)
emp["status"] = np.where(emp.left_company == 1, "Terminated", "Active")

# ---------- 4. Manager hierarchy ----------
emp = emp.sort_values(["job_level", "years_at_company"], ascending=False).reset_index(drop=True)
ids = emp.emp_id.tolist()
ceo = ids[0]
heads = ids[1:9]
managers = ids[9:55]
manager_map = {}
for h in heads:
    manager_map[h] = ceo
for m in managers:
    manager_map[m] = int(np.random.choice(heads))
for e in ids[55:]:
    manager_map[e] = int(np.random.choice(managers))
emp["manager_id"] = emp.emp_id.map(manager_map)
emp["manager_id"] = emp["manager_id"].astype("Int64")

emp = emp.sort_values("emp_id").reset_index(drop=True)
emp.to_csv(RAW / "employee.csv", index=False)

print("employee.csv written:", emp.shape)
print(emp.dept_name.value_counts())
print("Leavers:", emp.left_company.sum())