from unittest import TestCase
from rivery_cli.utils import path_utils
import pathlib

class TestPathUtils(TestCase):
    def test_search_for_files(self):
        path_ = pathlib.Path(r'.logics/')
        path_utils.PathUtils.search_for_files(path=path_, fnmatch_='*.yaml')
