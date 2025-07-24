import os.path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import yaml
from yaml import YAMLError

from .exceptions import ConfigurationError
from .logger import warn


@dataclass
class Config:
    plugins_dir: str = "./plugins"
    authors: List[str] = field(default_factory=list)
    modes: List[str] = field(default_factory=list)
    target_plugins: List[str] = field(default_factory=list)
    github_timeout: int = 30
    sftp_timeout: int = 60
    max_retries: int = 3

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        valid_modes   = ["valid", "github", "owned", "update"]
        invalid_modes = set(self.modes) - set(valid_modes)
        if invalid_modes:
            raise ConfigurationError(f"Modes invalides: {invalid_modes}")

        if not isinstance(self.plugins_dir, str) or not self.plugins_dir.strip():
            raise ConfigurationError("plugins_dir n'est pas initialisé")

        if not isinstance(self.authors, list):
            raise ConfigurationError("authors doit être une liste")

        if not isinstance(self.target_plugins, list):
            raise ConfigurationError("target_plugins doit être une liste")

        if self.github_timeout <= 0 or self.sftp_timeout <= 0:
            raise ConfigurationError("Timeouts doit être une valeur positive.")

        if self.max_retries < 0:
            raise ConfigurationError("max_retries doit être une valeur positive.")

    @property
    def mode_flags(self) -> Dict[str, bool]:
        return {
            "valid": "valid" in self.modes,
            "owned": "owned" in self.modes,
            "github": "github" in self.modes,
            "update": "update" in self.modes,
        }

def load_config(config_path: Optional[str] = None) -> Config:
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.yml")

    if not os.path.exists(config_path):
        warn(f"Le fichier de configuration n'a pas été trouvé dans {config_path}, utilisation des valeur par défaut...")
        return Config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except YAMLError as e:
        raise ConfigurationError(f"Fichier config YAML invalide: {e}")
    except IOError as e:
        raise ConfigurationError(f"Une erreur s'est produite lors de l'ouverture du fichier de configuration {e}")

    try:
        config = Config(
            plugins_dir=data.get("plugins_dir", "./plugins"),
            authors=data.get("authors", []),
            modes=data.get("modes", []),
            target_plugins=data.get("target_plugins", []),
            github_timeout=data.get("github_timeout", 30),
            sftp_timeout=data.get("sftp_timeout", 60),
            max_retries=data.get("max_retries", 3),
        )

        return config

    except Exception as e:
        raise ConfigurationError(f"La validation de la configuration a échoué: {e}")

# def load_config():
#     import yaml, os
#     config_path = os.path.join(os.path.dirname(__file__), "..", "config.yml")
#     with open(config_path, "r") as f:
#         return yaml.safe_load(f)