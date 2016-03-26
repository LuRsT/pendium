from os.path import dirname as get_dirname
from os.path import join as join_path
from os.path import realpath as get_realpath
from sys import argv

from pendium import run


try:
    _CONFIG_FILE = argv[1]
except IndexError:
    _CONFIG_FILE = None


def main():
    if _CONFIG_FILE:
        current_directory = get_dirname(get_realpath(__file__))
        config_absolute_path = join_path(current_directory, _CONFIG_FILE)
    else:
        config_absolute_path = None

    run(config_absolute_path)


main()
