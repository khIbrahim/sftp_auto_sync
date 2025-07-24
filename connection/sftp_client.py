import os
import socket
from contextlib import contextmanager
from getpass import getpass
from typing import Optional, Tuple

import paramiko
from dotenv import load_dotenv

from utils.exceptions import AuthentificationError
from utils.logger import debug, success, info, error


def load_credentials() -> dict:
    load_dotenv()

    def env_or_input(name: str, is_password = False, default: Optional[str] = None) -> str:
        val = os.getenv(name)
        if not val:
            prompt = f"Entrez la valeur de {name}: "
            if is_password:
                val = getpass(prompt)
            else:
                val = input(prompt)

        return val or default

    try :
        credentials = {
            "hostname": env_or_input("SFTP_HOST"),
            "port"    : int(env_or_input("SFTP_PORT", default="22")),
            "username": env_or_input("SFTP_USER"),
            "password": env_or_input("SFTP_PASS", is_password=True),
        }

        if not all([credentials["hostname"], credentials["port"], credentials["username"], credentials["password"]]):
            raise AuthentificationError("Les informations d'authentification SFTP sont incomplètes.")

        if not (1 <= credentials["port"] <= 65535):
            raise AuthentificationError("Le port SFTP doit être compris entre 1 et 65535.")

        return credentials
    except ValueError as e:
        raise AuthentificationError(f"Erreur de format des informations d'authentification SFTP: {e}")
    except Exception as e:
        raise AuthentificationError(f"Erreur de lecture des informations d'authentification SFTP: {e}")


def _cleanup_client(client: paramiko.SSHClient) -> None:
    try:
        client.close()
    except:
        pass


class SFTPManager:
    def __init__(self, timeout: int = 60, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

    def _cleanup(self) -> None:
        if self._sftp:
            try:
                self._sftp.close()
            except:
                pass
            self._sftp = None
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None

    def connect(self):
        if self._client and self._sftp:
            try:
                self._sftp.listdir()
                return self._client, self._sftp
            except:
                self._cleanup()

        creds  = load_credentials()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        max_retries = self.max_retries
        for attempt in range(max_retries):
            try:
                debug(f"Tentative de connexion au serveur SFTP {attempt + 1}/{max_retries}")

                client.connect(
                    hostname=creds["hostname"],
                    port=creds["port"],
                    username=creds["username"],
                    password=creds["password"],
                    timeout=self.timeout,
                    banner_timeout=30,
                    auth_timeout=30
                )

                sftp = client.open_sftp()
                sftp.get_channel().settimeout(self.timeout)

                sftp.listdir()

                success(f"La connexion au serveur SFTP a bien été établie")

                self._client = client
                self._sftp   = sftp

                return client, sftp
            except paramiko.AuthenticationException as e:
                _cleanup_client(client)
                raise AuthentificationError(f"Erreur d'authentification {e}")

            except (socket.timeout, socket.error) as e:
                _cleanup_client(client)
                if attempt == max_retries - 1:
                    raise ConnectionError(f"La connexion au serveur SFTP a échoué: {e}")
                info(f"Tentative de reconnexion au serveur SFTP {attempt + 1}/{max_retries} après une erreur de connexion: {e}")
        return None

    def close(self) -> None:
        self._cleanup()
        info("La connexion au serveur SFTP a été fermée")

    @contextmanager
    def connection(self):
        try:
            client, sftp = self.connect()
            yield client, sftp
        except Exception as e:
            error(f"Erreur lors de la connexion SFTP: {e}")
            raise

def create_sftp_connection(timeout: int = 60, max_retries: int = 3) -> Tuple[paramiko.SSHClient, paramiko.SFTPClient]:
    with SFTPManager(timeout, max_retries).connection() as (client, sftp):
        return client, sftp