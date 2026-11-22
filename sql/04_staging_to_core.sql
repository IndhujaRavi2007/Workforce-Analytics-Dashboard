------------Clean and load data , Filled core tables, duplicates removed, labels standardized--------------

insert into wfm_core.department
select cast(dept_id as unsigned),trim(dept_name),trim(cost_center) from wfm_staging.department;

insert into wfm_core.location
select cast(location_id as unsigned),trim(city),trim(country),
cast(latitude as decimal(9,6)),cast(longitude as decimal(9,6)) from wfm_staging.location;

select count(*) from wfm_core.department;
select count(*) from wfm_core.location;

insert into wfm_core.shift
select cast(shift_id as unsigned),trim(shift_name),cast(start_time as time),cast(end_time as time),
trim(shift_type),cast(planned_hours as unsigned) from wfm_staging.shift;

insert into wfm_core.checkin_method
select cast(method_id as unsigned),trim(method_name) from wfm_staging.checkin_method;

insert into wfm_core.leave_type
select cast(leave_type_id as unsigned),trim(leave_type),
cast(annual_quota as unsigned),cast(is_paid as unsigned) from wfm_staging.leave_type;

insert into wfm_core.client
select cast(client_id as unsigned),trim(client_name),trim(industry) from wfm_staging.client;

insert into wfm_core.project
select cast(project_id as unsigned),trim(project_name),
cast(client_id as unsigned),cast(billing_rate as decimal(10,2)) from wfm_staging.project;

insert into wfm_core.skill
select cast(skill_id as unsigned),trim(skill_name),trim(category) from wfm_staging.skill;

insert into wfm_core.skill_requirement
select cast(dept_id as unsigned),cast(skill_id as unsigned),cast(required_level as unsigned)
from wfm_staging.skill_requirement;

select count(*) from wfm_core.shift;
select count(*) from wfm_core.checkin_method;
select count(*) from wfm_core.leave_type;
select count(*) from wfm_core.client;
select count(*) from wfm_core.project;
select count(*) from wfm_core.skill;
select count(*) from wfm_core.skill_requirement;

insert into wfm_core.employee
select cast(e.emp_id as unsigned),trim(e.name),trim(e.gender),cast(e.age as unsigned),trim(e.dept_name),trim(e.job_role),
cast(e.job_level as unsigned),cast(e.salary as decimal(12,2)),trim(e.overtime_flag),cast(e.distance_from_home as unsigned),
cast(e.years_at_company as unsigned),cast(e.years_since_promotion as unsigned),cast(e.job_satisfaction as unsigned),
cast(e.performance_rating as unsigned),cast(e.left_company as unsigned),lower(trim(e.email)),l.location_id,
trim(e.employment_type),nullif(trim(e.vendor_name),''),str_to_date(left(e.hire_date,10),'%Y-%m-%d'),
str_to_date(left(nullif(trim(e.termination_date),''),10),'%Y-%m-%d'),trim(e.status),NULL
from wfm_staging.employee e 
join wfm_core.department d on d.dept_name=e.dept_name
join wfm_core.location l on l.city=trim(e.location);

update wfm_core.employee c
join wfm_staging.employee s on 
cast(s.emp_id as unsigned)=c.emp_id
set c.manager_id=cast(nullif(trim(s.manager_id),'') as unsigned);

select count(*) from wfm_core.employee where manager_id is null;
select min(hire_date),max(hire_date) from wfm_core.employee;

insert into wfm_core.attendance
 (emp_id,att_date,shift_id,method_id,check_in,check_out,status,gps_lat,gps_long)
