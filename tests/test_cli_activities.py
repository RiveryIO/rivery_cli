from unittest import TestCase
from click.testing import CliRunner
from rivery_cli.cli import base
import pathlib


class Test(TestCase):

    def setUp(self) -> None:
        """ Create a CLIRunner"""

        self.runner = CliRunner(echo_stdin=True)
        self.runner.invoke(
            cli=base.cli,
            args=['init', '--profile=test']
        )

    def test_fetch_logs(self):
        """ Test fetch logs """

        resp = self.runner.invoke(cli=base.cli,
                                  args=['--profile=test', 'activities', 'logs', 'fetch',
                                        '--runId=395ff1a3110d4796bf5cf8a6753af0f8'],
                                  catch_exceptions=False,
                                  color=True)
        print(resp.content)

    def tearDown(self) -> None:
        project = pathlib.Path('project.yaml')
        models = pathlib.Path('models')
        project.unlink(missing_ok=True)
        models.unlink(missing_ok=True)
