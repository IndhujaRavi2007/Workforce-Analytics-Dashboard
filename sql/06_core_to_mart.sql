----------------------Reshape and calculate,Filled star schema with business metrics--------------------------

---------------------Dimension-----------------------------
set session cte_max_recursion_depth=5000;
insert into wfm_mart.dim_date 
with recursive d as(
    select date('2026-01-01') as dt
    UNION ALL select dt+interval 1 day from d where dt<'2026-12-31'
)
select cast(date_format(dt,'%Y%m%d') as unsigned),dt,Year(dt),quarter(dt),month(dt),monthname(dt), date_format(dt,'%Y-%m'),
weekofyear(dt),dayname(dt),weekday(dt)+1,if(weekday(dt)>=5,1,0)
from d;

insert into wfm_mart.dim_department 
select dept_id,dept_name,cost_center from wfm_core.department;

insert into wfm_mart.dim_checkin_method
select method_id,method_name from wfm_core.checkin_method;

insert into wfm_mart.dim_client
select client_id,client_name,industry from wfm_core.client;

insert into wfm_mart.dim_leave_type
select leave_type_id,leave_type,annual_quota,is_paid from wfm_core.leave_type;

insert into wfm_mart.dim_location
select location_id,city,country,latitude,longitude from wfm_core.location;

insert into wfm_mart.dim_shift
select shift_id,shift_name,start_time ,end_time,shift_type ,planned_hours from wfm_core.shift;

insert into wfm_mart.dim_skill
select skill_id,skill_name,category from wfm_core.skill;

insert into wfm_mart.dim_project
select project_id,project_name,client_id,billing_rate from wfm_core.project;

DELETE FROM wfm_mart.dim_employee;

ALTER TABLE wfm_mart.dim_employee MODIFY location VARCHAR(50);
ALTER TABLE wfm_mart.dim_employee
  MODIFY name VARCHAR(100),
  MODIFY dept_name VARCHAR(50),
  MODIFY location VARCHAR(50),
  MODIFY email VARCHAR(120),
  MODIFY employment_type VARCHAR(20),
  MODIFY vendor_name VARCHAR(50),
  MODIFY status VARCHAR(20),
  MODIFY overtime_flag VARCHAR(5);

ALTER TABLE wfm_mart.dim_employee MODIFY job_role VARCHAR(80);

SELECT column_name, column_type FROM information_schema.columns
WHERE table_schema='wfm_mart' AND table_name='dim_employee' AND column_name IN ('job_role','dept_name','location');

INSERT INTO wfm_mart.dim_employee
  (emp_key, emp_id, name, gender, age, dept_key, dept_name, job_role, job_level, salary,
   overtime_flag, distance_from_home, years_at_company, years_since_promotion,
   job_satisfaction, performance_rating, left_company, email, location, location_key,
   employment_type, vendor_name, hire_date, termination_date, status, manager_id)
SELECT e.emp_id, e.emp_id, e.name, e.gender, e.age, d.dept_id, e.dept_name, e.job_role,
       e.job_level, e.salary, e.overtime_flag, e.distance_from_home, e.years_at_company,
       e.years_since_promotion, e.job_satisfaction, e.performance_rating, e.left_company,
       e.email, l.city, e.location_id, e.employment_type, e.vendor_name, e.hire_date,
       e.termination_date, e.status, e.manager_id
FROM wfm_core.employee e
JOIN wfm_core.department d ON d.dept_name = e.dept_name
JOIN wfm_core.location l   ON l.location_id = e.location_id;

SELECT column_name FROM information_schema.columns
WHERE table_schema='wfm_mart' AND table_name='dim_employee' ORDER BY ordinal_position;

SELECT column_name FROM information_schema.columns
WHERE table_schema='wfm_core' AND table_name='employee' ORDER BY ordinal_position;


---------------------fact-------------------
insert into wfm_mart.fact_attendance
select cast(date_format(a.att_date,'%Y%m%d')as unsigned), a.emp_id, a.shift_id, a.method_id, a.status,
       greatest(0, timestampdiff(minute,timestamp(date(a.check_in), s.start_time), a.check_in)),
       round(timestampdiff(minute, a.check_in, a.check_out)/60, 2),
       greatest(0, round(timestampdiff(minute, a.check_in, a.check_out)/60 - s.planned_hours, 2)),
       greatest(0, round(timestampdiff(minute, a.check_in, a.check_out)/60 - s.planned_hours, 2))
         * e.salary / 2080 * 1.5,
       a.gps_lat, a.gps_long, 0
