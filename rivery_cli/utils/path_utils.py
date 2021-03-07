import pathlib


class PathUtils:
    """ Utils set for a path """
    def __init__(self, path):
        self.path = pathlib.Path(path)

    def search_for_files(self, fnmatch_='**\*.yaml'):
        """ Get the whole paths under a self.path, recursivly, using glob and by searching after fnmatch_ phrase.
            :returns LIST[pathlib.Path] of file paths lays under the search criteria.

        """
        all_paths = []
        if self.path.is_dir():
            for path in self.path.glob(fnmatch_):
                all_paths.append(
                    pathlib.Path(path.relative_to(self.path))
                )
        else:
            all_paths = [pathlib.Path(self.path)]

        return all_paths

    def is_absolute(self):
        return self.path.is_absolute()

    def is_dir(self):
        return self.path.is_dir()

    def as_posix(self):
        return self.path.as_posix()

if __name__ == '__main__':
    path = PathUtils(r'c:\workspace\rivery_cli')
    print(path.search_for_files('**/*.yaml'))


