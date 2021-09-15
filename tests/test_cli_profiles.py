from unittest import TestCase
from click.testing import CliRunner
from rivery_cli.cli import profiles
import pathlib


class Test(TestCase):

    def setUp(self) -> None:
        """ Create a CLIRunner"""

        self.runner = CliRunner(echo_stdin=True)

    def test_fetch_logs(self):
        """ Test fetch logs """

        resp = self.runner.invoke(cli=profiles.show_profiles,
                                  catch_exceptions=False,
                                  color=True)
        assert resp.output

    def tearDown(self) -> None:
        project = pathlib.Path('project.yaml')
        models = pathlib.Path('models')
        project.unlink(missing_ok=True)
        models.unlink(missing_ok=True)