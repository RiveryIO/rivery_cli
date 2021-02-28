import click


def base_decorator(func):
    """ Base decorator that includes the basic options that can be exposed to every other requests.
        @ Must have a click.command() in the specific function, before this decorator.
     """

    def wrapped(*args, **kwargs):

        return func(*args, **kwargs)

    return wrapped