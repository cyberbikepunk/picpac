#!/usr/bin/python3

""" PICPAC picks and packs your pics

PICPAC recursively collects files inside the current directory and creates flat symlinks
inside a destination folder. If no arguments are passed, PICPAC selects only images and
puts symlinks under the home directory (~/.picpac). PICPAC avoids duplication on the basis
of file content not filename.

"""


from sys import stdout
from os.path import isdir, expanduser
from argparse import ArgumentParser
from itertools import chain
from os import walk, getcwd, mkdir, access, W_OK
from logging import basicConfig, INFO, info, disable
from hashlib import md5
from pathlib import Path


# TODO: Optimize for speed.


# Verbose mode:
basicConfig(level=INFO, format='PICPAC %(message)s')

# Readability:
FILES = 2
DIR = 0

# Defaults:
DESTINATION_FOLDER = expanduser('~/.picpac')
VALID_EXTENSIONS = ['.jpg',
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


def pick_n_pack(source, destination, extensions, verbose):
    tree = list(walk(source))
    total_files = get_total_files(tree)

    file_nb = 0
    symlinks_nb = 0

    for node in tree:
        info('found directory: %s', node[DIR])

        for file in node[FILES]:
            file_nb += 1

            if not verbose:
                show_progress(file_nb, total_files)

            if Path(file).suffix in extensions:
                original = Path(node[DIR], file)
                hashed = Path(destination, encode(original))

                if not hashed.exists():
                    hashed.symlink_to(original)
                    symlinks_nb += 1
                    info('added symlink: %s', hashed)
                else:
                    info('skipped duplicate: %s', original)

    print('Done: %s symlinks.' % symlinks_nb)


def show_progress(file_nb, total_files, length=50):
    progress = int(file_nb / total_files * length)
    remainder = '.' * (length - progress)
    counter = str(file_nb) + ' / ' + str(total_files)

    stdout.flush()
    stdout.write('\r' + 'Processing: ' + ' [' + '#' * progress + remainder + '] ' + counter)

    if file_nb == total_files:
        print()


def get_total_files(tree):
    files = [node[FILES] for node in tree]
    return len(list(chain(*files)))


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
    pick_n_pack(p.source, p.destination, p.extensions, p.verbose)

