#!/usr/bin/python3

""" PICPAC picks and packs your pics

PICPAC recursively collects files inside the current directory and creates flat symlinks
inside a destination folder. If no arguments are passed, PICPAC selects only images and
puts symlinks under the home directory (~/.picpac). PICPAC avoids duplication on the basis
of file content not filename.

"""


# TODO: Optimize for speed.


from progressbar import ProgressBar
from os.path import isdir, expanduser
from argparse import ArgumentParser
from itertools import chain
from os import walk, getcwd, mkdir, access, W_OK
from logging import basicConfig, INFO, info, disable
from hashlib import md5
from pathlib import Path


# Verbose mode:
basicConfig(level=INFO, format='PICPAC %(message)s')

# Readability:
FILES = 2
DIR = 0

# Defaults:
DESTINATION_FOLDER = expanduser('~/.picpac')
VALID_EXTENTIONS = ['.jpg',
                    '.jpeg',
                    '.bmp',
                    '.gif',
                    '.tiff',
                    '.exif',
                    '.rif']


def parse():
    parser = ArgumentParser(description=__doc__)

    parser.add_argument('-v', '--verbose',
                        help='Turn verbose mode on',
                        default=False,
                        action='store_true')

    parser.add_argument('-s', '--source',
                        help='Absolute path to source folder',
                        default=getcwd(),
                        type=str)

    parser.add_argument('-d', '--destination',
                        help='Absolute path to destination folder',
                        default=DESTINATION_FOLDER,
                        type=str)

    parser.add_argument('-e', '--extensions',
                        help='Valid file extensions like .mp3 (with the dot)',
                        default=VALID_EXTENSIONS,
                        type=str,
                        metavar='EXT',
                        nargs='*')

    args = parser.parse_args()

    print('Source: %s' % args.source)
    print('Destination: %s.' % args.destination)
    print('File extensions: %s' % args.extensions)

    assert isdir(args.source), 'Invalid source path'
    assert all([ext[0] is '.' for ext in args.extensions]), 'Invalid file extension'

    return args


def pick_n_pack(source, destination, extensions):
    tree = list(walk(source))

    progress = get_progress_bar(tree)
    progress.start()

    files = 0
    symlinks = 0

    for node in tree:
        info('found directory: %s', node[DIR])

        for file in node[FILES]:
            files += 1
            progress.update(files)

            if Path(file).suffix in extensions:
                image = Path(node[DIR], file)
                hashed = Path(destination, encode(image))

                if not hashed.exists():
                    hashed.symlink_to(image)
                    info('added symlink: %s', hashed)
                    symlinks += 1
                else:
                    info('skipped duplicate: %s', image)

    progress.finish()
    print('Done: %s symlinks.' % symlinks)


def get_progress_bar(tree_):
    file_nodes = [node_[FILES] for node_ in tree_]
    total_files = len(list(chain(*file_nodes)))
    return ProgressBar(maxval=total_files)


def encode(filepath):
    h = md5()

    with open(str(filepath), 'rb') as f:
        chunk = 0
        while chunk != b'':
            chunk = f.read(1024)
            h.update(chunk)

    return h.hexdigest() + filepath.suffix


class DestinationError(Exception):
    pass


def initialize(destination):
    if isdir(destination):
        if not access(destination, W_OK):
            raise PermissionError('Cannot write to %s' % destination)
    else:
        try:
            mkdir(destination)
        except OSError:
            raise DestinationError('Cannot create %s' % destination)


def configure(verbose):
    if not verbose:
        disable(INFO)


if __name__ == '__main__':
    p = parse()

    configure(p.verbose)
    initialize(p.destination)
    pick_n_pack(p.source, p.destination, p.extensions)

