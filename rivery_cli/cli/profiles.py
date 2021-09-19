import click
import prettytable
import yaml
from rivery_cli.utils import decorators
from rivery_cli.globals import global_settings


@click.group('profiles')
def profiles():
    """ List and get profiles details """
    pass


@profiles.command('get')
@decorators.error_decorator
@click.pass_obj
def show_profiles(ctx, **kwargs):
    """ Get the list of profiles available in the client from ~/.rivery/auth file """

    # Read the auth config file
    with open(global_settings.BASE_AUTH_PATH, 'r') as af:
        auth_configs = yaml.safe_load(af)

    # Create a pretty table for return in the end of the command
    pt = prettytable.PrettyTable(['Profile Name', 'Host', 'Region', 'Token'])
    pt.set_style(prettytable.PLAIN_COLUMNS)
    for profile, conf in auth_configs.items():
        # Add the profile details to the pretty table row.
        pt.add_row([profile, conf.get('host'), conf.get('region'), ('*' * 6 + conf.get('token', '')[-6:-1])])

    pt.max_width = 45
    pt.padding_width = 0
    pt.left_padding_width = 2
    pt.right_padding_width = 2
    pt.border = True
    click.echo(pt.get_string())


if __name__ == '__main__':
    profiles()