select emp_id,att_date,shift_id,method_id,check_in,check_out,status,gps_lat,gps_long
from(
     select cast(r.emp_id as unsigned) as emp_id,
     str_to_date(left(r.att_date,10),'%Y-%m-%d') as att_date,
     cast(r.shift_id as unsigned) as shift_id,
    cast(r.method_id as unsigned) as method_id,
    str_to_date(nullif(trim(r.check_in),''),'%Y-%m-%d %H:%i:%s') as check_in,
    str_to_date(nullif(trim(r.check_out),''),'%Y-%m-%d %H:%i:%s') as check_out,
    case when upper(trim(r.status)) in ('WFH','WORK FROM HOME') then 'WFH' 
    else concat(upper(left(trim(r.status),1)),lower(substring(trim(r.status),2))) end as status,
    cast(nullif(trim(r.gps_lat),'') as decimal(9,6)) as gps_lat,
    cast(nullif(trim(r.gps_long),'') as decimal(9,6)) as gps_long,
    row_number() over(partition by r.emp_id,r.att_date order by r.check_in,r.check_out desc )
    as rn
    from wfm_staging.attendance r
     join wfm_core.employee e 
     on e.emp_id=cast(r.emp_id as unsigned)
)x
where rn=1;

select count(*) from wfm_core.attendance;
select count(*) - count(distinct emp_id, att_date) from wfm_core.attendance;
delete from wfm_core.attendance;

insert into wfm_core.shift_roster(roster_date,emp_id,shift_id,is_swapped,swap_status)
select str_to_date(left(r.roster_date,10),'%Y-%m-%d'),cast(r.emp_id as unsigned),
cast(r.shift_id as unsigned),cast(r.is_swapped as unsigned),trim(r.swap_status)
from wfm_staging.shift_roster r
join wfm_core.employee e on
e.emp_id=cast(r.emp_id as unsigned);

insert into wfm_core.leave_request(leave_id,emp_id,leave_type_id,
start_date,end_date,days,status,request_date,approval_date)
select cast(l.leave_id as unsigned),cast(l.emp_id as unsigned),cast(l.leave_type_id as unsigned),
str_to_date(left(l.start_date,10),'%Y-%m-%d'),str_to_date(left(l.end_date,10),'%Y-%m-%d'),
cast(l.days as unsigned),trim(l.status),str_to_date(left(l.request_date,10),'%Y-%m-%d'),
str_to_date(left(nullif(trim(l.approval_date),''),10),'%Y-%m-%d')
from wfm_staging.leave_request l
join wfm_core.employee e on
e.emp_id=cast(l.emp_id as unsigned);

select count(*) from wfm_staging.leave_request;
select count(*) from wfm_core.leave_request;
select status,count(*) from wfm_core.leave_request group by status;

insert into wfm_core.timesheet(emp_id,ts_date,project_id,hours_logged,is_billable,approval_status)
select cast(t.emp_id as unsigned),str_to_date(left(t.ts_date,10),'%Y-%m-%d'),
cast(t.project_id as unsigned),cast(t.hours_logged as decimal(5,2)),cast(t.is_billable as unsigned),
trim(t.approval_status) from wfm_staging.timesheet t
join wfm_core.employee e
on e.emp_id=cast(t.emp_id as unsigned);

select approval_status,count(*) from wfm_core.timesheet group by approval_status;

alter table wfm_core.payroll
modify basic_pay decimal(12,2),
modify overtime_pay decimal(12,2),
modify leave_deduction decimal(12,2),
modify bonus decimal(12,2),
modify incentive decimal(12,2),
modify net_pay decimal(12,2);

delete from wfm_core.payroll;

insert into wfm_core.payroll(emp_id,pay_month,basic_pay,overtime_pay,
leave_deduction,bonus,incentive,net_pay) 
select cast(p.emp_id as unsigned),
str_to_date(left(p.pay_month,10),'%Y-%m-%d'),
cast(p.basic_pay as decimal(12,2)),
cast(p.overtime_pay as decimal(12,2)),
cast(p.leave_deduction as decimal(12,2)),
cast(p.bonus as decimal(12,2)),
cast(p.incentive as decimal(12,2)),
cast(p.net_pay as decimal(12,2)) from wfm_staging.payroll p join wfm_core.employee e 
on e.emp_id=cast(p.emp_id as unsigned);

select count(*) from wfm_staging.payroll;
select count(*) from wfm_core.payroll;
select max(bonus) as BONUS,max(net_pay) as NET_PAY, max(leave_deduction) as LEAVE_DEDUCTION
from wfm_core.payroll;

