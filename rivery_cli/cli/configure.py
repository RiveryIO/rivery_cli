import click
import pathlib
import os
import yaml

HOME_DIR = os.path.abspath(os.path.expanduser('~'))

BASE_RIVERY_DIR = os.path.join(HOME_DIR, '.rivery')
BASE_CONFIG_PATH = os.path.join(BASE_RIVERY_DIR, 'config')
BASE_AUTH_PATH = os.path.join(BASE_RIVERY_DIR, 'auth')


@click.command('configure')
@click.help_option()
@click.option('--profile', required=False)
@click.pass_obj
def create_auth_file(ctx, **kwargs):
    """ Configure new profile and the authentication."""
    profile = kwargs.get('profile') or ctx.get('PROFILE') or 'default'
    click.secho(f'Configuring profile: {profile}')
    region = ctx.get('REGION')
    host = ctx.get('HOST')

    # Create ~/.rivery if not exists
    if not pathlib.Path(BASE_RIVERY_DIR).exists():
        pathlib.Path(BASE_RIVERY_DIR).mkdir(exist_ok=True)

    # Create ~/.rivery/auth if not exists
    auth_path = pathlib.Path(BASE_AUTH_PATH)
    if not auth_path.exists():
        auth_path.touch()

    with open(auth_path, 'r') as af:
        auth_config = yaml.safe_load(af) or {}

    # Check the config and write it if not exists
    profile_auth = auth_config.get(profile) or {}
    token = auth_config.get('token') or ''
    host = host or auth_config.get('host')
    if not region:
        region = auth_config.get('region')

    # Prompt for token and region
    token = click.prompt(f'Please enter your token. ({"*" * 6 + token[6:]})', type=str, show_default=False,
                        default=profile_auth.get('token'))
    region = click.prompt(f'Choose your Region ({region})', show_choices=True, default=region, show_default=True,
                          type=str)
    # Construct the host
    host_ = host or f"https://{(region + '.') if region and region != 'us-east-2' else ''}console.cli.io"
    # Make the profile yaml
    auth_config[profile] = {"token": token,
                            "host": host_,
                            "region": region}

    # Write it to a file
    with open(auth_path, 'w') as af:
        yaml.safe_dump(auth_config, stream=af)

    click.echo(f'Thank you for entering auth credentials. \n'
               f'Please check your profile at: {auth_path}')

if __name__ == '__main__':
    create_auth_file()