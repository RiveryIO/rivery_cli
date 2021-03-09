import pathlib


class PathUtils:
    """ Utils set for a path """
    def __init__(self, path):
        self.path = pathlib.Path(path)

    @staticmethod
    def search_for_files(path, fnmatch_='**\*.yaml'):
        """ Get the whole paths under a self.path, recursivly, using glob and by searching after fnmatch_ phrase.
            :returns LIST[pathlib.Path] of file paths lays under the search criteria.

        """
        all_paths = []
        if path.is_dir():
            for path in path.glob(fnmatch_):
                all_paths.append(
                    pathlib.Path(path.relative_to(path))
                )
        else:
            all_paths = [pathlib.Path(path)]

        return all_paths

    def is_absolute(self):
        return self.path.is_absolute()

    def is_dir(self):
        return self.path.is_dir()

    def as_posix(self):
        return self.path.as_posix()

