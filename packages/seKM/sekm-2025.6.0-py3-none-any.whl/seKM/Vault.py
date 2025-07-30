import base64
import inspect
import json
import os
import sys
import urllib3
from typing import Any, Optional, Tuple, Dict, Union
from functools import wraps
from seCore.CustomLogging import logger
from seCore.HttpRest import HttpRest, HttpAction

urllib3.disable_warnings()


class VaultEngine:
    """A class for authenticating with Hashicorp Vault."""

    MAX_RETRIES = 3
    # DEFAULT_HEADERS = {"X-Vault-Token": ""}
    NOT_FOUND = "** not found **"

    def __init__(self, domain: str, namespace: str, app_role: str, role: str, secret: str, headers: str = "") -> None:
        # self.__base_url = domain
        # self.__namespace_path = f"/{namespace}" if namespace else ""
        # self.__urlLogin = f"{self.__base_url}/v1{self.__namespace_path}/auth/{app_role}/login"
        # self.__urlKV_Data = f"{self.__base_url}/v1{self.__namespace_path}/kv/data"

        if len(namespace) == 0:
            self.__urlLogin = f'{domain}/v1/auth/approle/login'
            self.__urlKV_Data = f'{domain}/v1/kv/data'
        else:
            self.__urlLogin = f'{domain}/v1/{namespace}/auth/{app_role}/login'
            self.__urlKV_Data = f'{domain}/v1/{namespace}/kv/data'

        self.__role_id = base64.b64decode(role).decode()
        self.__secret_id = base64.b64decode(secret).decode()
        self.__headers = self._parse_headers(headers)

        self.__vault_token: Optional[str] = None
        self.__vault_value: Optional[Dict] = None
        self.initialize()

    def _parse_headers(self, headers: str) -> Dict[str, str]:
        if not headers:
            return {}
        return {x.strip(): v.strip() for x, v in
                (item.split(':') for item in headers.split(","))}

    def _handle_error(self, error: Exception, function_name: str, message: str) -> None:
        exc_type, _, exc_tb = sys.exc_info()
        logger.error(json.dumps({
            function_name: {
                'exception_type': str(exc_type),
                'file': os.path.split(exc_tb.tb_frame.f_code.co_filename)[1],
                'line_number': exc_tb.tb_lineno,
                'msg': str(error)
            }
        }))

    def _make_request_with_retry(self, method: HttpAction, url: str,
                                 headers: Optional[Dict] = None,
                                 body: Optional[Dict] = None) -> Tuple[Any, int]:
        rest_api = HttpRest()
        retry_count = 0
        status_code = None

        while retry_count < self.MAX_RETRIES:
            try:
                if headers is None:
                    headers = {"X-Vault-Token": self.__vault_token}
                    if retry_count == 0:
                        headers.update(self.__headers)
                if status_code == 400:
                    headers.pop("X-Vault-Forward")

                # logger.warning(f'{retry_count} - {headers}')
                response, status_code = rest_api.http_request(method, url, headers=headers, body=body)

                if status_code == 200:
                    return json.loads(response), status_code

                retry_count += 1
                if retry_count < self.MAX_RETRIES:
                    logger.warning(json.dumps({
                        "vault": method.name,
                        "result": f"Request failed with status {status_code}. Retry {retry_count}/{self.MAX_RETRIES}",
                        "response": response,
                        "headers": headers
                    }))

            except Exception as e:
                self._handle_error(e, inspect.currentframe().f_code.co_name, str(e))
                break

        return None, status_code or 400

    def initialize(self) -> None:
        """Initialize Vault authentication."""
        self.__vault_token = self.get_token()

    @property
    def vault_token(self) -> Optional[str]:
        """Get the current Vault token."""
        return self.__vault_token

    @property
    def vault_value(self) -> Optional[Dict]:
        """Get the current Vault value."""
        return self.__vault_value

    def get_token(self) -> Optional[str]:
        """Authenticate and get a new Vault token."""
        try:
            body = {"role_id": self.__role_id, "secret_id": self.__secret_id}
            response, _ = self._make_request_with_retry(HttpAction.POST, self.__urlLogin, body=body)
            return response["auth"]["client_token"] if response else None
        except Exception as ex:
            logger.error(json.dumps({
                "function": "vault login",
                "result": "Failed to login to Vault",
                "error": str(ex)
            }))
            return None

    def get_value(self, secrets_folder: str = "", key: str = "") -> Tuple[Dict[str, str], Optional[int]]:
        """Get a specific value from Vault."""
        response, status_code = self._make_request_with_retry(
            HttpAction.GET,
            f"{self.__urlKV_Data}/{secrets_folder}"
        )

        if response:
            data = response["data"]["data"]
            self.__vault_value = {
                "project": secrets_folder,
                "key": key.lower(),
                "value": {k.lower(): v for k, v in data.items()}.get(key.lower(), self.NOT_FOUND)
            }
        else:
            self.__vault_value = {
                "project": secrets_folder,
                "key": key.lower(),
                "value": self.NOT_FOUND
            }

        return self.__vault_value, status_code

    def get_values(self, secrets_folder: str = "") -> Tuple[Dict[str, str], Optional[int]]:
        """Get all values from a Vault folder."""
        response, status_code = self._make_request_with_retry(
            HttpAction.GET,
            f"{self.__urlKV_Data}/{secrets_folder}"
        )

        if response and status_code == 200:
            return response["data"]["data"], status_code
        return {}, status_code

    def update_value(self, secrets_folder: str, key: str, value: str) -> int:
        """Update a specific value in Vault."""
        body = {"data": {key: value}}
        _, status_code = self._make_request_with_retry(
            HttpAction.POST,
            f"{self.__urlKV_Data}/{secrets_folder}",
            body=body
        )

        if status_code != 200:
            logger.error(json.dumps({
                "function": "vault update",
                "result": "Failed to update Vault",
                "error": f"Status code: {status_code}"
            }))

        return status_code
