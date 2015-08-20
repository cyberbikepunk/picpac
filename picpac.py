""" Picpac picks and packs my pics!

Picpac recursively collects images inside a source folder and generates symlinks
inside a destination folder. Usage: picpac <source_dir> <destination_dir>. Yo!

"""

from argparse import ArgumentParser
from os import walk
from pathlib import Path


DIR = 0
FILES = 2

VALID_EXTENTIONS = {
    '.jpg',
    '.jpeg',
    '.bmp',
    'gif',
    '.tiff',
    '.exif',
    '.rif'
}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()

    tree = walk(args.source)
    for node in tree:
        for file in node[FILES]:
            if Path(file).suffix in VALID_EXTENTIONS:
                image = Path(node[DIR], file)
                link = Path(args.destination, image.name)
                if not link.exists():
                    link.symlink_to(image)
