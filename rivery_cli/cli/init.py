import click
import yaml
import pathlib
import os
from rivery_cli.globals.global_settings import DEFAULT_MODELS, DEFAULT_SQLS, DEFAULT_MAPPING
from collections import OrderedDict
from rivery_cli.utils import decorators


@click.command('init')
@click.help_option()
@click.option('--name', required=False, type=str, help="Project name")
@click.option('--models', required=False, type=str, help="The Models (entities) directory", default=DEFAULT_MODELS)
@click.option('--sqls', required=False, type=str, help="The sqls (queries) directory", default=DEFAULT_SQLS)
@click.option('--maps', required=False, type=str, help="The mapping directory", default=DEFAULT_MAPPING)
@decorators.profile_decorator
def init(**kwargs):
    """ Make a initiation project.yaml in the current path"""
    project_name = kwargs.get('name')
    models = kwargs.get('models') or DEFAULT_MODELS
    sqls = kwargs.get('sqls') or DEFAULT_SQLS
    maps = kwargs.get('maps') or DEFAULT_MAPPING

    click.echo('Initiating new Rivery project!', color='blue')


    if not project_name:
        project_name = click.prompt(
            text='Please choose your project name.',
            default='my-rivery-project',
            show_default=True,
            type=str)

    current_project = pathlib.Path('./project.yaml')
    if current_project.exists():
        click.echo('There is an existing project in the current directory. '
                   'Please update it or choose a new project directory.')
        return

    new_project = {
        "name": project_name,
        "models": models,
        "sqls": sqls,
        "maps": maps,
        "version": 1.0
    }

    click.echo(f'Writing new project "{project_name}" under {current_project.absolute()}')

    with open(current_project, 'w') as prjct_yml:
        yaml.dump(data=new_project, stream=prjct_yml, sort_keys=False)

    click.echo('Project initiated! Welcome to Rivery CLI! '
               'In order to getting started, please refer our docs at https://docs.rivery.io',
               color='green')
