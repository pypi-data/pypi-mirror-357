import uuid

from uplink import Header, get, returns

from commons.http.client.dataos_consumer import DataOSBaseConsumer
from commons.http.client.hadler import raise_for_status_code
from heimdall.models.secret_response import SecretResponse


class SecretApi(DataOSBaseConsumer):
    @raise_for_status_code
    @returns.json
    @get("api/v1/secrets/{secret}")
    def get_secret(self, secret: str,
                   correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> SecretResponse:
        """
            Retrieve a secret from the specified source using the provided correlation ID.

            Parameters:
                self (object): The current instance of the class.
                secret (str): The name or identifier of the secret to retrieve.
                correlation_id (str, optional): The correlation ID used for tracking and logging the request.
                    It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

            Returns:
                SecretResponse: An object representing the response containing the retrieved secret.

            Raises:
                (Possible custom exceptions raised during the execution of this method)
            """
        pass
