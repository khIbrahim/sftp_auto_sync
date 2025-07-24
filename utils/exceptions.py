class AutoSyncError(Exception):
    pass

class ConfigurationError(AutoSyncError):
    pass

class AuthentificationError(AutoSyncError):
    pass