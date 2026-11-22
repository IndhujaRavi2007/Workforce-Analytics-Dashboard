-------------mart_tables is used for "Building empty star schema" which contains "10 dimension and 9 fact tables"----------------------

use wfm_mart;

drop table if exists wfm_mart.fact_attendance,
wfm_mart.fact_training,
wfm_mart.fact_timesheet,
wfm_mart.fact_shift_roster,
wfm_mart.fact_performance,
wfm_mart.fact_payroll,
wfm_mart.fact_leave_request,
wfm_mart.fact_attrition,
wfm_mart.fact_employee_skill,
wfm_mart.dim_checkin_method,
wfm_mart.dim_client,
wfm_mart.dim_department,
wfm_mart.dim_leave_type,
wfm_mart.dim_location,
wfm_mart.dim_shift,
wfm_mart.dim_skill,
wfm_mart.dim_project,
wfm_mart.dim_employee,
wfm_mart.dim_date;

------------------------DIMENSION TABLES--------------------------
create table wfm_mart.dim_department(
    dept_key int primary key,
    dept_name varchar(50),
    cost_center varchar(20)
);

create table wfm_mart.dim_location(
    location_key int primary key,
    city varchar(20),
    country varchar(20),
    latitude decimal(9,6),
    longitude decimal(9,6)
);

create table wfm_mart.dim_shift(
    shift_key int primary key,
    shift_name varchar(30),
    start_time time,
    end_time time,
    shift_type varchar(30),
    planned_hours varchar(30)
);

create table wfm_mart.dim_checkin_method(
    method_key int primary key,
    method_name varchar(30)
);

create table wfm_mart.dim_leave_type(
    leave_type_id int primary key,
    leave_type varchar(20),
    annual_quota int,
    is_paid int
);

create table wfm_mart.dim_client(
    client_key int primary key,
    client_name varchar(30),
    industry varchar(30)
);

create table wfm_mart.dim_project(
    project_key int primary key,
    project_name varchar(20),
    client_key int ,
    billing_rate decimal(10,2)
);

create table wfm_mart.dim_skill(
    skill_key int primary key,
    skill_name varchar(30),
    category varchar(30)
);

create table wfm_mart.dim_employee(
    emp_key int primary key,
    emp_id int ,
    name varchar(30),
    gender varchar(20),
    age int ,
    dept_key int,
    dept_name varchar(20),
    job_role  varchar(20),
    job_level int ,
    salary int ,
    overtime_flag varchar(10),
    distance_from_home int ,
    years_at_company int ,
    years_since_promotion int ,
    job_satisfaction int,
    performance_rating int ,
    left_company int ,
    email varchar(20),
    location varchar(20),
    location_key int,
    employment_type varchar(20),
    vendor_name varchar(20),
    hire_date date ,
    termination_date date ,
    status varchar(30),
    manager_id int 
);

create table wfm_mart.dim_date(
    date_key int primary key, 
    date DATE,
    year int,
    quarter int,
    month_no int,
    month_name varchar(20),
    year_month_txt char(7),
    week_no int,
    day_name varchar(10),
    day_no int,
    is_weekend tinyint
);

-------------------FACT TABLES---------------------
create table wfm_mart.fact_attendance(
    date_key int,
    emp_key int,
    shift_key int,
    method_key int ,
    status varchar(20),
    late_minutes int,
    worked_hours decimal(5,2),
    overtime_hours decimal(5,2),
    overtime_cost decimal(12,2),
    gps_lat decimal(9,6),
    gps_long decimal(9,6),
    anomaly_flag tinyint default 0
);

create table wfm_mart.fact_shift_roster(
    date_key int,emp_key int ,emp_id int ,shift_id int ,is_swapped int ,swap_status varchar(10)
);

create table wfm_mart.fact_leave_request(
    leave_key int ,emp_key int ,leave_type_key int ,start_date date,end_date date,
    days int ,status varchar(20),request_date date,approval_date date
);

create table wfm_mart.fact_timesheet(
    emp_key int ,ts_date date,project_key int ,hours_logged decimal(10,2),is_billable int ,approval_status varchar(20)
);

create table wfm_mart.fact_payroll(
    emp_key int,pay_month date,basic_pay decimal(10,2),overtime_pay decimal(10,2),
    leave_deduction decimal(15,3),bonus decimal(15,3),incentive decimal(15,3),net_pay decimal(15,3)
);

create table wfm_mart.fact_performance(
    emp_key int,quarter_start date,kpi_score decimal(5,2),
    goal_completion_pct decimal(5,2),productivity_score decimal(10,2),
    rating int ,potential_score decimal(10,2),sentiment_score decimal(10,2)
);

create table wfm_mart.fact_attrition(
    emp_key int,exit_date date,exit_reason varchar(90),is_voluntary tinyint,
    is_regretted tinyint,tenure_months int ,replacement_cost decimal(10,3)
);

create table wfm_mart.fact_employee_skill(
    emp_key int,skill_key int,proficiency_level int
);

create table wfm_mart.fact_training(
    emp_key int ,course_name varchar(30),completion_date date,hours int
);

select table_name from information_schema.tables where table_schema='wfm_mart' order by 1;