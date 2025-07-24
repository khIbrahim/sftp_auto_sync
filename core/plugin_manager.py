import os
import posixpath

import requests
import yaml

from .plugin import Plugin
from utils.logger import error


def is_valid(plugin: Plugin, sftp) -> bool:
    try:
        files = sftp.listdir(plugin.path)
        return "plugin.yml" in files and "src" in files
    except IOError:
        plugin.explain = lambda: error(f"{plugin.name} structure invalide")
        return False

def parse_authors(info: dict):
    authors = set()
    for key in ["author", "authors"]:
        val = info.get(key)
        if isinstance(val, str):
            authors.add(val.lower())
        elif isinstance(val, list):
            authors.update(a.lower() for a in val if isinstance(a, str))
    return list(authors)

def is_owned(plugin: Plugin, sftp, valid_authors) -> bool:
    try:
        with sftp.open(posixpath.join(plugin.path, "plugin.yml"), "r") as f:
            info = yaml.safe_load(f.read().decode())
    except (IOError, yaml.YAMLError) as e:
        plugin.is_valid = False
        plugin.reason = lambda: error(f"{plugin.name} plugin.yml invalide: {e}")
        return False

    name = info.get("name")
    if not name:
        return False

    plugin.authors = parse_authors(info)
    valid = [a.lower() for a in valid_authors]
    return any(a in valid for a in plugin.authors)

def is_plugin_on_github(plugin_name) -> bool:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    resp = requests.get(f"https://api.github.com/repos/{os.getenv("GITHUB")}/{plugin_name}", headers=headers)
    return resp.status_code == 200

def analyze_plugin(sftp, name, plugins_dir, authors, target_plugins, check_valid=True, check_author=True, check_github=True, update=False):
    path = posixpath.join(plugins_dir, name)
    plugin = Plugin(name, path)

    if check_valid:
        plugin.is_valid = is_valid(plugin, sftp)
    if check_author:
        plugin.is_owned = is_owned(plugin, sftp, authors)
    if check_github:
        plugin.is_github = is_plugin_on_github(plugin.name)

    plugin.setExplain()

    target_plugins = [pl.lower() for pl in target_plugins]
    plugin_name    = plugin.name.lower()

    if update and (plugin_name in target_plugins ) and plugin.is_github:
        plugin.update(sftp)

    return plugin