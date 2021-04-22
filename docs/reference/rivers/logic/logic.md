# Logic

## Basic definition 
Every logic river is defined from basic array of `steps` and block of `variables`. 
* `steps` block is an array that include the step definitions per each step/container in the logic.
* `variables` block is an object that define the *river variables* of the logic.

```yaml
properties:
  steps: 
    # The "steps" block which includes all steps 
    # (below for each step, based on step type)
    - <step block 1>
    - <step block 2>
  variables: # Logic variables
    <variable block>
```

## Steps:
The `steps` block which includes all steps (below for each step, based on step type) to run in the river.

Every step type has it's own required and definitions, in addition to the basic step definition every step in the yaml has.

### Basic step definition

Every step in rivery has a basic implementation as that:

```yaml
steps:
  - type: step|container 
    # the type of the step - "step" or "container", every type has its own definition
    isEnabled: true|false. # Step is enabled or not.
    step_name: Step Name
    step_type: sql|action|river|container
    <step block> | 
    <container block>
```

### SQL Step
SQL Step provides you the option to run query into table, variable and external file.

```yaml
  steps:
    - type: step
      block_primary_type: sql 
      block_db_type: snowflake|big_query_sql|redshift|rds_pg 
        # The step target type - Snowflake / BigQuery etc.
      block_type: same as block db type
      target_type: table|file_export|variable
      # Where to store the results of the SQL query
      
      # Source section
      # =================
      connection_id: 5aa5387b5674093f6a98c600 
        # The connection id that is connected to this step. 
        # In order to get the connection id, you can use Rivery API or `rivery connections` command line
      execute_sql_command: true|false 
        # Use SQL Script or not in the step?
      query_priority: interactive 
        # For DWH Support (BQ interactive)

      sql_query:  "SELECT * FROM TABLE..." | 
            !sql: <relative sql path under the sql directory>
      # The actual SQL query. The SQL can be inline or using !sql key to a specific SQL file.
      # e.g. `sql_query`: !sql: file_path.sql (under the SQL directory in the root directory of the project)         
    
      # Target section:
      # ==================
      ## ** Table **
      database: MY_DB 
        # The target database name to send the data to
      schema_id: MY_SCHEMA
        # In compatible targets (like Snowflake) - 
      drop_after: true|false 
      # Should the step drop the table after the river ends
      target_table: MY_TABLE
      # The target table to load into
      target_loading: merge|overwrite|append
      # The loading method
      merge_method: switch_tables|delete_insert|merge
      # The merge method to use in compatible targets (Snowflake, Postgres). 
      split_tables: true|false 
      # Splitting table to table partitions, in BQ legacy mode.
      split_interval: d|d_h|d_h_m
      # Splitting interval for table partitions, in BQ Legacy mode only.
      use_standard_sql: true|false
      # In BQ only, use standard/legacy SQL
      fields:
        # The column mapping. This is optional if there are no keys. 
        # User can either have the fields inline or !map to a table represented as yaml.
        - fieldName: impressions
          # The field name
          isKey: true|false
          # Is this field a key
          length: 0...2456432
          # The field length (if supported)
          type: VARCHAR|TIMESTAMP|INTEGER...
          # The field type
          alias: impressionsnew
          # The target field name
          expression: current_timestamp()
          # The target field expression
          fields:
            # In case of object field type, there's a need to define the fields under it.
            - <fields object>
        | !map: <relative map path under the mapping directory>

      ## ** File Export **
      bucket_name: MY_BUCKET
      # The bucket/container name
      compression: gzip
      # Does the file in the bucket is compressed or not?
      fzConnection: 5aa5387b5674093f6a98c600
      # The filezone connection, if needed (like in custom file zone definition in the source connection)
      file_path_destination: PATH/TO/FILE
      # The file path destination to put the results on
      file_type: json|csv
      # File type - json/csv
      csv_details:
        # In a case of CSV file type, provide the csv definition
        header: true|false 
        # Should we add an header to the csv
        delimiter: ,
        # delimiter of the csv, default=,
        quote: \"
        # the quote char in the csv, default="

      ## ** Variable **
      variable_name: Target variable name
      # variable name to send the result into 
```

### Action Step
Logic can run an action step, provide and gets variable data from and to the step.

```yaml
steps:
  - type: step
    block_primary_type: action
    block_type: action
    action_id: 5ddbfae556740961a97f6f37
      # The action cross id to run in the logic step. 
      # You can get the action id using the river url, and by the API, 
      # or as a reference from another action river entity.
    connection_oid: 5aa5387b5674093f6a98c600
    # The connection id the action will run with
    action_vars:
      # An object with the action variables to pass/get from the action, using variable mapping of key-val
      action_variables: 
        # variables to pass/return to the action
        key: val
      connection_details: 
        # The connection variables to pass in
        key: val
      interval_params: 
        # The interval parameters to pass in
        key: val
```

### River Step
Logic can run a river inside a step

```yaml
steps:
  - type: step
    block_primary_type: river
    block_type: river
    river_id: 5ddbfae556740961a97f6f37
      # The river id to run under the step.
```

### Container
Steps can also be set as container type, which means they include other steps (or containers, for example).

```yaml
steps:
  - type: container
    step_name: Container Name
    container_running: run_once|for_loop|condition
      # How the container is running. 
      # run_once = run the container on time
      # for_loop = run the container with for <> set in <> loop
      # condition = make a condition container
    isEnabled: true|false
      # does the container enabled
    isParallel: true|false
      # Should steps inside this container run in parallel
    loop_over_value: all_rows_var
      # For loop over only: the "first" part
    loop_over_variable_name: one_row_var
      # For loop over only: the "set in" part
    steps:
      - <step 1 block>
      - <step 2 block>
      - <container 1 block>
      ...
```

### Condition
Condition is a specific type of container, which create a specific run of specific step/containers by condition flow / else flow...
In condition container, the "setting" of each step for each condition will be added to the step itself. 

#### Condition Definition

```yaml
condition:
  condition_name: Condition 1
  condition_then: run_step | stop | failed | pass
  key: '{myvar}' 
    # The condition key in the equation
  operator: equals | greater_than | lower_than | exists ...
    # The "equalilty" sign... 
  val: my_val
    # The value for equals to 
```

#### Condition example

```yaml
steps:
  type: container
  step_name: Container Name
  container_running: run_once|for_loop|condition
    # How the container is running. 
    # run_once = run the container on time
    # for_loop = run the container with for <> set in <> loop
  # condition = make a condition container
  isEnabled: true|false
    # does the container enabled
  isParallel: true|false
  steps:
    - block_primary_type: river
      block_type: river
      condition:
        condition_name: Condition 1
        condition_then: run_step
        key: '{myvar}'
        operator: equals
        val: my_val
    - ....

```

## Variables

Variables are setting up in the logic river as the local variable of the specific river.

```yaml
variables:
  variable_name:
    # Variable name
    clear_value_on_start: true | false
    # Should the value be cleared on the start
    value: variable_value
    # The variable value
```