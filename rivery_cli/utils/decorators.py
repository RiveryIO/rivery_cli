import click



def error_decorator(func):
    """
    Ignore error and handling decorator for the entire CLI.
    If the user pass in the context that he want to ignore errors, the pass the error,
    else, raise a specific error message + warning that he can set the command with --ignoreErrors
    """
    def wrapped(ctx=None, *args, **kwargs):
        if not ctx:
            ctx = args[0]

        try:
            func(ctx or {}, *args, **kwargs)
        except Exception as e:
            click.echo(f'Got an error from command: {str(e)}', color='red')
            if ctx.get('PASS_ERRORS', False):
                return
            else:
                click.echo('If wanted, you can use the --ignoreErrors argument. ',
                           color='red')
                raise

    return wrapped