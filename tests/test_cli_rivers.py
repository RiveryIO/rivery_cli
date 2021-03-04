from unittest import TestCase
from click.testing import CliRunner
from rivery_cli.cli import base


class Test(TestCase):

    def setUp(self) -> None:
        """ Create a CLIRunner"""

        self.runner = CliRunner(echo_stdin=True)

    def check_exit_code(self, exit_code):
        assert exit_code == 0

    def test_import_rivers(self):
        """ Tes import rivers """

        resp = self.runner.invoke(cli=base.cli,
                                  args=['rivers', 'import', '--riverId=60005bb389f000001ef047aa', '--path=./logics/'],
                                  catch_exceptions=False)

        self.check_exit_code(resp.exit_code)
        print(resp)

    def test_push_rivers(self):
        resp = self.runner.invoke(
            cli=base.cli,
            args=['rivers', 'push', r'--paths=c:\workspace\rivery_cli\logics\60005bb389f000001ef047aa.yaml'],
            catch_exceptions=False)
        print(resp)
