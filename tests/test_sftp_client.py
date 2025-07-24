from unittest.mock import MagicMock

from sftp_auto_sync.connection.sftp_client import SFTPManager


def test_connect_success(mock_ssh_client_class, mock_load_credentials) -> None:
    mock_load_credentials.return_value = {
        "hostname": "localhost",
        "port": 22,
        "username": "user",
        "password": "pass",
    }

    mock_client_instance = MagicMock()
    mock_sftp_instance = MagicMock()
    mock_client_instance.open_sftp.return_value = mock_sftp_instance
    mock_ssh_client_class.return_value = mock_client_instance

    manager = SFTPManager()
    client, sftp = manager.connect()

    assert client is not None
    assert sftp is not None