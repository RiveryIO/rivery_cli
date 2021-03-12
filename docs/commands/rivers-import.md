
# rivers import

Import current river(s) into a yaml files.
Get a group or river ID in the right env and account
and create a yaml file per the source

## Usage

```
Usage: rivery rivers import [OPTIONS]
```

## Options
* `riverid`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--riverId`

  Please provide at least one river id.
River Id can be found in the river url, structured as this:
https://<cli-console>/#/river/<accountId>/<environmentId>/river/**<RiverId>**


* `groupname`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--groupName`

  Please provide a group name of rivers.
The group name can be found near every river, in the river screen at cli.


* `path`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--path`

  The path you want to import into.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```
Usage: rivery rivers import [OPTIONS]

  Import current river(s) into a yaml files. Get a group or river ID in the
  right env and account and create a yaml file per the source

Options:
  --riverId TEXT    Please provide at least one river id. River Id can be found
                    in the river url, structured as this: https://<cli-console>/
                    #/river/<accountId>/<environmentId>/river/**<RiverId>**

  --groupName TEXT  Please provide a group name of rivers. The group name can be
                    found near every river, in the river screen at cli.

  --path TEXT       The path you want to import into.
  --help            Show this message and exit.
```

