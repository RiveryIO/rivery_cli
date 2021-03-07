import click
from rivery_cli.cli import rivers, configure
import pathlib
import yaml


def parse_project(ctx):
    """Parsing the project configuration into the click ctx """
    runtime_dir = pathlib.Path('.').cwd()
    print(runtime_dir)

    ctx.obj['RUNTIME_CWD'] = runtime_dir
    ctx.obj['PROJECT_CONF_FILE'] = runtime_dir.joinpath('project.yaml')

    if not ctx.obj['PROJECT_CONF_FILE'].exists():
        click.echo('Could not find a project.yaml file in the root dir.')
        raise click.ClickException('Could not find a project.yaml file in the root dir.')

    with open(ctx.obj['PROJECT_CONF_FILE'], 'r') as prj_conf:
        prj_ = yaml.load(prj_conf)
    ctx.obj['MODELS_DIR'] = runtime_dir.joinpath(prj_.get('models', 'models'))
    ctx.obj['SQLS_DIR'] = runtime_dir.joinpath(prj_.get('sqls', 'sqls'))
    ctx.obj['MAP_DIR'] = runtime_dir.joinpath(prj_.get('maps', 'maps'))

    return ctx


@click.group()
@click.option(
    '--region',
    type=click.Choice(
        ['us-east-2', 'eu-west-1']),
    prompt=True, show_default=True, default='us-east-2', required=False, prompt_required=False)
@click.option('--host', default='https://console.rivery.io', required=False)
@click.option('--debug', is_flag=True, required=False, default=False)
@click.pass_context
def cli(ctx, **kwargs):
    """ Rivery CLI """
    if not kwargs.get('profile'):
        kwargs['profile'] = 'default'
    ctx.color = True
    ctx.ensure_object(dict)
    ctx = parse_project(ctx)

    ctx.obj["PROFILE"] = kwargs.get('profile')
    ctx.obj['DEBUG'] = kwargs.get('debug') or False
    ctx.obj['HOST'] = kwargs.get('host')
    ctx.obj['REGION'] = kwargs.get('region')

cli.add_command(rivers.rivers)
cli.add_command(configure.create_auth_file)

if __name__ == '__main__':
    cli(obj={})