from wfm_core.attendance a
join wfm_core.shift s on s.shift_id = a.shift_id
join wfm_core.employee e on e.emp_id = a.emp_id;

delete from wfm_mart.fact_attendance;

insert into wfm_mart.fact_employee_skill
select emp_id,skill_id,proficiency_level from wfm_core.employee_skill;

insert into wfm_mart.fact_attrition
select emp_id,cast(date_format(exit_date,'%Y%m%d') as unsigned),exit_reason,is_voluntary,
is_regretted,tenure_months,replacement_cost from wfm_core.employee_exit;

insert into wfm_mart.fact_leave_request
select leave_id,emp_id,leave_type_id,cast(date_format(start_date,'%Y%m%d') as unsigned),
cast(date_format(end_date,'%Y%m%d') as unsigned),days,status,
cast(date_format(request_date,'%Y%m%d') as unsigned),cast(date_format(approval_date,'%Y%m%d')as unsigned)
from wfm_core.leave_request;

insert into wfm_mart.fact_payroll
select emp_id,cast(date_format(pay_month,'%Y%m%d') as unsigned),basic_pay,overtime_pay,
leave_deduction,bonus,incentive,net_pay
from wfm_core.payroll;

insert into wfm_mart.fact_performance
select emp_id,cast(date_format(quarter_start,'%Y%m%d') as unsigned),kpi_score,
goal_completion_pct,productivity_score,rating,potential_score,sentiment_score
from wfm_core.performance;

insert into wfm_mart.fact_shift_roster (date_key, emp_id, shift_id, is_swapped, swap_status)
select cast(date_format(roster_date,'%Y%m%d') as unsigned),emp_id,
shift_id,is_swapped,swap_status
from wfm_core.shift_roster;

insert into wfm_mart.fact_timesheet
select emp_id,cast(date_format(ts_date,'%Y%m%d') as unsigned),project_id,
hours_logged,is_billable,approval_status
from wfm_core.timesheet;

insert into wfm_mart.fact_training
select emp_id,course_name,cast(date_format(completion_date,'%Y%m%d')as unsigned),hours
from wfm_core.training;

------------------Again performinng dimension date because for the first query it has many null statements----------
DELETE FROM wfm_mart.dim_date;


SET SESSION cte_max_recursion_depth = 5000;

INSERT INTO wfm_mart.dim_date
  (date_key, date, year, quarter, month_no, month_name, year_month_txt, week_no, day_name, day_no, is_weekend)
WITH RECURSIVE d AS (
  SELECT DATE('2024-01-01') AS dt
  UNION ALL
  SELECT dt + INTERVAL 1 DAY FROM d WHERE dt < '2026-12-31')
SELECT CAST(DATE_FORMAT(dt,'%Y%m%d') AS UNSIGNED), dt, YEAR(dt), QUARTER(dt), MONTH(dt),
       MONTHNAME(dt), DATE_FORMAT(dt,'%Y-%m'), WEEKOFYEAR(dt), DAYNAME(dt),
       WEEKDAY(dt)+1, IF(WEEKDAY(dt)>=5,1,0)
FROM d;

SELECT column_name FROM information_schema.columns
WHERE table_schema='wfm_mart' AND table_name='dim_date' ORDER BY ordinal_position;

SELECT COUNT(*), MIN(date), MAX(date) FROM wfm_mart.dim_date; 

SELECT MIN(f.date_key), MAX(f.date_key), COUNT(DISTINCT f.date_key)
FROM wfm_mart.fact_shift_roster f
LEFT JOIN wfm_mart.dim_date d ON d.date_key = f.date_key
WHERE d.date_key IS NULL;

SELECT column_name FROM information_schema.columns
WHERE table_schema='wfm_mart' AND table_name='fact_shift_roster' ORDER BY ordinal_position;

SELECT date_key, emp_id, emp_key, shift_id, is_swapped, swap_status
FROM wfm_mart.fact_shift_roster LIMIT 5;

DELETE FROM wfm_mart.fact_shift_roster;

INSERT INTO wfm_mart.fact_shift_roster
  (date_key, emp_key, shift_id, is_swapped, swap_status)
SELECT CAST(DATE_FORMAT(roster_date,'%Y%m%d') AS UNSIGNED), emp_id, shift_id, is_swapped, swap_status
FROM wfm_core.shift_roster;
SELECT COUNT(*) FROM wfm_mart.fact_shift_roster;                       
SELECT COUNT(*) FROM wfm_mart.fact_shift_roster WHERE emp_key IS NULL;  