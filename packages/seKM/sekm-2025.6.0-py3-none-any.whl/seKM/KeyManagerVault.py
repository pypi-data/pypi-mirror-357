import inspect
import json

from typing import Optional
from bitflags import BitFlags

from seCore.CustomLogging import logger
from seCore.Encryption import Encryption
from seCore.jsondb import JsonDB
from seCore.jsondb.db_types import NewKeyValidTypes

from .Utilities import get_exception_details
from .Vault import VaultEngine


# Constants
SEPARATOR_LINE = "-" * 160


class KeyManager_Logging(BitFlags):
    options = {
        0: "init_folder",
        1: "init_schema",
        2: "init_secrets",
    }


class _BaseConfig(object):
    # Constants for required configuration properties
    REQUIRED_CONFIG_ATTRIBUTES = {
        'HV_DOMAIN': '_domain',
        'HV_NAMESPACE': '_namespace',
        'HV_APPROLE': '_approle',
        'HV_APPROLE_ROLE_ID': '_approle_role_id',
        'HV_APPROLE_SECRET_ID': '_approle_secret_id',
        'HV_SECRETS_FOLDER': '_secrets_folder',
        'HV_SECRETS_KEY': '_secrets_key',
        'HV_HEADERS': '_headers',
    }

    def __init__(self, conf: dict) -> None:
        # Default Attributes
        self._domain: str = ""
        self._namespace: str = ""
        self._approle: str = ""
        self._approle_role_id: str = ""
        self._approle_secret_id: str = ""
        self._secrets_folder: str = ""
        self._secrets_key: str = ""
        self._headers: str = ""
        self._log_keymanager: int = 0

        self._set_configuration(conf.copy())

    def _set_configuration(self, config: dict) -> None:
        missing_keys = []
        # Set required configuration properties
        for env_key, attr_name in self.REQUIRED_CONFIG_ATTRIBUTES.items():
            config_value = config.pop(env_key, None)
            if config_value is None:
                missing_keys.append(env_key)
            else:
                setattr(self, attr_name.strip(), config_value)

        if missing_keys:
            raise ValueError(f"Missing required configuration properties: {', '.join(missing_keys)} in .env.secrets")

        # Set remaining optional configuration properties
        for key, value in config.items():
            attr_name = f'_{key.lower()}'
            setattr(self, attr_name, value)


