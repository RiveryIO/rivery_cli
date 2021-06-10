# Overview

Rivery CLI is an amazing way to manage, deploy, run and edit rivers inside Rivery.
The rivers are configured only by `.yaml` files, as a configuration files, makes this CLI as a basic
of Infrastructure As Code (IaC) methodology.

In order to start using the tool, go to the [Getting Started](https://riveryio.github.io/rivery_cli/getting-started/) page.


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
pip install -U rivery-cli
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
to specific account+environment inside your Rivery console, and every account+environment pair has
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


# Issues and Feature Requests
Rivery CLI and IaC engine is fully open source dir.
We're getting in warm welcome any issues/features submitted to our end, and encourage the community to contribute in the solution.
Please don't hesitate to add any issues/feature request using the [repo's Issues section.](https://github.com/RiveryIO/rivery_cli/issues)


# Getting start With Rivery
You can check out our product docs at [https://docs.rivery.io](https://docs.rivery.io) in order to getting started.


# Full documentation
You may find here the [full documentation](https://riveryio.github.io/rivery_cli).