alter table wfm_core.performance
modify kpi_score decimal(10,2),
modify goal_completion_pct decimal(10,2),
modify potential_score decimal(10,2),
modify productivity_score decimal(10,2),
modify rating decimal(10,2),
modify sentiment_score decimal(10,2);

delete from wfm_core.performance;

insert into wfm_core.performance(emp_id,quarter_start,kpi_score,goal_completion_pct,
productivity_score,rating,potential_score,sentiment_score)
select cast(p.emp_id as unsigned),
str_to_date(left(p.quarter_start,10),'%Y-%m-%d'),
cast(p.kpi_score as decimal(10,2)),
cast(p.goal_completion_pct as decimal(10,2)),
cast(p.productivity_score as decimal(10,2)),
cast(p.rating as decimal(10,2)),
cast(p.potential_score as decimal(10,2)),
cast(p.sentiment_score as decimal(10,2))
from wfm_staging.performance p
join wfm_core.employee e
on e.emp_id=cast(p.emp_id as unsigned);

select count(*) from wfm_staging.performance;
select count(*) from wfm_core.performance;
select  quarter_start, avg(kpi_score)from wfm_core.performance 
group by quarter_start;

delete from wfm_core.employee_exit;

insert into wfm_core.employee_exit(emp_id,exit_date,exit_reason,is_voluntary,
is_regretted,tenure_months,replacement_cost)
select cast(t.emp_id as unsigned),
str_to_date(left(t.exit_date,10),'%Y-%m-%d'),
trim(t.exit_reason),
cast(cast(t.is_voluntary as decimal(10,2)) as unsigned),
cast(cast(t.is_regretted as decimal(10,2)) as unsigned),
cast(cast(t.tenure_months as decimal(10,2)) as unsigned),
cast(t.replacement_cost as decimal(10,2))
from wfm_staging.exit t 
join wfm_core.employee e
on e.emp_id=cast(t.emp_id as unsigned);

insert into wfm_core.employee_skill(emp_id,skill_id,proficiency_level)
select cast(s.emp_id as unsigned),cast(s.skill_id as unsigned),cast(s.proficiency_level as unsigned)
from wfm_staging.employee_skill s
join wfm_core.employee e
on s.emp_id=e.emp_id;

select emp_id,sum(proficiency_level) as total_proficiency_level from wfm_core.employee_skill
group by emp_id;

insert into wfm_core.training(emp_id,course_name,completion_date,hours)
select cast(t.emp_id as unsigned),
trim(course_name),
str_to_date(left(completion_date,10),'%Y-%m-%d'),
cast(hours as unsigned) from wfm_staging.training t
join wfm_core.employee e 
on e.emp_id=cast(t.emp_id as unsigned);

select course_name,count(*) from wfm_core.training 
group by course_name;

delete from wfm_core.etl_log;

insert into wfm_core.etl_log(table_name,rows_staging,rows_core)
select 'employee' ,(select count(*) from wfm_staging.employee),(select count(*) from wfm_core.employee)
UNION ALL
select 'attendance',(select count(*) from wfm_staging.attendance),(select count(*) from wfm_core.attendance)
UNION ALL
select 'shift_roster',(select count(*) from wfm_staging.shift_roster),(select count(*) from wfm_core.shift_roster)
UNION ALL
select 'leave_request',(select count(*) from wfm_staging.leave_request),(select count(*) from wfm_core.leave_request)
UNION ALL
select 'timesheet',(select count(*) from wfm_staging.timesheet),(select count(*) from wfm_core.timesheet)
UNION ALL
select 'payroll',(select count(*) from wfm_staging.payroll),(select count(*) from wfm_core.payroll)
UNION ALL
select 'performance',(select count(*) from wfm_staging.performance),(select count(*) from wfm_core.performance)
UNION ALL
select 'employee_exit',(select count(*) from wfm_staging.exit),(select count(*) from wfm_core.employee_exit)
UNION ALL
select 'employee_skill',(select count(*) from wfm_staging.employee_skill),(select count(*) from wfm_core.employee_skill)
UNION ALL
select 'training',(select count(*) from wfm_staging.training),(select count(*) from wfm_core.training);

select * from wfm_core.etl_log;

