import signal
import stat
import sys
from typing import List

from connection.sftp_client import SFTPManager
from core.plugin_manager import analyze_plugin
from utils.config_loader import load_config, validate_environment
from utils.exceptions import ConfigurationError, AutoSyncError
from utils.logger import debug, warn, info, error, success


class AutoSync:
    def __init__(self):
        self.sftp_manager = None
        self.config       = None
        self.interrupted  = None

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        warn(f"Signal {signum} reçu, arrêt en cours...")
        if self.sftp_manager:
            self.sftp_manager.close()
        self.interrupted = True
        sys.exit(0)

    def initialize(self) -> bool:
        try:
            validate_environment()

            self.config = load_config()
            info(f"Configuration initialisée")
            debug(f"Modes: {self.config.modes}")
            debug(f"Target plugins: {self.config.target_plugins}")

            self.sftp_manager = SFTPManager(timeout=self.config.sftp_timeout, max_retries=self.config.max_retries)

            return True
        except ConfigurationError as e:
            warn(f"Erreur de configuration: {e}")
            return False
        except Exception as e:
            warn(f"Erreur lors de l'initialisation: {e}")
            return False

    def get_plugin_names(self, sftp) -> List[str]:
        try:
            entries      = sftp.listdir_attr(self.config.plugins_dir)
            plugins_name = []

            for entry in entries:
                if stat.S_ISDIR(entry.st_mode):
                    plugins_name.append(entry.filename)

            return sorted(plugins_name)

        except Exception as e:
            warn(f"Erreur lors de la récupération des noms de plugins: {e}")
            return []

    def analyze_plugins(self, sftp, plugin_names: List[str]) -> List:
        plugins = []
        total = len(plugin_names)

        for i, name in enumerate(plugin_names, 1):
            if self.interrupted:
                break

            debug(f"[{i}/{total}] Analyzing {name}")
            try:
                plugin = analyze_plugin(
                    sftp=sftp,
                    name=name,
                    plugins_dir=self.config.plugins_dir,
                    authors=self.config.authors,
                    target_plugins=self.config.target_plugins,
                    check_valid=self.config.mode_flags["valid"],
                    check_author=self.config.mode_flags["owned"],
                    check_github=self.config.mode_flags["github"],
                    update=self.config.mode_flags["update"],
                )

                if plugin:
                    plugins.append(plugin)
                    if plugin.explain:
                        plugin.explain()
            except Exception as e:
                error(f"Failed to analyze plugin {name}: {e}")

            print("-" * 80)

        return plugins

    def run(self) -> int:
        # 0 succès, 1 erreur
        try:
            if not self.initialize():
                return 1

            client, sftp = self.sftp_manager.connect()

            try:
                plugin_names = self.get_plugin_names(sftp)
                if not plugin_names:
                    warn(f"Aucun plugin trouvé dans {self.config.plugins_dir}")
                    return 1

                debug(f"Plugins trouvés: {plugin_names}")

                debug(f"Analyse de {len(plugin_names)} plugins dans {self.config.plugins_dir}...")
                plugins = self.analyze_plugins(sftp, plugin_names)

                if not plugins:
                    warn("Aucun plugin valide trouvé.")
                    return 1

                self.print_summary(plugins)

                return 0
            finally:
                self.sftp_manager.close()
        except ConnectionError as e:
            error(f"Erreur de connexion SFTP: {e}")
            return 1
        except AutoSyncError as e:
            error(f"Erreur lors de l'exécution de l'auto-sync: {e}")
            return 1
        except KeyboardInterrupt as e:
            warn(f"Exécution interrompue {e}")
            return 1
        except Exception as e:
            error(f"Erreur inattendue: {e}")
            return 1

    def print_summary(self, plugins) -> None:
        if self.config.mode_flags["valid"]: debug(f"{sum(p.is_valid for p in plugins)} plugins valides")
        if self.config.mode_flags["owned"]: warn(f"{sum(p.is_owned for p in plugins)} vous appartiennent")
        if self.config.mode_flags["github"]: info(f"{sum(p.is_github for p in plugins)} sont sur GitHub (et vous appartiennent)")
        if self.config.mode_flags["update"]: success(f"{sum(p.updated for p in plugins)} ont été update")

def main() -> int:
    app = AutoSync()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())