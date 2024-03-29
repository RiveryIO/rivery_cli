# Getting started

## Requirements
1. You must have Python 3.6 or later installed.
For installation instructions, see the [Downloading Python](https://www.python.org/downloads/) page in Python's Beginner Guide.

2. An API Token with the following scopes:
```
    * me:list
    * river:execute
    * river:edit
    * river:list
    * river:delete
    * connection:edit
    * connection:list
    * connection:delete
```
In order to create a new API token, [please refer to our docs](https://rivery.io/docs/api-documentation)

## Install
Install Rivery CLI, by using the next command:

```bash

> pip install rivery-cli
```

## Check Installation
In order to see if Rivery CLI was installed in your client, check the version option by the next command:

```shell
> rivery --version
```

Result should be:

```shell
Rivery CLI, version ...
```

## Initiate a new project
in order to start new _project_:
1. create new project directory, for example in linux base OS:
```bash 
> mkdir /home/my-project
```
or in windows:
```shell
> mkdir c:\my-project
```

2. Go into the `my-project` directory you've created: `cd my-project`
3. run the next command and choose your project name.
```bash
> rivery init
```

## Create the first profile
Rivery CLI store defaults and credentials under an "entity" called `profile`. 

Each profile has its name and the configurations under it. Due to every API token refers
to specific `account`+`environment` inside your Rivery console, and every account+environment pair has
its own credentials, it is likely you'll have a profile per each account+environment coupling.

For creating your first profile use the next command:

```bash
> rivery configure
```

And Follow the prompt:
```bash
> Please enter your token. (******): ...
> Choose your Region () [...]: ...
> Thank you for entering auth credentials. 
> Please check your profile at: ~/.rivery/auth
```

And you're good to go!
