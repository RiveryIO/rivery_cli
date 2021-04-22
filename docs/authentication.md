# Authentication

The authentication using the IaC in Rivery is a `token` based authentication.
Every token is referenced under the hood the combination of `account` and `environment` ids, the specific token 
can make requests to.

In order to create a new token, please [check out our docs](https://rivery.io/docs/api-documentation).

## Token scopes
Every token includes a list of the scope it allowed to in the platform.
The needed scopes for getting started with the running rivers, using the CLI are:

```markdown
    * me:list
    * river:execute
    * river:edit
    * river:list
    * river:delete
    * connection:edit
    * connection:list
    * connection:delete
```

## Named Profile

A named profile is a collection of settings and credentials that you can apply to a Rivery IaC CLI. 
When you specify a profile to run a command, the settings and credentials are used to run that command.
You can specify the "deault" profile, and other profiles have names that you can specify as a parameter on the command line. 

Each profile has its name and the configurations under it. Due to every API token refers
to specific `account`+`environment` inside your Rivery console, and every account+environment pair has
its own credentials, it is likely you'll have a profile per each `account`+`environment` coupling.

## Auth file

The profiles and other configuration kept saved under `~/.rivery/auth` file. 
Auth file lists all the configurations of all the profiles. 
It is created once you hit the `Rivery configure` command. 
By default the `default` profile is created after hiting the `confgure` command, 
but multiple profiles can be added to the file.

### `~/.rivery/auth` file structure

```yaml
profile_name:
  host: https://console.rivery.io
    # The host the CLI, using this profile, will make the request to. 
    # Host can be any host of rivery, such as the regular "console", or 'eu-west-1.console"
  region: us-east-2
    # The region of Rivery to request
  token: eyJhbGciOiJIUzI1NiIsImV4cCI6MTkzMjY2MjI1NC...
    # the token that had been configured using in this specific profile
```