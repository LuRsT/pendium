from os.path import dirname as get_dirname
from os.path import join as join_path
from os.path import realpath as get_realpath

from pendium import run
from click import command
from click import option
from click import argument


@command()
@option('--config', default=None, help='Config file')
@argument('wikipath')
def main(config, wikipath):
    run(config, wikipath)


if __name__ == '__main__':
    main()
