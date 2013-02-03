# Pendium

A (com)Pendium for all your markdown files

This is a web app for all your markdown files, you can use it for reading them in web way, share them through the interwebs or you can even create a personal ( or not so personal ) wiki with just a bunch of files ( you can link them together nicely ).

[![Screenshot](http://i.imgur.com/gxCYN8Rl.png)](http://i.imgur.com/gxCYN8R.png)

Powered by Python 2.7

### Requirements

* Flask
* Markdown
* yapsy
* GitPython # Optional for git support
* docutils  # Optional for rest documents
* pygments  # Optional for python documents

### Setup

To get yourself up and running you only need to run these commands:

    git clone git://github.com/LuRsT/Pendium.git
    cd Pendium
    pip install `cat requirements.txt`

Note: Pendium was hacked in python 2.7, so use the appropriate command to install de dependencies e.g. in arch linux it's 'pip2'.
Note2: Remember to install the optional requirements in order to unleash the full power of Pendium.

##### Config

If you want to change the config, move the config.py\_example file to config.py

    mv config.py_example config.py

#### Git Support

Before you do anything be sure to enable git support in the config file ( config.py ):

    WIKI_GIT_SUPPORT = True

To get the git support, run these commands afterwards ( if you don't have a remote git repo, go to the next step ):

    cd wiki
    git init
    git remote add origin <your_remote_git_repo>
    git branch --set-upstream master origin/master
    git pull #Optional, just to check if everything is okay and to get your files immediately

##### Hey, I don't have a remote git repo, what do I do now?

I'm assuming you already have a remote git repo up and running on the previous step, if you do not, do this:

    cd <repo_dir>
    git init --bare

with this you made yourself a git repo, now run these:

    cd wiki_dir # by default: <pendium_dir>/wiki
    git clone <path_to_previous_repo> <path_to_wiki_folder>
    touch home.md
    git add home.md
    git commit -m "Initial commit"
    git push -u origin master

### Running it

To use Pendium simply execute the run.py file:

    python run.py

By default it should read the files from the wiki dir inside the pendium directory, change the directory in the config file or symlink your own dir.

Note: Pendium was hacked in python 2.7, so use the appropriate command to run it e.g. in arch linux it's 'python2'

### Roadmap

* ~~Discover a better style~~
* ~~Git integration~~
* ~~404 pretty error~~
* ~~Sub wikis~~
* ~~Grep-like search~~
* ~~Edit files~~
* ~~Create files~~
* ~~Create dirs~~
* ~~Delete files/dirs~~
* Better editor
* Version Control with plugins
* Keyboard shortcuts

### Notes

Uses [Twitter Bootstrap](http://twitter.github.com/bootstrap/) and [Font Awesome](http://fortawesome.github.com/Font-Awesome/).
