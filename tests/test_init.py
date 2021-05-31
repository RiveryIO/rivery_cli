from unittest import TestCase
import unittest
from click.testing import CliRunner
from rivery_cli.cli import base
import pathlib


class TestInit(TestCase):
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
        project = pathlib.Path('./project.yaml')
        project.unlink(missing_ok=True)
