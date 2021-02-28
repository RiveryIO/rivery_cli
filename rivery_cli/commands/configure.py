import click
from click import Choice
from rivery_cli.base import cli
import pathlib
import os
import yaml

HOME_DIR = os.path.abspath(os.path.expanduser('~'))

BASE_CONFIG_PATH = os.path.join(HOME_DIR, '.rivery/config')
BASE_AUTH_PATH = os.path.join(HOME_DIR, '.rivery/auth')


@cli.command('configure')
@click.pass_obj
def create_auth_file(ctx, **kwargs):
    """ Create a auth file """
    profile = ctx.profile or 'default'
    region = ctx.region
    auth_path = pathlib.Path(BASE_AUTH_PATH)
    if not auth_path.exists():
        auth_path.touch()

    with open(auth_path, 'r') as af:
        auth_config = yaml.safe_load(af) or {}

    profile_auth = auth_config.get(profile) or {}
    token = auth_config.get('token') or ''
    host = auth_config.get('host') or ''

    token = click.prompt(f'Please enter your token. ({"*" * 6 + token[6:]})', type=str, show_default=False,
                        default=profile_auth.get('token'))
    region = click.prompt(f'Choose your Region ({region})', show_choices=True)

    host_ = host or f"https://{region + '.' if region else ''}console.rivery.io"

    auth_config[profile] = {"token": token,
                            "host": host_}

    with open(auth_path, 'w') as af:
        yaml.dump(auth_config, stream=af)

    click.echo(f'Thank you for entering auth credentials. Please check your profile at: {auth_path.name}')
