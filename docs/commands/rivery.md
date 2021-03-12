
# rivery

Rivery CLI 

## Usage

```
Usage: rivery [OPTIONS] COMMAND [ARGS]...
```

## Options
* `region`: 
  * Type: Choice('['us-east-2', 'eu-west-1']') 
  * Default: `us-east-2`
  * Usage: `--region`

  The region of the profile to connect


* `host`: 
  * Type: STRING 
  * Default: `https://console.rivery.io`
  * Usage: `--host`

  Connect to specific Rivery host (for example: https://eu-west-1.console.rivery.io)


* `debug`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--debug`

  Show debug log


* `ignoreerros`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--ignoreErros`

  Ignore errors during run.


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```
Usage: rivery [OPTIONS] COMMAND [ARGS]...

  Rivery CLI

Options:
  --region [us-east-2|eu-west-1]  The region of the profile to connect
                                  [default: us-east-2]

  --host TEXT                     Connect to specific Rivery host (for example:
                                  https://eu-west-1.console.rivery.io)

  --debug                         Show debug log
  --ignoreErros                   Ignore errors during run.
  --help                          Show this message and exit.

Commands:
  configure  Configure new profile and the authentication.
  init       Make a initiation project.yaml in the current path
  rivers     Rivers operations (push, pull/import)
```

