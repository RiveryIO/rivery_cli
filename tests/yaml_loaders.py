import yaml
import click
import pathlib


def get_context():
    """ Get the context from click application"""
    try:
        return click.get_current_context(silent=True) or {}
    except:
        return {}

def import_model(loader, node):
    """ Import yaml from the specific paths in the project """
    ctx = get_context()
    models = ctx.get('MODELS_DIR') or pathlib.Path('entities')  # Path class

    scalar_ = loader.construct_scalar(node)
    with open(models.joinpath(scalar_), 'r') as yml_:
        yaml.load(yml_, Loader=yaml.SafeLoader)


def import_sql(loader, node):
    """ Import yaml from the specific paths in the project """
    ctx = get_context()
    models = ctx.get('SQLS_DIR') or pathlib.Path('./sqls')  # Path class

    scalar_ = loader.construct_scalar(node)
    with open(models.joinpath(scalar_), 'r') as sql_:
        return sql_.read()


def construct_loader():
    yaml.SafeLoader.add_constructor('!model', import_model)
    yaml.SafeLoader.add_constructor('!sql', import_sql)
    return yaml.SafeLoader


if __name__ == '__main__':
    loader = construct_loader()
    with open('entities/logic_river.yaml', 'r') as stream_:
        resp = yaml.load(stream_, loader)
    print(resp)
