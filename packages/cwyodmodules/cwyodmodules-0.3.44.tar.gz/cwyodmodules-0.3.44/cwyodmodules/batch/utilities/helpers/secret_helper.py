from azure.keyvault.secrets import SecretClient

from mgmt_config import logger, identity


class SecretHelper:
    def __init__(self, keyvault_uri) -> None:
        """
        Initializes an instance of the SecretHelper class.

        The constructor sets the USE_KEY_VAULT attribute based on the value of the USE_KEY_VAULT environment variable.
        If USE_KEY_VAULT is set to "true" (case-insensitive), it initializes a SecretClient object using the
        AZURE_KEY_VAULT_ENDPOINT environment variable and the DefaultAzureCredential.

        Args:
            None

        Returns:
            None
        """
        self.USE_KEY_VAULT = True
        self.secret_client = None
        if self.USE_KEY_VAULT:
            credential = identity.get_credential()
            self.secret_client = SecretClient(
                vault_url=keyvault_uri,
                credential=credential,
                connection_verify=True,
            )

    @logger.trace_function(log_execution=True, log_args=False, log_result=False)
    def get_secret(self, secret_name: str) -> str:
        """
        Retrieves the value of a secret from the environment variables or Azure Key Vault.

        Args:
            secret_name (str): The name of the secret or "".

        Returns:
            str: The value of the secret.

        Raises:
            None

        """
        secret_value = self.secret_client.get_secret(name=secret_name).value
        return secret_value

    @logger.trace_function(log_execution=True, log_args=False, log_result=False)
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """
        Sets the value of a secret in Azure Key Vault only if it doesn't exist or has a different value.

        Args:
            secret_name (str): The name of the secret.
            secret_value (str): The value to be stored.

        Returns:
            None

        Raises:
            None
        """
        try:
            current_secret = self.secret_client.get_secret(name=secret_name)
            if current_secret.value != secret_value:
                self.secret_client.set_secret(name=secret_name, value=secret_value)
            else:
                logger.warning(
                    f"Secret {secret_name} already has the same value, skipping update"
                )
        except Exception:
            self.secret_client.set_secret(name=secret_name, value=secret_value)
            logger.warning(f"Secret {secret_name} has been created")


    @logger.trace_function(log_execution=True, log_args=False, log_result=False)
    def get_secret_from_json(self, secret_name: str) -> str:
        secret_value = self.secret_client.get_secret(secret_name).value
        return secret_value
