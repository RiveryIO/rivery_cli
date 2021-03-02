from click.testing import CliRunner
from rivery_cli.base import cli


def test_configure():
    runner = CliRunner()
    runner.invoke(cli, [r'--host=https://dev.app.rivery.io', '--profile=dev', '--region=us-east-2', 'configure'])



def test_run():
    runner = CliRunner()
    runner.invoke(cli, ['push', r'--paths=c:\workspace\rivery_cli\logics\logic_river.yaml'],
                  catch_exceptions=False)


if __name__ == '__main__':
    # test_configure()
    test_run()
