from unittest import TestCase
from rivery_cli.utils import path_utils


class TestPathUtils(TestCase):
    def setUp(self) -> None:
        self.path_ = path_utils.PathUtils(r'.logics/')

    def test_search_for_files(self):
        self.path_.search_for_files('*.yaml')
