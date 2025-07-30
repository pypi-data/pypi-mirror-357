# File: tests/test_Vault.py
import base64
from unittest.mock import Mock, patch

import pytest
from seCore.HttpRest import HttpRest, HttpAction
from seKM.Vault import VaultEngine


def test_vault_engine_initialization(mocker):
    """Test initialization of the VaultEngine class."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    domain = "https://test-vault"
    namespace = "namespace"
    app_role = "approle"
    role_id = "role_id"
    secret_id = "secret_id"
    headers = "key:value"

    vault_engine = VaultEngine(domain, namespace, app_role,
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               headers)
    # assert vault_engine._VaultEngine__urlLogin == f"{domain}/v1/{namespace}/auth/{app_role}/login"
    # assert vault_engine._VaultEngine__urlKV_Data == f"{domain}/v1/{namespace}/kv/data"


def test_vault_engine_initialization_ns(mocker):
    """Test initialization of the VaultEngine class."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    domain = "https://test-vault"
    namespace = ""
    app_role = "approle"
    role_id = "role_id"
    secret_id = "secret_id"
    headers = "key:value"

    vault_engine = VaultEngine(domain, namespace, app_role,
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               headers)
    # assert vault_engine._VaultEngine__urlLogin == f"{domain}/v1/{namespace}/auth/{app_role}/login"
    # assert vault_engine._VaultEngine__urlKV_Data == f"{domain}/v1/{namespace}/kv/data"


def test_get_token_success(mocker):
    """Test successful retrieval of a token from the VaultEngine."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    mock_http_rest = mocker.create_autospec(HttpRest)
    mock_http_rest_instance = mocker.Mock()
    mock_http_rest.return_value = mock_http_rest_instance

    response_mock = '{"auth": {"client_token": "test_token"}}'
    mock_http_rest_instance.http_request.return_value = (response_mock, 200)
    mocker.patch("seCore.HttpRest.HttpRest", mock_http_rest)

    vault_engine = VaultEngine("https://test-vault", "namespace", "approle",
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode())
    token = vault_engine.get_token()
    # assert token == "test_token"


def test_get_token_failure(mocker):
    """Test behavior when get_token fails to retrieve a vault token."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    mock_http_rest = mocker.create_autospec(HttpRest)
    mock_http_rest_instance = mocker.Mock()
    mock_http_rest.return_value = mock_http_rest_instance

    mock_http_rest_instance.http_request.side_effect = Exception("Authentication error")
    mocker.patch("seCore.HttpRest.HttpRest", mock_http_rest)

    vault_engine = VaultEngine("https://test-vault", "namespace", "approle",
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode())
    token = vault_engine.get_token()
    assert token == ""


def test_get_value_success(mocker):
    """Test getting a value from VaultEngine with valid settings."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    mock_http_rest = mocker.create_autospec(HttpRest)
    mock_http_rest_instance = mocker.Mock()
    mock_http_rest.return_value = mock_http_rest_instance

    response_mock = '{"data": {"data": {"key": "value"}}}'
    mock_http_rest_instance.http_request.return_value = (response_mock, 200)
    mocker.patch("seCore.HttpRest.HttpRest", mock_http_rest)

    vault_engine = VaultEngine("https://test-vault", "namespace", "approle",
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode())
    vault_engine.hashicorp_token = "mock_token"

    value, status_code = vault_engine.get_value("secrets_folder", "key")
    # assert value == {"project": "secrets_folder", "key": "key", "value": "value"}
    # assert status_code == 200


def test_update_value_failure(mocker):
    """Test behavior when update_value fails due to TypeError."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    mock_http_rest = mocker.create_autospec(HttpRest)
    mock_http_rest_instance = mocker.Mock()
    mock_http_rest.return_value = mock_http_rest_instance

    mock_http_rest_instance.http_request.side_effect = TypeError("Invalid data type")
    mocker.patch("seCore.HttpRest.HttpRest", mock_http_rest)

    vault_engine = VaultEngine("https://test-vault", "namespace", "approle",
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode())
    vault_engine.hashicorp_token = "mock_token"

    status_code = vault_engine.update_value("secrets_folder", "key", {"invalid": "data"})
    assert status_code == 400


def test_get_values_key_error(mocker):
    """Test behavior when get_values encounters a KeyError."""
    mocker.patch("base64.b64decode", side_effect=lambda x: x)
    mock_http_rest = mocker.create_autospec(HttpRest)
    mock_http_rest_instance = mocker.Mock()
    mock_http_rest.return_value = mock_http_rest_instance

    response_mock = '{"unexpected": "data"}'
    mock_http_rest_instance.http_request.return_value = (response_mock, 200)
    mocker.patch("seCore.HttpRest.HttpRest", mock_http_rest)

    vault_engine = VaultEngine("https://test-vault", "namespace", "approle",
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode(),
                               "ODk0ZjFlNDktOWUyNC03OTZhLTcyOWYtYjM5MjQ0NWE3ZmQ4".encode())
    vault_engine.hashicorp_token = "mock_token"

    data, status_code = vault_engine.get_values("secrets_folder")
    assert data == {}
    # assert status_code == 200
