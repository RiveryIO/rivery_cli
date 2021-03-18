import yaml
import click
import pathlib


def get_context():
    """ Get the context from click application"""
    try:
        return click.get_current_context(silent=True).obj or {}
    except:
        return {}


def import_model(loader, node):
    """ Import yaml from the specific paths in the project """
    ctx = get_context()
    models = ctx.get('MODELS_DIR') or pathlib.Path('./models')  # Path class

    scalar_ = loader.construct_scalar(node)
    with open(models.joinpath(scalar_), 'r') as yml_:
        return yaml.load(yml_, Loader=yaml.SafeLoader)


def import_sql(loader, node):
    """ Import yaml from the specific paths in the project """
    ctx = get_context()
    models = ctx.get('SQLS_DIR') or pathlib.Path('./sqls')  # Path class

    scalar_ = loader.construct_scalar(node)
    with open(models.joinpath(scalar_), 'r') as sql_:
        return sql_.read().strip()


def import_maps(loader, node):
    """ Import maps by relative path """
    ctx = get_context()
    maps = ctx.get('MAPS_DIR') or pathlib.Path('./maps')
    scalar_ = loader.construct_scalar(node)
    with open(maps.joinpath(scalar_), 'r') as fields:
        mapping_ = yaml.load(fields, Loader=yaml.SafeLoader)

    return mapping_.get('fields', []) or mapping_.get('mapping', [])


def import_yaql(loader, node):
    """Import yaql and make a recursive run on the yaml """
    param = loader.construct_sequence(node.value[0], deep=True)
    print(param)
    # do something with the param here
    return param



def get_loader():
    yaml.SafeLoader.add_constructor('!model', import_model)
    yaml.SafeLoader.add_constructor('$model', import_model)
    yaml.SafeLoader.add_constructor('!sql', import_sql)
    yaml.SafeLoader.add_constructor('$sql', import_sql)
    yaml.SafeLoader.add_constructor('!map', import_maps)
    yaml.SafeLoader.add_constructor('$map', import_maps)
    # yaml.SafeLoader.add_constructor('!ref', import_yaql)
    # yaml.SafeLoader.add_constructor('$ref', import_yaql)

    return yaml.SafeLoader
