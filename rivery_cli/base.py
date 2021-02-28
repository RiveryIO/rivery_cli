import click


class CLIContext(object):
    def __init__(self, profile='default',
                 region='us-east-2', host='https://console.rivery.io', debug=False,
                 **kwargs
                 ):
        self.profile = profile or 'default'
        self.region = region
        self.host = host
        self.debug = debug or False


@click.group('rivery')
@click.option('-P', '--profile', required=False)
@click.option(
    '--region',
    type=click.Choice(
        ['us-east-2', 'eu-west-1']),
    prompt=True, show_default=True, default='us-east-2')
@click.option('-h', '--host', default='https://console.rivery.io', required=False)
@click.option('--debug', is_flag=True, required=False, default=False)
@click.pass_context
def cli(ctx, **kwargs):
    """ Rivery CLI """
    if not kwargs.get('profile'):
        kwargs['profile'] = 'default'
    ctx.obj = CLIContext(
        **kwargs)


# The import is here, in order to make sure there's no rounding imports
from .commands import configure, create

# Adding commands
cli.add_command(configure.create_auth_file)
cli.add_command(create.run_paths)

if __name__ == '__main__':
    cli()
