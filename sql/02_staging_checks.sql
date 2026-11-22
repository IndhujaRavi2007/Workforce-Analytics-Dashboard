----------------------Inspect the raw data,Table list, row counts, the 3,103 duplicates, “Work From Home” vs “WFH”----------------------

USE wfm_staging;
SHOW TABLES;                                             
SELECT COUNT(*) FROM attendance;                     
SELECT status, COUNT(*) FROM attendance GROUP BY status;  
SELECT COUNT(*) - COUNT(DISTINCT emp_id, att_date) AS duplicate_rows FROM attendance; 