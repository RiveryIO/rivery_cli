import csv
import time
from itertools import chain, repeat
from io import StringIO

import click
import click_spinner
import prettytable

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
        sleep_ = chain(repeat(1, 10), range(1, 30, 2),
                       repeat(30, 10))

        while not logs:
            logs_response = session.fetch_run_logs(run_id=run_id, query_id=query_id, return_full_response=True)

            click.echo(f'Logs query response is: {logs_response.status_code}')
            if logs_response.status_code == 200:
                return logs_response
            if logs_response.status_code != 202 and still_in_progress_msg not in logs_response.content.lower():
                raise Exception(f'Failed to fetch logs of run id: {run_id}.')

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
@click.option("--pretty", required=False, type=bool, default=False,
              help="""Should the output be in a pretty table format.""")
@click.pass_obj
@decorators.error_decorator
def download_run_logs(ctx, **kwargs):
    """ Download the logs of a given run id """
    profile_name = ctx.get('PROFILE')
    run_id = kwargs.get('runid')

    click.echo(f'Starting to download logs for run id {run_id} in profile: {profile_name}')
    rivery_client = client.Client(name=profile_name, profile=profile_name)
    session = rivery_client.session

    click.echo(f'Downloading logs of run id "{run_id}"')

    with click_spinner.spinner(force=True) as spinner:
        spinner.start()
        resp = fetch_run_logs(session, run_id)
        spinner.stop()

    click.echo(
        f'Run ID {run_id} logs fetched successfully.'
    )

    logs = str(resp.content).replace("\\r\\n", "\r\n")
    prettier = kwargs.get('pretty')

    if prettier:
        # Making the data prettier
        # Removing the last char (empty line)
        data = StringIO(logs[:-1])

        rd = csv.reader(data, delimiter=',')
        pt = prettytable.PrettyTable(next(rd))
        pt.set_style(prettytable.PLAIN_COLUMNS)
        for row in rd:
            pt.add_row(row)
        pt.max_width = 45
        pt.padding_width = 0
        pt.left_padding_width = 0
        pt.right_padding_width = 0
        pt.border = True
        logs = pt.get_string()

    file_path = kwargs.get('filepath')
    if file_path:
        click.echo(f'Saving logs to file: {file_path}')
        with open(file_path, "a") as f:
            f.write(logs)
    else:
        click.echo(f'Logs content: {logs}')


if __name__ == '__main__':
    activities()
