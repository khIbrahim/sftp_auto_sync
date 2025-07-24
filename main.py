import posixpath, stat
from sftp_connection import create_sftp_connection
from utils.config_loader import load_config
from core.plugin_manager import analyze_plugin
from utils.logger import debug, success, warn, info

config         = load_config()
authors        = config.authors
plugins_dir    = config.plugins_dir
modes          = config.modes or []
target_plugins = config.target_plugins or []
mode_flags     = config.mode_flags or []

sftp, client = create_sftp_connection()

plugin_names = [name for name in sftp.listdir(plugins_dir) if stat.S_ISDIR(sftp.stat(posixpath.join(plugins_dir, name)).st_mode)]

total = len(plugin_names)
plugins = []

debug(f"Analyse de {total} plugins")
for i, name in enumerate(plugin_names, 1):
    debug(f"[{i}/{total}] Analyse de {name}")
    plugin = analyze_plugin(
        sftp=sftp,
        name=name,
        plugins_dir=plugins_dir,
        authors=authors,
        target_plugins=target_plugins,
        check_author=mode_flags["owned"],
        check_valid=mode_flags["valid"],
        check_github=mode_flags["github"],
        update=mode_flags["update"],
    )

    if plugin:
        plugins.append(plugin)
        if plugin.explain:
            plugin.explain()
    print("-" * 80)

if mode_flags["valid"]: debug(f"{sum(p.is_valid for p in plugins)} plugins valides")
if mode_flags["owned"]: warn(f"{sum(p.is_owned for p in plugins)} vous appartiennent")
if mode_flags["github"]: info(f"{sum(p.is_github for p in plugins)} sont sur GitHub (et vous appartiennent)")
if mode_flags["update"]: success(f"{sum(p.updated for p in plugins)} ont été update")

sftp.close()
client.close()
