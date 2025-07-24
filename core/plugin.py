import os
import posixpath
import stat
import tempfile

from git import Repo

from utils.logger import success, error, info


def remove_sftp_dir_recursive(sftp, path):
    files = sftp.listdir_attr(path)
    for entry in files:
        entry_path = posixpath.join(path, entry.filename)
        if stat.S_ISDIR(entry.st_mode):
            remove_sftp_dir_recursive(sftp, entry_path)
            sftp.rmdir(entry_path)
        else:
            sftp.remove(entry_path)
    pass

def upload_dir_to_sftp(sftp, local_path, path):
    for item in os.listdir(local_path):
        if item.endswith(".git"):
            continue

        local_item_path  = posixpath.join(local_path, item)
        remote_item_path = posixpath.join(path, item)

        if os.path.isdir(local_item_path):
            try:
                sftp.mkdir(remote_item_path)
            except IOError:
                pass
        else:
            sftp.put(local_item_path, remote_item_path)

class Plugin:
    def __init__(self, name, path):
        self.name      = name
        self.path      = path
        self.is_valid  = False  # structure
        self.is_owned  = False
        self.is_github = False
        self.authors   = None
        self.explain   = None
        self.updated   = False

    def update(self, sftp):
        github_token = os.getenv("GITHUB_TOKEN")
        github       = os.getenv("GITHUB")
        repo_url     = f"https://{github_token}@github.com/{github}/{self.name}.git"

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                info(f"{self.name}: Clonage du repository dans le dossier temporaire...")

                local_repo_path = posixpath.join(tmpdir, self.name)
                Repo.clone_from(repo_url, local_repo_path)

                info(f"{self.name}: Repository cloné avec succès sur le dossier temporaire")

                info(f"{self.name}: Suppression des fichiers SFTP...")
                remove_sftp_dir_recursive(sftp, self.path)

                info(f"{self.name}: Upload des fichiers mis à jour...")
                upload_dir_to_sftp(sftp, local_repo_path, self.path)

                success(f"{self.name}: Plugin mis à jour avec succès.")
                self.updated = True
            except Exception as e:
                error(f"{self.name}: échec de la mise à jour {e}")
        pass

    def setExplain(self):
        if self.is_valid and self.is_owned and self.is_github:
            self.explain = lambda: success(f"{self.name}: prêt pour synchronisation")
            return

        if not (self.is_valid or self.is_owned or self.is_github):
            self.explain = lambda: info(f"{self.name}: aucune vérification effectuée")
            return

        states = []
        issues = []

        if self.is_valid:
            states.append("structure valide")
        else:
            issues.append("structure invalide")

        if self.is_owned:
            states.append("vous appartient")
        else:
            issues.append("ne vous appartient pas")

        if self.is_github:
            states.append("lié à votre GitHub")
        else:
            issues.append("n'est pas sur GitHub")

        if issues:
            # jamais tasra normalement
            if len(issues) == 3:
                log_func = error
                message = " et ".join(issues)
            elif any("structure invalide" in issue for issue in issues):
                log_func = error
                if states:
                    message = " et ".join(states) + " mais " + " et ".join(issues)
                else:
                    message = " et ".join(issues)
            else:
                log_func = info
                if states:
                    message = " et ".join(states) + " mais " + " et ".join(issues)
                else:
                    message = " et ".join(issues)
        else:
            log_func = info
            message = " et ".join(states)

        self.explain = lambda: log_func(f"{self.name}: {message}")