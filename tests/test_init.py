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
        prjct = pathlib.Path('./project.yaml')
        prjct.unlink(missing_ok=True)



class TestRivers(TestInit):
    def test_import_rivers(self):
        """ Tes import rivers """

        resp = self.runner.invoke(cli=base.cli,
                                  args=['rivers', 'import', '--riverId=60005bb389f000001ef047aa', '--path=logics/'],
                                  catch_exceptions=False,
                                  color=True)
        print(resp.stdout)

    def test_push_rivers(self):
        resp = self.runner.invoke(
            cli=base.cli,
            args=['rivers', 'push', r'--paths=logics'],
            catch_exceptions=False)
        print(resp)

    def test_help(self):
        resp = self.runner.invoke(cli=base.cli,
                                  args=['rivers', '--help'],
                                  catch_exceptions=True)
        assert resp.exit_code == 0, 'Failed on help'


if __name__ == '__main__':
    unittest.main()