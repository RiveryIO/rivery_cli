from rivery_cli import RiverySession
import os
from rivery_cli import global_keys
import yaml
import pathlib
import logging

HUMAN_LOG_FORMAT = '%(process)d - %(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
logging.basicConfig(format=HUMAN_LOG_FORMAT,
                    level=logging.INFO)

VERSION = 0.1


class RiverError(Exception):
    def __init__(self, e):
        super(RiverError, self).__init__("Error occurred during update or creating a river. Error: {}".format(
            str(e)))


class ConnectionError(Exception):
    def __init__(self, e):
        super(ConnectionError, self).__init__("Error occurred during update or creating a connection. Error: {}".format(
            str(e)))


class RiveryError(Exception):
    def __init__(self, e):
        super(RiveryError, self).__init__("Error occurred while updating or create entity in Rivery. Error: {}".format(
            str(e)))


class Client:
    """ Rivery Client class.
        Handling the creating/updating/deleting of entities in Rivery
    """

    HOMEDIR = os.path.abspath(os.path.expanduser('~'))
    CLIENT_BASE_PATH = os.path.join(HOMEDIR, '.rivery')
    AUTH_FILE_PATH = os.path.join(CLIENT_BASE_PATH, global_keys.BASE_AUTH_FILE_NAME)
    CONFIG_FILE_PATH = os.path.join(CLIENT_BASE_PATH, global_keys.CONFIG_FILE_NAME)

    ENTITY_FUNC = {
        "push": {
            "river": RiverySession.save_river,
            "connection": RiverySession.create_connection
        },
        "get": {
            "river": RiverySession.get_river,
            "connection": RiverySession.get_connection
        }
    }

    CONNECTION_TYPES = {}

    PROFILES = {}

    def __init__(self, **kwargs):
        """ A Rivery client should get token as a basic credentials mechanism.
            The credentials of the client are determine by waterfall of 3 stages.
            The order in which the client searches for credentials is:

            1. Paramter "token" passed to the client.
            2. Environment variable (RIVERY_ACCESS_TOKEN)
            3. A auth file under "~/.rivery/auth"
        """
        self._base_dir = pathlib.Path(self.CLIENT_BASE_PATH)
        self._base_dir.mkdir(exist_ok=True)

        self.token = kwargs.get('token')
        self.debug = kwargs.get('debug') or False
        self.stack_path = kwargs.get('stack_path') or '.'
        self.stack_name = kwargs.get('name') or kwargs.get('stack_name') or kwargs.get('client_name')

        self.config = {}

        self._stack_path = pathlib.Path(self.stack_path).joinpath(self.stack_name+'.stack')
        self._config_path = pathlib.Path(self.CONFIG_FILE_PATH)
        if not self._config_path.exists():
            self._config_path.touch(exist_ok=True)

        self.host = kwargs.get('host')
        self.credentials = {
            "token": self.token,
            "host": self.host
        }
        self.stack_ = {}
        self.stack_entities = {}
        self.current_entities = {}
        self.profile = kwargs.get('profile') or 'default'
        self.session = None

        try:
            if self.profile not in self.PROFILES:
                self._make_session(force_new=kwargs.get('force_new_session'))
            else:
                self.session = self.PROFILES.get(self.profile)
        except Exception as e:
            raise RiveryError('Connecting to rivery error: {}'.format(str(e)))

        self._make_config()

    def _make_config(self):
        if self.config.get('logging', {}):
            logging.basicConfig(**self.config.get('logging'))
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    def _search_for_credentials(self, search_type='ENV_VAR'):
        """ Searching for token if it isn't passed """

        self.credentials['token'] = self.token
        self.credentials['host'] = self.host

        if search_type == 'ENV_VAR':
            # Search on ENV Var
            if not self.credentials.get('token'):
                self.token = os.environ.get(global_keys.ENV_VAR_TOKEN)
            if not self.credentials.get('host'):
                self.host = os.environ.get(global_keys.ENV_VAR_HOST)

            if not self.host or not self.token:
                self._search_for_credentials(search_type='AUTH_FILE')

        elif search_type == 'AUTH_FILE':
            # Search on auth file
            if os.path.exists(self.AUTH_FILE_PATH):
                with open(self.AUTH_FILE_PATH, 'r') as auth_f:
                    auth_dict = yaml.full_load(auth_f)
                    profile_ = auth_dict.get(self.profile, {})
                    if not self.credentials.get('token'):
                        self.token = profile_.get('token')
                    if not self.credentials.get('host'):
                        self.host = profile_.get('host')
                self.credentials['token'] = self.token
                self.credentials['host'] = self.host

    def _make_session(self, force_new=False):
        """ Create client session """
        # Search for the credentials if it wasnt provided in the class itself.
        if not self.token or not self.host:
            self._search_for_credentials()
        # Make new Rivery Session
        if force_new or not self.session:
            # Creating new Rivery Session
            logging.info(f'Connecting to host: {self.host or global_keys.DEFAULT_HOST}')
            self.session = RiverySession(token=self.token, host=self.host or global_keys.DEFAULT_HOST)
            self.session.connect()
            # self.session.list_connection_types()
            all_conn_props = {}

            self.PROFILES[self.profile] = self.session

            # Get the configuration from config file
            config = {}
            with open(self.CONFIG_FILE_PATH, 'r') as cnf:
                config = yaml.safe_load(cnf.read())
            self.config = config or {}