class KeyManager(_BaseConfig):
    # Constants
    _ROLES_KEY = "Roles"

    def __init__(self, conf: dict = dict):
        # Initialize Keys
        self._keys = {'': {}}
        # Initialize Configuration
        super().__init__(conf)
        # ---------------------------------------------------------------------------------------------
        # Logging settings
        logger.level("LOGGING", 26, color="<green>")
        self._loggingFlags = KeyManager_Logging()

        self._loggingFlags.value = int(self._log_keymanager)
        if self._loggingFlags.value > 0:
            logger.log("LOGGING", SEPARATOR_LINE)
            logger.log("LOGGING", json.dumps({"key_manager_vault": {"logging": f'{self._loggingFlags.value} - {self._loggingFlags}'}}))

        # Setup Encryption
        self.encryption = Encryption()

        if self._loggingFlags.init_folder:  # Logging: __init__ - folder
            logger.log("LOGGING", json.dumps({"key_manager_vault": {
                "init_folder": {
                    "secrets_folder": self._secrets_folder,
                    "secret_key": self._secrets_key
                }}}))

        # Initialize Vault
        self.vlt = VaultEngine(self._domain,
                               self._namespace,
                               self._approle,
                               self._approle_role_id,
                               self._approle_secret_id,
                               self._headers)

        # Get Secrets Value and validate is in the right format
        secrets, status_code = self.vlt.get_value(self._secrets_folder, self._secrets_key)
        # =============================================================================================
        # == New Code
        # =============================================================================================
        logger.info(SEPARATOR_LINE)

        # Could not find km settings in Vault
        if "** not found **" in secrets['value']:
            logger.error(json.dumps({"key_manager_vault": {
                "folder": {
                    "secrets_folder": self._secrets_folder,
                    "secret_key": self._secrets_key,
                    "desc": f'Key `{self._secrets_key}` was not found in Vault, need to create'}
            }}))
            secret_value = {"keys": [], "data": {}}

        else:
            logger.info(json.dumps({"key_manager_vault": {
                "folder": {
                    "secrets_folder": self._secrets_folder,
                    "secret_key": self._secrets_key,
                    "desc": f'Key `{self._secrets_key}` was found in Vault'}
            }}))
            secret_value = json.loads(self.encryption.decrypt(secrets.get('value', '** not found **')))
        # ------------------------------------------------------
        # Get keys in folder
        vlt_folder_keys, status_code = self.vlt.get_values(self._secrets_folder)

        if self._loggingFlags.init_schema:  # Logging: __init__ - folder
            logger.log("LOGGING", SEPARATOR_LINE)
            logger.log("LOGGING", json.dumps(
                {'key_manager_vault': {
                    'init_schema': {
                        'decrypted_raw': secret_value,
                    }}}))

            logger.log("LOGGING", json.dumps(
                {'key_manager_vault': {
                    'init_schema': {
                        'folder_keys': list(vlt_folder_keys.keys())
                    }}}))

        # ------------------------------------------------------
        # Check Version
        self.__version = secret_value.get("version", 1)
        if self.__version == 1:
            _defaultKeys = {
                            "version": self.__version + 1,
                            "keys": [],
                            "data": secret_value.get('data', secret_value)
                        }
            first_element = _defaultKeys['data']
            first_element_keys = list(first_element[list(first_element.keys())[0]].keys())
            _defaultKeys['keys'] = first_element_keys
            self.__db = JsonDB("", load_json=_defaultKeys)

            if self._loggingFlags.init_schema:  # Logging: __init__ - folder
                logger.log("LOGGING", json.dumps({'key_manager_vault': {'init_schema': 'Upgrated schema to version 2'}}))
            # todo: need to update vault value

        # ------------------------------------------------------
        if self.__version == 2:
            # Load JsonDB and Set Keys
            self.__db = JsonDB("", load_json=secret_value)

        self._keys = self.__db.get_all()
        if self._loggingFlags.init_schema:  # Logging: __init__ - folder
            logger.log("LOGGING", json.dumps({'key_manager_vault': {'init_schema': self.__db.dump_json()}}))

        # =============================================================================================
        # == New Code: End
        # =============================================================================================

        if self._loggingFlags.init_secrets:  # Logging: __init__ - secrets
            logger.log("LOGGING", SEPARATOR_LINE)
            logger.log("LOGGING", json.dumps({'key_manager_vault': {
                'init_secrets': {
                    "key_cnt": len(self._keys),
                    "keys": list(self._keys.keys())
                }}}))

    # ---------------------------------------------------------------------------------------------

    def get_all_keys(self) -> dict:
        """
        Returns all keys as a dictionary.
        """
        return self._keys

    # ---------------------------------------------------------------------------------------------

    def get_masked_keys(self) -> dict:
        """
        Gets masked versions of the keys from the original keys and returns a dictionary
        mapping the masked keys to their corresponding data. The method retrieves all
        the original keys, masks their values, and creates a new dictionary where each
        masked key is associated with the corresponding original key data, with the key
        value updated to its masked version.

        :raises AttributeError: If the `self.get_all_keys` or `self.mask_key` method is
            not correctly implemented in the class or instance.
        :raises KeyError: If "Key" is missing in the key data during the iteration of
            the original keys.

        :return: A dictionary where the keys are masked versions of the original keys,
            and the values are copies of the original key data with the key value
            replaced by its masked version.
        :rtype: dict
        """
        original_keys = self.get_all_keys()
        masked_keys = {}

        for original_key, key_data in original_keys.items():
            if "Key" in key_data:
                masked_key = self.mask_key(key_data["Key"])
                masked_keys[masked_key] = key_data.copy()
                masked_keys[masked_key]["Key"] = masked_key

        return masked_keys

    # ---------------------------------------------------------------------------------------------

    def validate_key(self, key: str) -> bool:
        """
        Checks if a given key is valid.
        """
        return key in self._keys

    # ---------------------------------------------------------------------------------------------

    def mask_key(self, key: str) -> str:
        """
        Masks a key by returning its last segment.
        """
        return key.split("-")[-1] if self.validate_key(key) else ""

    # ---------------------------------------------------------------------------------------------

    def get_roles(self, key: str) -> list:
        """
        Returns the roles associated with a given key.
        :param key: The key to retrieve roles for.
        :return: A list of roles.
        """
        return self._keys.get(key, {}).get("Roles", [""])

    # ---------------------------------------------------------------------------------------------

    def _get_roles_from_key(self, key: str) -> list:
        """Helper function to fetch roles for a given key."""
        key_data = self._keys.get(key)
        if key_data and self._ROLES_KEY in key_data:
            return key_data[self._ROLES_KEY]
        return []

    @staticmethod
    def _normalize_roles(roles: str | list[str]) -> list[str]:
        """Ensure roles is always a list."""
        return [roles] if isinstance(roles, str) else roles

    def validate_role(self, key: str, roles: str | list[str]) -> bool:
        """Validates if a role is associated with a key."""
        allowed_roles = self._get_roles_from_key(key)
        roles_to_validate = self._normalize_roles(roles)

        return bool(set(allowed_roles).intersection(roles_to_validate))

    def validate_key_role(self, key: str, roles: str | list[str]) -> dict:
        """
            Validates the given key and role(s) and returns a detailed dictionary
            containing the key, its roles, a masked version of the key, valid roles
            obtained for the key, and the result of the role validation.
            """
        return {
            "key": key,
            "roles": roles,
            "key_mask": self.mask_key(key),
            "valid_roles": self.get_roles(key),
            "role_valid": self.validate_role(key, roles),
        }

    def schema_version(self):
        """
        Retrieves the schema version associated with the current instance.

        The schema version is stored privately within the object and can
        be retrieved for operations requiring version control or checks.

        :return: The schema version of the instance.
        :rtype: str
        """
        return self.__version

    # ---------------------------------------------------------------------------------------------
    # Need to validate these functions, so skipping for now
    # ---------------------------------------------------------------------------------------------

    # todo: add_new_key - validate and test
    def add_new_key(self, key: str, default: Optional[NewKeyValidTypes] = None) -> None:  # pragma: no cover
        self.__db.add_new_key(key, default)

    # todo: set_schema - validate and test
    def set_schema(self, schema: dict):  # pragma: no cover
        """
        Update keys in Vault
        Args:
            schema: str

        Returns:
            None
        """
        self.__db = JsonDB("", load_json=schema)
        # logger.error(json.dumps(self.__db.dump_json()))
        self.vlt.app_init()  # pragma: no cover
        self.vlt.update_value(self._secrets_folder, self._secrets_key, self.encryption.encrypt(json.dumps(self.__db.dump_json())).decode())  # pragma: no cover
        logger.info(json.dumps({"keys": {"count": len(self._keys)}}))  # pragma: no cover
        # logger.info(json.dumps({"key_manager_vault": {"key_cnt": len(self.keys),
        #                                "keys": list(self.keys.keys())}}))

    # todo: set_keys - validate and test
    def set_keys(self, keys: dict):  #
        """
        Update keys in Vault
        Args:
            keys: dict

        Returns:
            None
        """
        self._keys = keys  # pragma: no cover
        self.vlt.app_init()  # pragma: no cover
        self.vlt.update_value(self._secrets_folder, self._secrets_key, self.encryption.encrypt(json.dumps(keys)).decode())  # pragma: no cover
        logger.info(json.dumps({"keys": {"count": len(self._keys)}}))  # pragma: no cover
        # logger.info(json.dumps({"key_manager_vault": {"key_cnt": len(self.keys),
        #                                "keys": list(self.keys.keys())}}))

    def get_key_element(self, key: str, element_name: str, default_value: any = None) -> any:  # pragma: no cover
        """
        Returns any element from the key data with a default value if not found.

        Args:
            key: The key to look up data for
            element_name: Name of the element to retrieve from key data
            default_value: Value to return if key or element is not found (default: None)

        Returns:
            The value of the requested element or the default_value if not found
        """
        key_data = self._keys.get(key, {})
        return key_data.get(element_name, default_value)