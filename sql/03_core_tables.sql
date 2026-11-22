-----------------Build empty clean tables,22 typed tables with primary and foreign keys, plus error_log and etl_log--------------------------

use wfm_core;

drop table if exists attendance, checkin_method,client,department,employee_skill,employee,exist,
leave_request,leave_type, location, payroll,performance,project,shift_roster,shift,skill_requirement,
skill,timesheet,training;

create table department(
    dept_id int primary key,dept_name varchar(20) not null UNIQUE ,cost_center varchar(50)
);

create table location(
    location_id int primary key,city varchar(50) not null unique,
    country varchar(25),latitude decimal(9,4),longitude decimal(9,4)
);

create table shift(
    shift_id int primary key,shift_name varchar(30) not null unique,
    start_time time,end_time time,shift_type varchar(29),planned_hours decimal(3,1)
);

create table checkin_method(
    method_id int primary key,method_name varchar(20) not null 
);

create table leave_type(
    leave_type_id int primary key,leave_type varchar(50) not null ,
    annual_quota int,is_paid int 
);

create table client(
    client_id int primary key,client_name varchar(20) not null ,industry varchar(50)
);

create table project(
    project_id int primary key,project_name varchar(50) not null unique,
    client_id int,billing_rate decimal(10,2),
    foreign key(client_id) references client(client_id)
);

create table skill(
    skill_id int primary key ,skill_name varchar(30),category varchar(30)
);

create table skill_requirement(
    dept_id int ,skill_id int ,required_level int,
    primary key(dept_id,skill_id),
    foreign key(dept_id) references department(dept_id),
    foreign key(skill_id) references skill(skill_id)
);

create table employee(
    emp_id int primary key,name varchar(50) ,gender varchar(20),
    age int ,dept_name varchar(30),
    job_role varchar(50),job_level int ,salary int ,overtime_flag varchar(10),
    distance_from_home int,years_at_company int ,
    years_since_promotion int ,job_satisfaction int ,
    performance_rating int ,left_company int ,email varchar(50) not null unique,
    location_id int ,employment_type varchar(50),
    vendor_name varchar(50),hire_date datetime,termination_date datetime,
    status varchar(50),manager_id int ,
    foreign key(manager_id) references employee(emp_id),
    foreign key(location_id) references location(location_id)
);

create table attendance(
    att_id bigint primary key AUTO_INCREMENT,emp_id int not null,att_date DATE not null,shift_id int ,
    method_id int ,check_in datetime null,check_out datetime null,status varchar(50),gps_lat decimal(10,7),
    gps_long decimal(10,7),
    foreign key(emp_id) references employee(emp_id),
    foreign key(shift_id) references shift(shift_id),
    foreign key(method_id) references checkin_method(method_id)
);

create table shift_roster(
    roster_date date ,emp_id int not null ,shift_id int ,
    is_swapped int ,swap_status varchar(30),
    foreign key(emp_id) references employee(emp_id),
    foreign key(shift_id) references shift(shift_id)
);

create table leave_request(
    leave_id int primary key,emp_id int ,leave_type_id int ,start_date date ,end_date date,
    days int ,status varchar(50),request_date date,approval_date date,
    foreign key(emp_id) references employee(emp_id),
    foreign key(leave_type_id) references leave_type(leave_type_id)
);

create table timesheet(
    ts_id int primary key auto_increment,emp_id int ,ts_date date,project_id int ,hours_logged decimal(4,2),
    is_billable int ,approval_status varchar(30),
    foreign key(emp_id) references employee(emp_id),
    foreign key(project_id) references project(project_id)
);

create table payroll(
    emp_id int not null,pay_month date not null,basic_pay decimal(6,2),overtime_pay decimal(6,2),
    leave_deduction decimal(2,1),bonus decimal(2,1),incentive decimal(5,2),net_pay decimal(6,2),
    primary key(emp_id,pay_month),
    foreign key(emp_id) references employee(emp_id)
);

create table performance(
    emp_id int not null,quarter_start date,kpi_score decimal(3,1),goal_completion_pct decimal(3,1),
    productivity_score decimal(3,1),rating int ,potential_score decimal(3,1),sentiment_score decimal(3,2),
    primary key(emp_id,quarter_start),
    foreign key(emp_id) references employee(emp_id)
);

create table employee_exit(
    emp_id int primary key,exit_date date,exit_reason varchar(60),is_voluntary tinyint ,
    is_regretted tinyint ,tenure_months int ,replacement_cost decimal(12,2),
    foreign key(emp_id) references employee(emp_id)
);

create table employee_skill(
    emp_id int ,skill_id int ,proficiency_level int ,
    primary key(emp_id,skill_id),
    foreign key(emp_id) references employee(emp_id),
    foreign key(skill_id) references skill(skill_id)
);

create table training(
    training_id int primary key auto_increment,emp_id int ,course_name varchar(30),
    completion_date date,hours decimal(4,2),
    foreign key(emp_id) references employee(emp_id)
);

create table etl_log(
  table_name varchar(50) primary key, rows_staging int, rows_core int,
  rows_dropped int as (rows_staging - rows_core),
  run_at timestamp default CURRENT_TIMESTAMP
);

create table error_log (
  error_id int primary key AUTO_INCREMENT, table_name varchar(50),
  record_key varchar(50), issue varchar(200), logged_at timestamp default CURRENT_TIMESTAMP
);

select table_name from information_schema.TABLES
where table_schema='wfm_core' order by 1;
