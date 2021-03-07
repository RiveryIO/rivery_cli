SELECT
  accounts.registration_date as registration_date,
  accounts._id as account_id ,
  accounts.account_name as account_name,
  accounts.account_type as account_type,
  accounts.owner_email as owner_email,
  accounts.step as reg_step_id,
  case when accounts.step=1 then '1 - Account_Form'
       when accounts.step=2 then '2 - Verification'
       when accounts.step=3 then '3 - Test Connection'
       when accounts.step=4 then '4 - Finish Account Creation'
       else 'Unknown' end as reg_step_name,
  accounts.status as account_status,
  accounts.first_name as first_name,
  accounts.last_name as last_name,
  accounts.company_name as company_name,
  accounts.country_code as country_code,
  accounts.country as country,
  accounts.phone_number as phone_number,
  accounts.job_title as job_title,
  accounts.is_technical_registration as is_technical_registration,
  accounts.first_referrer_url as first_referrer_url,
  accounts.first_url as first_url,
  accounts.registration_target_type as registration_target_type,
  accounts.current_units as current_rpu_units,
  accounts.limitations.units as limitations_rpu_units,
  accounts.limitations.days_trial as limitations_days_trial,
  accounts.is_active as is_account_active,
  accounts.partner as partner,
  accounts.affiliate as affiliate,
  accounts.wp_referrer as wp_referrer,
  events.source_interest as source_interest,
  events.target_interest as target_interest,
  events.complete_target as complete_target,
  events.flow_session_run_river as flow_session_run_river,
  events.flow_session_run_river_success as flow_session_run_river_success,
  events.flow_session_run_river_failures as flow_session_run_river_failures,
  events.flow_session_success_run_congrats_message as flow_session_success_run_congrats_message,
  events.flow_session_mapping_triggered as flow_session_mapping_triggered,
  events.flow_session_mapping_success as flow_session_mapping_success,
  activity.total_river_runs as total_river_runs,
  activity.total_success_river_runs as total_success_river_runs,
  activity.total_failure_river_runs as total_failure_river_runs
FROM [visionbi-cloud:rivery_internal.ods_mongodb_accounts] as accounts
  left join
  (
      SELECT
      account as account_id,
      max(case when event_data.name = 'source_interest' then event_data.value else null end) as source_interest,
      max(case when event_data.name = 'target_interest' then event_data.value else null end) as target_interest,
      max(case when event_data.name = 'complete_target' then event_data.value else null end) as complete_target,
      sum(case when event_data.name = 'flow_session_run_river' then 1 else 0 end) as flow_session_run_river,
      sum(case when event_data.name = 'flow_session_run_river_success' then 1 else 0 end) as flow_session_run_river_success,
      sum(case when event_data.name = 'flow_session_run_river_failures' then 1 else 0 end) as flow_session_run_river_failures,
      sum(case when event_data.name = 'flow_session_success_run_congrats_message' then 1 else 0 end) as flow_session_success_run_congrats_message,
      sum(case when event_data.name = 'flow_session_mapping_triggered' then 1 else 0 end) as flow_session_mapping_triggered,
      sum(case when event_data.name = '	flow_session_mapping_success' then 1 else 0 end) as flow_session_mapping_success
    FROM [visionbi-cloud:rivery_internal.ods_mongodb_registration_events]
    group by account_id
  )events
  on accounts._id  = events.account_id

  left join
  (
  SELECT account_id,
  sum(case when task_status in( 'D','E') then 1 else 0 end) as  total_river_runs,
  sum(case when task_status = 'D' then 1 else 0 end) as total_success_river_runs,
  sum(case when task_status = 'E' then 1 else 0 end) as total_failure_river_runs,
  sum(case when task_status = 'D' then rpu else 1 end) as total_rpu
  FROM [visionbi-cloud:rivery_internal.v_fact_stats_activity]
  group by account_id
  )activity
  on accounts._id  = activity.account_id