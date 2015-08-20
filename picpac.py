""" Picpac picks and packs pics!

Picpac recursively collects images inside a source folder and
generates corresponding symlinks inside a destination folder.

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
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()

    counter = 0
    tree = walk(args.source)
    for node in tree:
        for file in node[FILES]:
            if Path(file).suffix in VALID_EXTENTIONS:
                counter += 1
                image = Path(node[DIR], str(counter) + '_' + file)
                link = Path(args.destination, image.name)
                if not link.exists():
                    link.symlink_to(image)

    print('Picpic has created %s symlinks.' % counter)
