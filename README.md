# Pendium

A (com)Pendium for all your markdown files

This is a web app for all your markdown files, you can use it for reading them in web way, share them through the interwebs or you can even create a personal ( or not so personal ) wiki with just a bunch of files ( you can link them together nicely ).

### Requirements

* Flask
* Markdown

To install them all type this in your command line:

    pip install `cat requirements`

Note: Pendium was hacked in python 2.7, so use the appropriate command to install de dependencies e.g. in arch linux it's 'pip2'

### Running it

To use Pendium simply execute the pendium.py file

    python pendium.py

By the default config it should read the files from the wiki dir inside the pendium directory, change the directory in the config file or symlink your own dir.

Note: Pendium was hacked in python 2.7, so use the appropriate command to run it e.g. in arch linux it's 'python2'

### Roadmap

* ~~Discover a better style~~
* 404 pretty error
* Edit files
* Create files
* Sub wikis
* Keyboard shortcuts
* Grep search
* Git integration

### Notes

Uses [Twitter Bootstrap](http://twitter.github.com/bootstrap/) and [Font Awesome](http://fortawesome.github.com/Font-Awesome/).
