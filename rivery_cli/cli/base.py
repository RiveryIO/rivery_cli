import click
from rivery_cli.cli import rivers, configure

@click.group()
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

cli.add_command(rivers.rivers)
cli.add_command(configure.configure)

if __name__ == '__main__':
    cli(obj={})