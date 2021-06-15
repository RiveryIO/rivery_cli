from itertools import chain, repeat
import time

import click
import click_spinner

from rivery_cli import client
from rivery_cli.utils import decorators


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
        response = session.fetch_run_logs(run_id=run_id, return_full_response=True)

        # Get the query id from the response header
        query_id = response.headers['queryid']

        if not query_id:
            raise Exception(f'Did not receive any query id parameter for run: {run_id}.')

        logs = None
        still_in_progress_msg = "downloading logs is still in progress"
        while not logs:
            logs_response = session.fetch_run_logs(run_id=run_id, query_id=query_id, return_full_response=True)

            click.echo(f'Logs query response is: {logs_response.status_code}')
            if logs_response.status_code == 200:
                return logs_response
            if logs_response.status_code != 202 and still_in_progress_msg not in logs_response.content.lower():
                raise Exception(f'Failed to fetch logs of run id: {run_id}.')

            sleep_ = chain(repeat(1, 10), range(1, 30, 2),
                           repeat(30, 10))
            next_sleep = next(sleep_)
            click.secho(f'Waiting for logs query to be completed. Run ID: {run_id}. Sleeping for {next_sleep} seconds.', color='green')
            if next_sleep:
                time.sleep(next_sleep)
            else:
                raise Exception(f'Exhausted of waiting for the logs of run id: {run_id}.')

    except Exception as e:
        raise click.ClickException(f'Problem on running run_id "{run_id}". Error returned: {str(e)}')

    return response


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
        with open(file_path, "a") as f:
            f.write(str(resp.content))
    else:
        click.echo(f'Logs content: {resp.content}')


if __name__ == '__main__':
    activities()
