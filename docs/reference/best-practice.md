# How to work with Rivery CLI?
Rivery CLI is an amazing way to manage, deploy, run and edit rivers inside Rivery.
The rivers are configured only by `.yaml` files, as a configuration files, makes this CLI as a basic
of Infrastructure As Code (IaC) methodology.

Rivery CLI is a project based command line tool, what means the command line knows to work and operate under every directory
has a `project.yaml` file under it. The `project.yaml` file provides the 

A project is a directory includes `.sql` and `.yaml` reference files, which represents infra entities, references and connections between them,
what makes the management and handling entities in Rivery (rivers/connections) connected in one place, and can be done using Infrastructure As Code ([IaC](https://en.wikipedia.org/wiki/Infrastructure_as_code)) methodology.

In order to start new project, please check out this project's [getting started guide](getting-started.md).

## Referencing between entities
When you configure and manage your entities, it is common to have some features which you use across several of resources.
In that case, you can create a snippet for such elements in order to use them multiple times when you need it and manage them in one place.
Rivery CLI provides a quick and easy way to manage entities, using a fragmented, isolated and independent references per each entity,
or even per specific parts in the entities, like table references, sql clauses, variables, and references.


### The `!ref` key
The basic reference key is the `!ref` key. 
Using `!ref` provides to create a reference (which actually concatenate) another pieces of `yaml` files across.

For example, supposed you have a large [logic](rivers/logic/logic.md) entity, and you want to manage its steps in file-per-step structure.
In this case, you may want to have a structure like the next:

```
rivers/
   base.yaml
   steps/
     step1.yaml
     step2.yaml
```

Therefore, in order to manage each step in its own yaml file, you can create a 2 [step.yaml](rivers/logic/logic.md#steps) file that will look like that:
```yaml
## Step 1.yaml
type: step
block_primary_type: river
block_type: river
river_id: 5ddbfae556740961a97f6f37
step_name: my_river_step
```

```yaml
## Step 2.yaml
type: step
block_primary_type: river
block_type: river
river_id: 5d49f85d03g7d930f8g7d9f
step_name: my_river_step2
```

and connect them in the main [`container`](rivers/logic/logic.md#container) definition with `!ref` key:

```yaml
steps:
  type: container
  steps:
    - !ref: steps/step1.yaml
      # Reference to the first steps definition
    - !ref: steps/step2.yaml
      # Reference to the second step definition
  ...
```

### The `!sql` key
Managing sql clauses inside yaml files are not the easiest and nicest thing to perform. Therefore, in most cases, it's recommended
managing SQLs in separated files, one per a query. __An important__ ability using SQL files in separated files provide is version management using any version-control tool, such as `git`.

For these cases, you can create the a `.sql` file under the `sqls` dir configured in the `project.yaml`, and use
its reference on entities/mapping `yaml` files. The reference for using an sql query file is deteremnined by the
`!sql` key. Moreover, using this reference provides you the way to manage the same sql query with more than one
logic entity.

For example, think you have a project included entities yaml with a couple of steps:

```
project-dir/
    entities/
        logics/
            logic1.yaml
```
and the `logic.yaml` file contains 2 sql query steps:

```yaml
steps:
  ## Step 1.yaml
  - type: step
    block_primary_type: sql
    block_db_type: ...
    block_type: sql
    sql_query: "SELECT * from mydb.mytable"
    step_name: my_river_step
  ## Step 2.yaml
  - type: step
    block_primary_type: sql
    block_db_type: ...
    block_type: sql
    sql_query: "SELECT * from mydb.mytable2"
    step_name: my_river_step2
```

Therefore, instead of managing these sql inline in the yaml files, you can separate them into independent files:
```sql
/* mytable.sql */
SELECT * from mydb.mytable
```
```sql
/* mytable2.sql */
SELECT * from mydb.mytable
```

The files will lay under the `sqls` dir as defined in the `project.yaml` and can be also combined under dir by their business significance :

```
project-dir/
    project.yaml
    entities/
      logics/
        logic1.yaml
    sqls:
      sales/
        mytable.sql
        mytable2.sql  
```

and create a reference in your yamls to your files:
```yaml
steps:
  ## Step 1.yaml
  - type: step
    block_primary_type: sql
    block_db_type: ...
    block_type: sql
    sql_query: 
      !sql: sales/mytable.sql
    step_name: my_river_step
  ## Step 2.yaml
  - type: step
    block_primary_type: sql
    block_db_type: ...
    block_type: sql
    sql_query: 
      !sql: sales/mytable2.sql
    step_name: my_river_step2
```




