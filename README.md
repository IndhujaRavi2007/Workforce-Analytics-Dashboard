##  Workforce-Analytics-Dashboard
## Project Overview

The Workforce Management Analytics System is a data analytics project developed to transform workforce data into meaningful business insights using Power BI and MySQL.

The project provides interactive dashboards designed for HR professionals, managers, and employees to monitor workforce performance, attendance, productivity, employee engagement, and organizational health.

## Objectives

* Analyze overall workforce distribution and demographics.

* Monitor employee attendance, absenteeism, and late arrivals.

* Evaluate employee performance and productivity.

* Analyze recruitment and employee attrition.

* Monitor leave management, shifts, and overtime.

* Support data-driven workforce management decisions.
  
## Technologies Used

| Technology | Purpose |
| --- | --- |
| Power BI  | Interactive dashboards and data visualization |
|MySQL | Database management |
|SQL | Data querying and transformation |
|DAX  | KPI calculations and analytical measures |

## Dashboard Modules

1. HR Dashboard

Provides an overall view of workforce operations and organizational performance.

Key analysis:
* Executive Summary
* Workforce Analytics
* Attendance
* Leave and Shift Analysis
* Payroll and Cost
* Attrition Analysis
* Performance
* Contractor and Multi-location

2. Manager Dashboard

Helps managers monitor their teams and evaluate operational performance.

Key analysis:
* Team Today
* Team Attendance
* Leave and Approvals
* Shifts and Overtime
* Productivity and Utilization
* Resource Allocation

3. Employee Dashboard

Provides individual employees with insights into their work-related information.

Key analysis:
* My Overview
* My Attendance
* My Leave
* My Shifts
* My Payroll
* My performance and Development

## Database Design

MySQL is used to store and manage workforce-related information.

The database consists of:
    * Fact tables
    * Dimension tables
    * Workforce data models
    * SQL queries for analytical reporting

## Key Performance Indicators (KPIs)

The dashboards include workforce metrics such as:
* Active Employees
* Attrition Rate
* Average Performance
* Total Payroll
* Attendance Rate
* Total present
* Total absent
* Total leave request
* Pending leave request
* Rejected leave request
* Approved leave request
* Total payroll
* Total overtime pay
* Average net pay
* Total bonus
* Employee exits
* Voluntary exits
* Involuntary exits
* Regretted attrition
* Tensure rate
* High Performer
* KPI score
* Employment Satisfaction
* Performance score
* Goal completion percentage
* Total location and so on.........

## Project Files
<pre>
Workforce Management Analytics System/
|
├── .vscode
|      ├── settings.json
├──data_raw
|       ├── attendance.csv
|       ├── checkin_method.csv
|       ├── client.csv
|       ├── department.csv
|       ├── employee_skill.csv
|       ├── employee.csv
|       ├── exit.csv
|       ├── leave_request.csv
|       ├── leave_type.csv
|       ├── location.csv
|       ├── payroll.csv
|       ├── performance.csv
|       ├── project.csv
|       ├── shift_roster.csv
|       ├── shift.csv
|       ├── skill_requirement.csv
|       ├── skill.csv
|       ├── timesheet.csv
|       ├── training.csv
|       ├── WA_Fn__UseC-HR-Employee-Attrition.csv
├──PowerBI_Dashboards
|       ├── Workforce Management Project.pbix
├──python
|       ├── 01_build_employees.py
|       ├── 02_master_data.py
|       ├── 03_generate_attendance.py
|       ├── 04_generate_leave_timesheet.py
|       ├── 05_generate_payroll_performance.py
|       ├── 06_load_staging.py
|       ├── download_data.py
├── sql
|     ├── 01_create_database.sql
|     ├── 02_staging.checks.sql
|     ├── 03_core_table.sql
|     ├── 04_staging_to_core.sql
|     ├── 05_mart_table.sql
|     ├── 06_mart_to_core.sql
├── license
├── wfm_local2.session.sql
</pre>
## Project Outcomes

* Developed interactive workforce dashboards for three user groups.
* Designed analytical KPIs using DAX.
* Used SQL and MySQL for workforce data management.
* Converted raw workforce data into actionable insights.
* Enabled data-driven HR and management analysis.

## License
This project is licensed under the MIT License.

