from rivery_cli.converters import yaml_converters, LogicConverter
from rivery_cli import client
from rivery_cli.globals import global_settings, global_keys
import click
import pathlib
from rivery_cli.utils import path_utils, decorators

RIVER_TYPE_CONVERTERS = {
    "logic": LogicConverter
}


@click.group('rivers')
def rivers(*args, **kwargs):
    """ Rivers operations (push, pull)"""
    pass


@rivers.command('push')
@click.option('--paths', type=str, required=True, help='Provide yaml paths')
@click.pass_obj
@decorators.error_decorator
def push(ctx, *args, **kwargs):
    """ Push current yaml paths into a rivers in the platform."""
    profile_name = ctx['PROFILE']
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session
    all_rivers = {}
    paths = kwargs.get('paths', '')
    for path in paths.split(','):
        # Split the paths string to path
        # Search for specific yaml if the path is dir
        yaml_paths = path_utils.PathUtils(path).search_for_files('**/*.yaml')
        for yaml_path in yaml_paths:
            click.echo(f'Start Creating River from Yaml file in {yaml_path.absolute()}', color='green')
            try:
                # Make a base converter by the yaml path. The base converter already reads the yaml by path.
                converter = yaml_converters.YamlConverterBase(yaml_path)
            except Exception as e:
                click.echo(f'Problem on reading the definition yaml files. Error: {str(e)}', color='red')
                if ctx.get('IGNORE_ERRORS'):
                    click.echo('The --ignoreError set to True. Continue to the next river.', color='orange')
                    continue
                else:
                    raise

            # Get the entity type from the converter definition
            river_type = converter.definition.get('type')
            content = converter.content
            # Check if there's a river converter that is already supported. If not, raise an error.
            river_converter = RIVER_TYPE_CONVERTERS.get(river_type)
            if not river_converter:
                raise NotImplementedError(f'River type of {river_type} is not supported for now. '
                                          f'Supported river types: {RIVER_TYPE_CONVERTERS.keys()}.')
            # Make the river convertion to entity def that will be sent to the API.
            entity = river_converter(content=content).convert()
            if converter.entity_name in all_rivers:
                raise KeyError(f'Duplicate Entity Name: {converter.entity_name}.'
                               f'Already exists in {all_rivers.get(converter.entity_name, {}).get("path")}')
            # Add the entity definition as the base dictionary of "all rivers".
            # This is based on the "entity_name" here.
            all_rivers[converter.entity_name] = {
                "client_entity": entity,
                "converter": river_converter,
                "cross_id": entity.get('cross_id'),
                "_id": entity.get('_id'),
                "is_new": False if entity.get('_id') else True,
                "yaml": converter.full_yaml,
                "path": yaml_path
            }

    for entity_name, entity in all_rivers.items():
        click.echo(f'Pushing {entity_name} to Rivery')
        is_new = entity.get('is_new')
        yaml_ = entity.get('yaml')
        river_converter = entity.get('converter')
        try:
            resp = session.save_river(
                data=entity.get('client_entity'),
                create_new=is_new
            )
        except Exception as e:
            if ctx['IGNORE_ERRORS']:
                click.echo(f'Problem on push entity "{entity_name}" into Rivery. Error: {str(e)}')
            raise

        yaml_ = river_converter._import(resp)
        yaml_converters.YamlConverterBase.write_yaml(path=entity.get('path'), content=yaml_)

    click.echo(f'Pushed {len(all_rivers)} rivers.', color='green')

    return


@rivers.command('import')
@click.option('--riverId', type=str, required=False,
              help="""Please provide at least one river id.
              River Id can be found in the river url, structured as this:
              https://<cli-console>/#/river/<accountId>/<environmentId>/river/**<RiverId>**""")
@click.option('--groupName', type=str, required=False,
              help="""
              Please provide a group name of rivers.
              The group name can be found near every river, in the river screen at cli.
              """)
@click.option('--path', type=str, required=False, help=""" The path you want to import into.""")
@click.pass_obj
def import_(ctx, *args, **kwargs):
    """ Import current river(s) into a yaml files.
    Get a group or river ID in the right env and account
    and create a yaml file per the source"""
    click.echo(kwargs)
    click.echo(f'Currently - these are the only river types can be imported: '
               f'{",".join(global_settings.AVAILABE_RIVER_TYPES)}.')

    target_path = kwargs.get('path')
    river_id = kwargs.get('riverid')
    group_name = kwargs.get('groupname')

    assert target_path, 'Please provide --path parameter in order to import the rivers'
    if not river_id and not group_name:
        raise AssertionError('One missing: --riverId or --groupName. Check help for more info.')

    target_path = pathlib.Path(target_path)

    if not target_path.exists():
        click.echo(f'Path {target_path} doesnt exist. Creating...')
        target_path.mkdir(parents=True)

    # get profile name
    profile_name = ctx['PROFILE']
    # make client and session
    click.echo(f'Connecting to river. Profile: {profile_name}')
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session

    if session:
        # Get the rivers list by the filter
        rivers_list = []
        all_rivers = {}
        if group_name:
            click.echo(f'Searching for rivers with criteria of groupName={group_name}')
            rivers_list = session.list_rivers(group=group_name)
        elif river_id:
            click.echo(f'Searching for rivers with criteria of riverId={river_id}')
            rivers_list = session.list_rivers(river_id=river_id)

        click.echo(f'Got {len(rivers_list)} rivers.')

        for river_ in rivers_list:
            river_def = river_.get(global_keys.RIVER_DEF)
            river_type_id = river_def.get('river_type_id')
            if river_type_id not in RIVER_TYPE_CONVERTERS:
                click.echo(F'{river_def.get("river_type_name")} River {river_.get("river_name")}('
                           F'{river_.get("cross_id")}) is not supported yet. Passing it.')
                continue
            else:
                river_def = session.get_river(river_id=river_.get(global_keys.CROSS_ID))
                river_name = river_def.get(global_keys.RIVER_DEF, {}).get('river_name')
                cross_id = river_def.get(global_keys.CROSS_ID)

                try:
                    click.echo(f'Importing {river_name}({cross_id})')
                    target_yml_path = target_path.joinpath(cross_id + '.yaml')
                    click.echo(f'Target Yaml will be: {target_yml_path}')
                    converter_ = RIVER_TYPE_CONVERTERS.get(river_type_id)
                    resp = converter_._import(def_=river_def)
                    yaml_converters.YamlConverterBase.write_yaml(content=resp, path=target_yml_path)

                except Exception as e:
                    click.echo(f'Failed to convert river '
                               f'`{river_name}`({cross_id})'
                               f'Because of an error: {str(e)}')
                    return

    else:
        raise ConnectionError('Problem on creating session to Rivery. '
                              'Please check if the host and token are configured correctly.')


if __name__ == '__main__':
    rivers()
