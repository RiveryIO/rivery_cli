import click


@click.group('rivery')
@click.option('--profile', required=False)
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
    print(ctx)
    ctx.color = True
    ctx.ensure_object(dict)
    ctx.obj["PROFILE"] = kwargs.get('profile')
    ctx.obj['DEBUG'] = kwargs.get('debug') or False
    ctx.obj['HOST'] = kwargs.get('host')
    ctx.obj['REGION'] = kwargs.get('region')


# The import is here, in order to make sure there's no rounding imports
from .commands import configure, create

# Adding commands
cli.add_command(configure.create_auth_file)
cli.add_command(create.run_paths)

if __name__ == '__main__':
    cli(obj={})
