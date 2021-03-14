from unittest import TestCase
from click.testing import CliRunner
from rivery_cli.cli import base
import pathlib


class Test(TestCase):
    def setUp(self) -> None:
        """ Create a CLIRunner"""

        self.runner = CliRunner(echo_stdin=True)

    def check_exit_code(self, exit_code):
        assert exit_code == 0

    def test_init(self):
        self.runner.invoke(cli=base.cli,
                           args=['init'],
                           catch_exceptions=False)

    def tearDown(self) -> None:
        prjct = pathlib.Path('./project.yaml')
        prjct.unlink(missing_ok=True)