import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data_raw"

# Departments
pd.DataFrame({
    "dept_id": range(1, 8),
    "dept_name": ["Sales", "Engineering", "HR", "Finance", "Operations", "Support", "Marketing"],
    "cost_center": [f"CC{100 + i}" for i in range(7)],
}).to_csv(RAW / "department.csv", index=False)

# Locations
pd.DataFrame({
    "location_id": [1, 2, 3, 4],
    "city": ["Chennai", "Bengaluru", "Mumbai", "Delhi"],
    "country": "India",
    "latitude": [13.0827, 12.9716, 19.0760, 28.6139],
    "longitude": [80.2707, 77.5946, 72.8777, 77.2090],
}).to_csv(RAW / "location.csv", index=False)

# Shifts
pd.DataFrame({
    "shift_id": [1, 2, 3],
    "shift_name": ["Morning", "General", "Night"],
    "start_time": ["06:00", "09:00", "21:00"],
    "end_time": ["14:00", "17:00", "05:00"],
    "shift_type": ["Rotational", "Fixed", "Night"],
    "planned_hours": [8, 8, 8],
}).to_csv(RAW / "shift.csv", index=False)

# Check-in methods
pd.DataFrame({
    "method_id": [1, 2, 3, 4],
    "method_name": ["Biometric", "Face", "GPS", "QR"],
}).to_csv(RAW / "checkin_method.csv", index=False)

# Leave types
pd.DataFrame({
    "leave_type_id": [1, 2, 3, 4],
    "leave_type": ["Casual", "Sick", "Earned", "Maternity"],
    "annual_quota": [12, 10, 15, 90],
    "is_paid": [1, 1, 1, 1],
}).to_csv(RAW / "leave_type.csv", index=False)

# Clients and projects
pd.DataFrame({
    "client_id": range(1, 9),
    "client_name": [f"Client {c}" for c in "ABCDEFGH"],
    "industry": ["Banking", "Retail", "Telecom", "Healthcare", "Insurance",
                 "Manufacturing", "Logistics", "Energy"],
}).to_csv(RAW / "client.csv", index=False)

pd.DataFrame({
    "project_id": range(1, 26),
    "project_name": [f"Project {i:02d}" for i in range(1, 26)],
    "client_id": [(i % 8) + 1 for i in range(25)],
    "billing_rate": [1500 + (i % 6) * 250 for i in range(25)],
}).to_csv(RAW / "project.csv", index=False)

# Skills
skills = ["Python", "SQL", "Excel", "Power BI", "Communication", "Leadership",
          "Project Management", "Sales Negotiation", "Recruitment", "Accounting",
          "Customer Support", "Digital Marketing", "Data Analysis", "Cloud", "Compliance"]
cats = ["Technical", "Technical", "Technical", "Technical", "Soft", "Soft",
        "Soft", "Business", "Business", "Business", "Business", "Business",
        "Technical", "Technical", "Business"]
pd.DataFrame({"skill_id": range(1, 16), "skill_name": skills, "category": cats}
            ).to_csv(RAW / "skill.csv", index=False)

print("Master data files written to", RAW)