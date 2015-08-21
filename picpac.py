""" PICPAC picks and packs pics!

PICPAC recursively collects files inside the current directory and creates flat symlinks
inside a destination folder. If no arguments are passed, PICPAC selects only images and
puts symlinks under the home directory (~/.picpac). PICPAC avoids duplication on the basis
of file content not filename. PICPAC is handy to keep playlists or slideshows up to date.

"""


from os.path import isdir, expanduser
from argparse import ArgumentParser
from os import walk, getcwd, mkdir
from pathlib import Path
from logging import basicConfig, DEBUG, debug
from hashlib import md5


# NB: this script has not been optimized for speed.


# Feedback
basicConfig(level=DEBUG)

# Readability
FILES = 2
DIR = 0
DOT = '.'

# Defaults
DESTINATION_FOLDER = expanduser('~/.picpac')
VALID_EXTENTIONS = ['.jpg',
                    '.jpeg',
                    '.bmp',
                    '.gif',
                    '.tiff',
                    '.exif',
                    '.rif']


def encode(filepath):
    h = md5()

    with open(str(filepath), 'rb') as f:
        chunk = 0
        while chunk != b'':
            chunk = f.read(1024)
            h.update(chunk)

    return h.hexdigest() + filepath.suffix


def parse():
    parser = ArgumentParser(description=__doc__)

    parser.add_argument('--source', '-s',
                        help='Absolute path to source folder',
                        default=getcwd(),
                        type=str)

    parser.add_argument('--destination', '-d',
                        help='Absolute path to destination folder',
                        default=DESTINATION_FOLDER,
                        type=str)

    parser.add_argument('--extensions', '-e',
                        help='Valid file extensions e.g. .jpg ',
                        default=VALID_EXTENTIONS,
                        type=str,
                        metavar='EXT',
                        nargs='*')

    args = parser.parse_args()
    debug('arguments: %s', args)

    assert isdir(args.source), 'Invalid source path'
    assert all([ext[0] is DOT for ext in args.extensions]), 'Invalid extension'

    return args


def pick_n_pack(source, destination, extensions):
    tree = walk(source)
    added = 0

    for node in tree:
        debug('directory: %s', node[DIR])
        for file in node[FILES]:
            if Path(file).suffix in extensions:
                image = Path(node[DIR], file)
                hashed = Path(destination, encode(image))
                if not hashed.exists():
                    hashed.symlink_to(image)
                    debug('added: %s', hashed)
                    added += 1
                else:
                    debug('skipping duplicate: %s', image)

    debug('symlinks: %s', added)
    return added


class DestinationError(Exception):
    pass


def initialize(destination):
    if not isdir(destination):
        try:
            mkdir(destination)
        except OSError:
            raise DestinationError('Cannot create %s' % destination)


if __name__ == '__main__':
    p = parse()
    initialize(p.destination)
    n = pick_n_pack(p.source, p.destination, p.extensions)
    print('Created %s symlinks' % n)
