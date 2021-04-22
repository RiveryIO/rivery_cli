# `project.yaml` 

## What is it for?
The `project.yaml` is the file define the project structure and basic configuration. Evert Rivery IaC project needs
its own `project.yaml` file, which indicates that the project dir is a Rivery IaC project. The CLI command knows to 
handle the references and connectivity between entities inside the project only under project dir.

For example, a directory of `my-project` includes a `project.yaml` file, 
and should be used as a Rivery IaC reference project.

## Reference

```yaml
name: <string> # my-project-name
version: 1.0 # Rivery Iac reference version. 
models: <string> # the name of the "models" or "entities" dir inside the project.
sqls: <string> # the name of the "sql" files dir isnide the project
maps: <string> # the name of the mapping (table references) dir inside the project 
```

## Init a new project

In order to create new project inside a dir, just run the [`rivery init`](..\commands\rivery-init.md) command.


## Importing groups/rivers
Rivery CLI provide a command to create local entity `yaml` files from rivers in a live account/env.
In order to import river or an entire group of rivers from your account to your local project, you can run the next command:

```bash
> rivery rivers import --groupName='my-group'/--riverId='123475658493782612' --path=/import/path/under/models/dir
```

Check out the [`rivery rivers import` reference](../commands/rivers/rivers-import.md) for more info.