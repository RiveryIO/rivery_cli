# River Yaml Reference
River yaml reference has couple of mandatory keys needed to be provided in the yaml.

```yaml
name: River name. 
description: River Description. 
type: logic # The type of the river, we now support only *logic* type of river. 
group_name: The river group name.
notifications: 
  <notifications block>
schedule: 
  <schedule block>
properties: 
  <properties block by type>
```

## Notifications
```yaml
notifications: 
  on_failure: 
    # On failure notification. 
    email: myemail@mycomp.com # email to send notifications
    enabled: true|false 
  on_warning:
    # On warning notifications
    email: myemail@mycomp.com # email to send notifications
    enabled: true|false 
  on_run_threshold:
    # On runtime notification 
    email: myemail@mycomp.com # email to send notifications
    enabled: true|false
  run_notification_timeout: 43200  # The number of seconds for sending a notification timeout, up to 43200 (12 hours).
```

## Schedule
Schedule block, define the scheduling method of the river

All scheduling in Rivery uses [quartz expression](https://www.freeformatter.com/cron-expression-generator-quartz.html) as the scheduling expression to fire the river.

```yaml
schedule:
  cronExp: 0 55 14 1 1 ? * # Quartz expression to run
  endDate: 2020-01-03T00:00:00 # Start date of the scheduling
  isEnabled: true|false # Does the scheduling enabled
  startDate:  2020-01-03T00:00:00 # End date of the scheduling
```


