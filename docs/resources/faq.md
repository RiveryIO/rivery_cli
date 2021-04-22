# FAQ

## Which environment is best to push my YAMLs to?
It is a best practice to always push your `yaml` filess to 
your development environment and only then run deployment to production through the UI.

## When I import again using the same river cross ID will my `yaml` be overridden?
Yes, if you import again using the same river cross id, your yaml will be overridden,
and you might lose all references. After initial import, it is best practice making all river 
updates in the yaml and not the UI. 

## What happens if I don't specify --profile in my commands?
If you don't specify profile, the CLI will attempt to import/push using the default configuration.

## What happens if I push a river with the same river_id and cross_id to a different environment?
The river will be pushed to the new environemnt, as defined in the profile.

## How can I get more info about command running and extra logging?
Use `rivery --debug ..` option in your commands.