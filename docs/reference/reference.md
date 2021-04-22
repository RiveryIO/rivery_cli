# Basic Reference

Rivers are referenced and defined, using the CLI, as `.yaml` files. Every river can be set as one file
which indicates its configurations, references, state etc. All of the `.yaml` files and the other references 
(like `.sql` files) are laying under the same project, and this is the way they can reference to each other.

## The Basic `.yaml` structure
Every `.yaml` file has a basic structure that required to be declared.
Here's the basic structure of every rivery entity yaml:

```yaml
rivery:
  cross_id: 5d1a068f7bedeb52687eef4d  # uuid of the entity in Rivery. Should be filled in the first deploy (push).
  entity_name: string # entity name. Entity name can be used for reference to other entities under "models" directory. 
  type: river # entity type. 
  version: 0.1 # entity definition version
  definition:
    # Every entity has a "definition" block which include the
    # breakdown of all elements in the entity
    <river definition block>
```