from rivery_cli.converters import yaml_converters, LogicConverter
from rivery_cli import client
from rivery_cli.globals import global_settings, global_keys
import click
import pathlib
from rivery_cli.utils import path_utils, decorators
import time
import itertools

RIVER_TYPE_CONVERTERS = {
    "logic": LogicConverter
}

STATUS_TRANS = {
    "E": "Error",
    "D": "Success",
    "R": "Running",
    "W": "Waiting",
    "P": "Preparing"
}

END_STATUSES = ['D', 'E']


@click.group('rivers')
def rivers(*args, **kwargs):
    """ Rivers operations (push, pull/import)"""
    pass


@rivers.command('push')
@click.option('--paths', type=str, required=True, help='Provide the yaml, or base path to push')
@click.pass_obj
@decorators.error_decorator
def push(ctx, *args, **kwargs):
    """ Push current yaml paths into a rivers in the platform."""
    profile_name = ctx.get('PROFILE')
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session
    all_rivers = {}
    paths = kwargs.get('paths', '')
    for path in paths.split(','):
        # Split the paths string to path
        # Search for specific yaml if the path is dir
        path = pathlib.Path(path)
        if not path.is_absolute():
            path = (ctx['MODELS_DIR'].joinpath(path)).absolute()

        yaml_paths = path_utils.PathUtils.search_for_files(path, f'**\*.yaml')
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
                "is_new": False if river_converter.cross_id else True,
                "yaml": converter.full_yaml,
                "path": yaml_path
            }

    for entity_name, entity in all_rivers.items():
        click.echo(f'Pushing {entity_name} to Rivery')
        river_converter = entity.get('converter')
        try:
            resp = session.save_river(
                data=entity.get('client_entity'),
                create_new=entity.get('is_new')
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
    if not target_path.is_absolute():
        target_path = (ctx['MODELS_DIR'].joinpath(target_path)).absolute()

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

        no_of_rivers_to_import = len(rivers_list)
        click.echo(f'Got {no_of_rivers_to_import} rivers.')

        if no_of_rivers_to_import > 0:
            # Make an agreement prompt confimration
            click.confirm(text=f'There are {no_of_rivers_to_import} rivers that chosen to be imported. '
                               'Any current entity definition '
                               'you have in the path chosen will be updated by this operation.'
                               'Are you sure you want to proceed? (Y/N)',
                          default=False,
                          abort=True,
                          prompt_suffix='(Y/N)',
                          show_default=True
                          )

            # Make an import progress nar
            with click.progressbar(iterable=rivers_list, length=no_of_rivers_to_import,
                                   label='Rivers imported', show_percent=True, show_eta=False,
                                   fill_char='R', empty_char='-', color='blue', ) as bar:
                time.sleep(1)

                # Run for any river in the list
                for idx_, river_ in enumerate(rivers_list):
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
                            bar.update(idx_+1)
                        except Exception as e:
                            raise click.ClickException(f'Failed to convert river '
                                                       f'`{river_name}`({cross_id})'
                                                       f'Because of an error: {str(e)}. Aborting')
        else:
            click.echo('Nothing to import here. Bye bye!')

    else:
        raise ConnectionError('Problem on creating session to Rivery. '
                              'Please check if the host and token are configured correctly.')


@rivers.command('run')
@click.option('--riverId', required=True, type=str,
              help="""Please provide at least one river id to run.
              River Id can be found in the river url, structured as this:
              https://<cli-console>/#/river/<accountId>/<environmentId>/river/**<RiverId>**""")
@click.option('--entityName', required=False, type=str)
@click.option('--waitForEnd', required=False, is_flag=True)
@click.pass_obj
def run(ctx, **kwargs):
    """ Run a river whitin the current profile (account+environment). Gets a riverid key, with the river id to run
        and just run it in the platform.
    """
    river_id = kwargs.get('riverid')
    entity_name = kwargs.get('entityname')
    if not river_id and not entity_name:
        raise click.ClickException('Please provide one of the above - riverId or entityName')
    # get profile name
    profile_name = ctx['PROFILE']
    rivery_client = client.Client(name=profile_name)

    session = rivery_client.session
    try:
        click.echo(f'Running river "{river_id}"')
        resp = session.run_river(river_id=river_id)
    except Exception as e:
        raise click.ClickException(f'Problem on running river "{river_id}". Error returned: {str(e)}')

    if kwargs.get('waitforend'):
        click.echo(f"--waitForEnd set to true, so waiting for the river to end. River: {river_id}")
        if resp.get('run_id'):
            wait_for_end(session, run_id=resp.get('run_id'))
        else:
            raise click.ClickException(f'Did not recieved any run_id from the run method. '
                                       f'The response is: {", ".join(["{}={}".format(k, v) for k, v in resp.items()])}')
    else:
        click.echo(f'Initiated Run of {river_id}. Run_id: {resp.get("run_id")}. '
                   f'If you wish to check the run status,'
                   f' please send the "run" command with --runId={resp.get("run_id")}.')


def check_run_status(session, run_id):
    """ Send check run method"""
    try:
        resp = session.check_run(run_id=run_id)
    except Exception as e:
        raise click.ClickException(f'Problem on running run_id "{run_id}". Error returned: {str(e)}')

    return resp


def wait_for_end(session, run_id):
    """
    Waiting for the run to end with D/E.
    """
    resp = check_run_status(session, run_id)
    river_id = resp.get('river_id')
    status = resp.get('river_run_status') or 'W'
    start_time = time.time()
    max_time = 3600 * 2
    sleep_chain = itertools.chain(range(1, 10), range(2, 30, 3), itertools.repeat(30))
    while status not in END_STATUSES:
        if time.time() - start_time > max_time:
            click.echo(f'Exhausted of checking the river "{river_id}" after {max_time} seconds. '
                       f'You can check this out manually using the "run" command.')
            return

        time_to_sleep = next(sleep_chain)
        click.echo(f'Run {run_id} of River "{river_id}", did not complete yet. Status: {STATUS_TRANS.get(status)}. '
                   f'Sleeping for {time_to_sleep} seconds until the next check.')

        time.sleep(time_to_sleep)
        resp = check_run_status(session, run_id)
        river_id = resp.get('river_id')
        status = resp.get('river_run_status') or 'W'
    else:
        click.echo(f'River {river_id} completed with {status} status. '
                   f'{"Error Message: {}".format(str(resp.get("river_run_message")))}')


@rivers.command("run-status")
@click.option("--runId", required=True, type=str,
              help="""The run id to check the status on.""")
@click.option('--waitForEnd', required=False, type=str)
@click.pass_obj
def check_run(ctx, **kwargs):
    """" Check the run status """
    profile_name = ctx.get('PROFILE')
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session
    run_id = kwargs.get('runid')

    click.echo(f'Checking Run Id "{run_id}"')
    if kwargs.get('waitforend'):
        click.echo(f'--waitForEnd set to true, so waiting for the river to end. run id: {run_id}"')
        wait_for_end(session, run_id)
    else:
        resp = check_run_status(session, run_id)
        status = resp.get('river_run_status') or 'W'
        click.echo(f'Run {run_id} is with  {STATUS_TRANS.get(status)}. {resp.get("river_run_message")} ')


if __name__ == '__main__':
    rivers()
