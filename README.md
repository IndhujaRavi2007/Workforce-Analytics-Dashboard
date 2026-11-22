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

# Technology                                            Purpose 
  Power BI                               Interactive dashboards and data visualization
  MySQL                                           Database management
  SQL                                      Data querying and transformation
  DAX                                   KPI calculations and analytical measures

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
Workforce Management Analytics System/
|
|__.vscode
|     |__settings.json
|__data_raw
|      |__attendance.csv
|      |__checkin_method.csv
|      |__client.csv
|      |__department.csv
|      |__employee_skill.csv
|      |__employee.csv
|      |__exit.csv
|      |__leave_request.csv
|      |__leave_type.csv
|      |__location.csv
|      |__payroll.csv
|      |__performance.csv
|      |__project.csv
|      |__shift_roster.csv
|      |__shift.csv
|      |__skill_requirement.csv
|      |__skill.csv
|      |__timesheet.csv
|      |__training.csv
|      |__WA_Fn__UseC-HR-Employee-Attrition.csv
|__PowerBI_Dashboards
|      |__Workforce Management Project.pbix
|__python
|      |__01_build_employees.py
|      |__02_master_data.py
|      |__03_generate_attendance.py
|      |__04_generate_leave_timesheet.py
|      |__05_generate_payroll_performance.py
|      |__06_load_staging.py
|      |__download_data.py
|__sql
|    |__01_create_database.sql
|    |__02_staging.checks.sql
|    |__03_core_table.sql
|    |__04_staging_to_core.sql
|    |__05_mart_table.sql
|    |__06_mart_to_core.sql
|__license
|__wfm_local2.session.sql

## Project Outcomes

* Developed interactive workforce dashboards for three user groups.
* Designed analytical KPIs using DAX.
* Used SQL and MySQL for workforce data management.
* Converted raw workforce data into actionable insights.
* Enabled data-driven HR and management analysis.

## License
This project is licensed under the MIT License.

