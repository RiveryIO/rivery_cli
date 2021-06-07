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
@click.option("--filePath", required=False, type=str,
              help="""The file that the logs should be saved to.""")
@click.pass_obj
@decorators.error_decorator
def download_run_logs(ctx, **kwargs):
    """ Download the logs of a given run id """
    profile_name = ctx.get('PROFILE')
    run_id = kwargs.get('runid')

    click.echo(f'Starting to download logs for run id {run_id} in profile: {profile_name}')
    rivery_client = client.Client(name=profile_name)
    session = rivery_client.session

    click.echo(f'Downloading logs of run id "{run_id}"')

    with click_spinner.spinner(force=True) as spinner:
        spinner.start()
        resp = fetch_run_logs(session, run_id)
        spinner.stop()

    click.echo(
        f'Run ID {run_id} logs fetched successfully.'
    )
    file_path = kwargs.get('filepath')
    if file_path:
        click.echo(f'Saving logs to file: {file_path}')
        f = open(file_path, "a")
        f.write(str(resp.content))
        f.close()
    else:
        click.echo(f'Logs content: {resp.content}')


if __name__ == '__main__':
    activities()
