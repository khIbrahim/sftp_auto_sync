import os
import paramiko
from dotenv import load_dotenv
from getpass import getpass
from utils.logger import success, info

def load_credentials():
    load_dotenv()
    def env_or_input(name, isPassword=False, default=None):
        val = os.getenv(name)
        if not val:
            prompt = f"{name} est vide, entrez sa valeur"
            val    = getpass(f"{prompt}: ") if isPassword else input(f"{prompt}: ")
        return val or default

    return {
        "hostname": env_or_input("SFTP_HOST"),
        "username": env_or_input("SFTP_USER"),
        "password": env_or_input("SFTP_PASS", isPassword=True),
        "port"    : int(env_or_input("SFTP_PORT", default=22)),
    }

def create_sftp_connection():
    creds  = load_credentials()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    info("Connexion au serveur SFTP...")
    client.connect(
        hostname=creds["hostname"],
        username=creds["username"],
        password=creds["password"],
        port=creds["port"],
    )

    sftp = client.open_sftp()

    success("Connexion réussie")

    return sftp, client