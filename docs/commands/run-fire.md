
# run fire

 Run a river whitin the current profile (account+environment).
Gets a riverid key, with the river id to run
and just run it in the platform.

## Usage

```
Usage: rivery rivers run fire [OPTIONS]
```

## Options
* `riverid` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--riverId`

  Please provide at least one river id to run.
River Id can be found in the river url, structured as this:
https://<cli-console>/#/river/<accountId>/<environmentId>/river/**<RiverId>**


* `entityname`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--entityName`

  


* `waitforend`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--waitForEnd`

  


* `timeout`: 
  * Type: INT 
  * Default: `none`
  * Usage: `--timeout`

  The number of seconds to wait for the run to complete until giving up.  
Eligible only on hitting --waitForEnd option


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```
Usage: rivery rivers run fire [OPTIONS]

   Run a river whitin the current profile (account+environment). Gets a
   riverid key, with the river id to run and just run it in the platform.

Options:
  --riverId TEXT     Please provide at least one river id to run. River Id can
                     be found in the river url, structured as this:
                     https://<cli-console>/#/river/<accountId>/<environmentId>/r
                     iver/**<RiverId>**  [required]

  --entityName TEXT
  --waitForEnd
  --timeout INTEGER  The number of seconds to wait for the run to complete until
                     giving up.   Eligible only on hitting --waitForEnd option

  --help             Show this message and exit.
```

