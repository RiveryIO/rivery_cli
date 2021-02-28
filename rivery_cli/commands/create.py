from rivery_cli.converters import yaml_converters
from rivery import client
import click
from rivery_cli.base import cli


@cli.command('push')
@click.option('--paths', type=str, required=True, help='Provide yaml paths')
@click.option('--stack-name', type=str, required=False, help='The stack name to create and push into Rivery.')
@click.pass_obj
def run_paths(ctx, paths='', **kwargs):
    profile_name = ctx.profile
    stack_name = kwargs.get('stack_name')
    rivery_client = client.Client(name=stack_name or profile_name)
    paths = paths or ''
    all_entities = []
    for yml_path in paths.split(','):
        print('Start Creating River from Yaml file')
        converter_ = yaml_converters.YamlConverterBase(yaml_path=yml_path)
        entity = converter_.run()
        print('Login to Rivery')
        print('Create River')
        all_entities.append(entity)
    rivery_client.prepare(entities=all_entities)
    rivery_client.deploy()

    return
