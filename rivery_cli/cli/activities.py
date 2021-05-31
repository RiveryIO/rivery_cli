from rivery_cli import client
import click
from rivery_cli.utils import decorators
import click_spinner


@click.group('activities')
def activities(*args, **kwargs):
    """ Activities operations (Monitor runs)"""
    pass


@activities.group('logs')
def runs(*args, **kwargs):
    """ Runs operations (Download runs' logs)"""
    pass


def fetch_run_logs(session, run_id):
    """ Fetch the logs of a given run """
    try:
        resp = session.fetch_run_logs(run_id=run_id, return_full_response=True)
    except Exception as e:
        raise click.ClickException(f'Problem on running run_id "{run_id}". Error returned: {str(e)}')

    return resp


@runs.command("fetch")
@click.option("--runId", required=True, type=str,
              help="""The run id that will be used to filter the logs.""")
@click.pass_obj
@decorators.error_decorator
def download_run_logs(ctx, **kwargs):
    """ Download the logs of a given run id """
    profile_name = ctx.get('PROFILE')
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session
    run_id = kwargs.get('runid')

    click.echo(f'Download logs of run id "{run_id}"')

    with click_spinner.spinner(force=True) as spinner:
        spinner.start()
        resp = fetch_run_logs(session, run_id)
        spinner.stop()

    click.echo(
        f'Run ID {run_id} logs fetched successfully. '
        f'{resp.content}'
    )


if __name__ == '__main__':
    activities()
