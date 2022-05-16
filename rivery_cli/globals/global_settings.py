import os

# SET THE VERSION
__version__ = "0.4.0"

# CONSTANTS
AVAILABE_RIVER_TYPES = ['logic']

SCHEMA_VALIDATION_PATH = 'converters/schemas'

DEFAULT_MODELS = 'models'
DEFAULT_SQLS = 'sqls'
DEFAULT_MAPPING = 'maps'
DEFAULT_CODE = 'code'

# DIRS AND PATHS
HOME_DIR = os.path.abspath(os.path.expanduser('~'))
BASE_RIVERY_DIR = os.path.join(HOME_DIR, '.rivery')
BASE_CONFIG_PATH = os.path.join(BASE_RIVERY_DIR, 'config')
BASE_AUTH_PATH = os.path.join(BASE_RIVERY_DIR, 'auth')

# SUBCOMMANDS CONFIG
PROFILE_MESSAGE_IGNORE_SUBCOMMANDS = ['init', 'profiles']