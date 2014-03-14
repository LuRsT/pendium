import git


class GitWrapper(object):
    def __init__(self, path):
        self.basepath = path

    def get_repo(self):
        try:
            repo = git.Repo(self.basepath)
            return repo
        except ImportError:
            raise Exception('Could not import git module')

    def delete(self, path=None):
        if path is None:
            return None

        repo = self.get_repo()
        repo.git.rm(path, r=True)
        repo.git.commit(m='Path deleted')

        if self.git_repo_has_remote():
            repo.git.push()

    def save(self, path=None, comment=None):
        if path is None:
            return None

        if not comment or comment is None:
            comment = 'New content version'

        repo = self.get_repo()
        repo.git.add(path)
        repo.git.commit(m=comment)

        if self.git_repo_has_remote():
            repo.git.push()

    def git_repo_has_remote(self):
        try:
            if self.get_repo().git.remote():
                return True

            return False
        except:
            return False

    def file_refs(self, filepath, count=15):
        """
        Returns a list of the commit hashes where this file was changed
        count is how many refs will we return
        """
        try:
            refs = self     \
                .get_repo() \
                .git.log(
                    '--pretty=oneline',
                    '--format=%H',
                    filepath)

            return refs.split("\n")[:count]
        except:
            return []

    def show(self, ref, filepath=None):
        """
        Returns a git show of the ref.
        Can also get a filepath and show that file in that commit
        """
        show_string = ref
        if filepath:
            show_string = ':'.join([ref, filepath])

        try:
            return self.get_repo().git.show(show_string)
        except:
            return ''
