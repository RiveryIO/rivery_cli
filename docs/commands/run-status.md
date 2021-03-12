
# run status

Check the run status by runId 

## Usage

```
Usage: rivery rivers run status [OPTIONS]
```

## Options
* `runid` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--runId`

  The run id to check the status on.


* `timeout`: 
  * Type: INT 
  * Default: `none`
  * Usage: `--timeout`

  The number of seconds to wait for the run to complete until giving up.  
Eligible only on hitting --waitForEnd option


* `waitforend`: 
  * Type: STRING 
  * Default: `false`
  * Usage: `--waitForEnd`

  


* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```
Usage: rivery rivers run status [OPTIONS]

  Check the run status by runId

Options:
  --runId TEXT       The run id to check the status on.  [required]
  --timeout INTEGER  The number of seconds to wait for the run to complete until
                     giving up.   Eligible only on hitting --waitForEnd option

  --waitForEnd
  --help             Show this message and exit.
```

