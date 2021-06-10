from unittest import TestCase
from click.testing import CliRunner
from rivery_cli.cli import base


class Test(TestCase):

    def setUp(self) -> None:
        """ Create a CLIRunner"""

        self.runner = CliRunner(echo_stdin=True)
        self.runner.invoke(
            cli=base.cli,
            args=['init', '--profile=test']
        )

    def test_import_rivers(self):
        """ Test import rivers """

        resp = self.runner.invoke(cli=base.cli,
                                  args=['--profile=test', 'rivers', 'import', '--riverId=60005bb389f000001ef047aa', '--path=logics/'],
                                  catch_exceptions=False,
                                  color=True)
        print(resp.stdout)

    def test_push_rivers(self):
        resp = self.runner.invoke(
            cli=base.cli,
            args=['rivers', 'push', r'--paths=logics'],
            catch_exceptions=False,
            input='Y')
        print(resp)

    def test_help(self):
        resp = self.runner.invoke(cli=base.cli,
                                  args=['rivers', '--help'],
                                  catch_exceptions=True)
        assert resp.exit_code == 0, 'Failed on help'

    def test_run_river(self):
        resp = self.runner.invoke(cli=base.cli,
                                  args=['rivers', 'run', 'fire', '--riverId=6050b2f2f5682c1be691a5a9', '--waitForEnd'])
        assert resp
