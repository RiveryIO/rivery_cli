
# logs fetch

None

## Usage

```
Usage: rivery activities logs fetch [OPTIONS]
```

## Options
* `runid` (REQUIRED): 
  * Type: STRING 
  * Default: `none`
  * Usage: `--runId`

  The run id that will be used to filter the logs.

* `filepath`: 
  * Type: STRING 
  * Default: `none`
  * Usage: `--filePath`

  The file that the logs should be saved to.


* `pretty`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--pretty`

  Whether logs should be in a pretty table format or not.
  
* `help`: 
  * Type: BOOL 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```
Usage: rivery activities logs fetch [OPTIONS]

Options:
  --runId TEXT     The run id that will be used to filter the logs.  [required]
  --filePath TEXT  The file that the logs should be saved to.
  --pretty TEXT  Whether logs should be in a pretty table format or not.
  --help           Show this message and exit.
```

