from importlib import resources

from jubeatools import song
from jubeatools.formats import LOADERS
from jubeatools.formats.guess import guess_format


def load_test_file(package: resources.Package, file: str) -> song.Song:
    with resources.as_file(resources.files(package) / file) as p:
        format_ = guess_format(p)
        load = LOADERS[format_]
        return load(p)
