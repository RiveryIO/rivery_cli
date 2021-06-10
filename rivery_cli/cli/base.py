import click
from rivery_cli.cli import rivers, configure, init, activities
import pathlib
import yaml
from rivery_cli.utils import decorators
from rivery_cli.globals import global_settings


def parse_project(ctx):
    """
    Parsing the project configuration into the click ctx . If no ctx, make the defaults.
    """
    runtime_dir = pathlib.Path('.').cwd()
    print(runtime_dir)

    ctx.obj['RUNTIME_CWD'] = runtime_dir
    ctx.obj['PROJECT_CONF_FILE'] = runtime_dir.joinpath('project.yaml')

    if not ctx.obj['PROJECT_CONF_FILE'].exists():
        click.secho(
            "Could not find a project.yaml file in the root dir of your project.\n" 
            "Please run `rivery init` prior running any command.\n", nl=True, fg='green')

    else:
        with open(ctx.obj['PROJECT_CONF_FILE'], 'r') as prj_conf:
            prj_ = yaml.load(prj_conf, Loader=yaml.SafeLoader)
        ctx.obj['MODELS_DIR'] = runtime_dir.joinpath(prj_.get('models', 'models'))
        ctx.obj['SQLS_DIR'] = runtime_dir.joinpath(prj_.get('sqls', 'sqls'))
        ctx.obj['MAP_DIR'] = runtime_dir.joinpath(prj_.get('maps', 'maps'))

    return ctx


# TODO: calculate the entities on the fly in the project by the context, and add the entities to ENTITIES dict.
def parse_entities(ctx):
    """
    Parsing the entities list by entity_name.
    Searches the entire dir or specific path, under MODELS_DIR, and create the entities context.
    Save the entities list by name:path dict under the ctx
    """
    raise NotImplementedError()


@click.group(name="rivery")
@click.version_option(global_settings.__version__, prog_name='Rivery CLI')
@click.option(
    '--region',
    type=click.Choice(
        ['us-east-2', 'eu-west-1']),
    show_default=True, default='us-east-2', required=False,
    help="The region of the profile to connect")
@click.option('--host', default='https://console.rivery.io', required=False,
              help="Connect to specific Rivery host (for example: https://eu-west-1.console.rivery.io)")
@click.option('--debug', is_flag=True, required=False, default=False,
              help="Show debug log")
@click.option('--ignoreErrors', is_flag=True, required=False, default=False,
              help="Ignore errors during run.")
@decorators.profile_decorator
@click.pass_context
def cli(ctx, **kwargs):
    """ Rivery CLI """
    if not kwargs.get('profile'):
        kwargs['profile'] = 'default'
    ctx.color = True
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand != 'init':
        ctx = parse_project(ctx)

    ctx.obj["PROFILE"] = kwargs.get('profile')
    ctx.obj['DEBUG'] = kwargs.get('debug') or False
    ctx.obj['HOST'] = kwargs.get('host')
    ctx.obj['REGION'] = kwargs.get('region')
    ctx.obj["IGNORE_ERRORS"] = kwargs.get('ignoreerrors') or False

    if ctx.obj['DEBUG'] is True:
        click.secho(f'Context details: \n' +
                    ",\n".join(["{}={}".format(key, val) for key, val in ctx.obj.items()]),
                    fg='magenta')


cli.add_command(init.init)
cli.add_command(rivers.rivers)
cli.add_command(activities.activities)
cli.add_command(configure.create_auth_file)

if __name__ == '__main__':
    cli(obj={})
