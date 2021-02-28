from click.testing import CliRunner
from rivery_cli.base import cli


def test_configure():
    runner = CliRunner()
    runner.invoke(cli, ['configure', r'--host=https://dev.app.rivery.io', '--profile=dev'])



def test_run():
    runner = CliRunner()
    runner.invoke(cli, args=['push',r'--paths=c:\workspace\rivery_cli\logics\logic_river.yaml','--profile=dev'],
                  catch_exceptions=False)


if __name__ == '__main__':
    # test_configure()
    test_run()
