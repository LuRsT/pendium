import git
from pendium.plugins import IVersionPlugin


class Git(IVersionPlugin):
    name = "Git"

    def configure(self, configuration):
        self.basepath = configuration.get('basepath', '')

    def get_repo(self):
        try:
            repo = git.Repo(self.basepath)
            return repo
        except ImportError:
            raise Exception("Could not import git module")


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
            comment = "New content version"

        repo = self.get_repo()
        repo.git.add(path)
        repo.git.commit(m=comment)

        if self.git_repo_has_remote():
            repo.git.push()

    def refresh(self):
        return self.get_repo().git.pull()

    def git_repo_has_remote(self):
        try:
            if self.get_repo().git.remote():
                return True
            else:
                return False
        except:
            return False


