import click


def error_decorator(func):
    """
    Ignore error and handling decorator for the entire CLI.
    If the user pass in the context that he want to ignore errors, the pass the error,
    else, raise a specific error message + warning that he can set the command with --ignoreErrors
    """

    @click.pass_obj
    def wrapped(obj, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except click.Abort as e:
            raise
        except Exception as e:
            if obj:
                click.secho(f'Got an error from command: {str(e)}', fg='yellow')
                if obj.get('IGNORE_ERRORS', False):
                    click.secho('--ignoreErrors set. Passing by.', fg='green')
                    pass
                else:
                    click.secho('If wanted, you can use the --ignoreErrors argument. ',
                               fg='yellow')
                    raise
            else:
                raise

    return wrapped


def profile_decorator(func):
    """
    Profile decorator for adding --profile to every function
    """
    @click.option('--profile', help='The profile you want to work with, as defined in the auth file.')
    @click.pass_context
    def wrapped(ctx, *args, **kwargs):
        """ Warrped function """
        if ctx:
            ctx.ensure_object(dict)
            ctx.obj['PROFILE'] = kwargs.get('profile') or 'default'
        func(*args, **kwargs)

    return wrapped

