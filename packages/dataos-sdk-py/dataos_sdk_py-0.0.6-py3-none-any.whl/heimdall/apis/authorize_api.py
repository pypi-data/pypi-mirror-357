import uuid

from uplink import Header, returns, post, Body, json

from commons.http.client.dataos_consumer import DataOSBaseConsumer
from commons.http.client.hadler import raise_for_status_code
from heimdall.models.authorization_request import AuthorizationRequest, AuthorizationRequestBatch
from heimdall.models.authorization_response import AuthorizationResponse, AuthorizationResponseBatch


class AuthorizeApi(DataOSBaseConsumer):
    @raise_for_status_code
    @returns.json
    @json
    @post("api/v1/authorize")
    def authorize(self, payload: Body(type=AuthorizationRequest),
                  correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> AuthorizationResponse:
        """
            Perform a single authorization request using the provided payload and correlation ID.

            Parameters:
                self (object): The current instance of the class.
                payload (AuthorizationRequest): The payload containing the authorization request details.
                correlation_id (str, optional): The correlation ID used for tracking and logging the request.
                    It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

            Returns:
                AuthorizationResponse: An object representing the response for the authorization request.

            Raises:
                HTTPError: If the HTTP request returns an unsuccessful status code.
        """
        pass

    @raise_for_status_code
    @returns.json
    @json
    @post("api/v1/authorize/batch")
    def authorize_batch(self, payload: Body(type=AuthorizationRequestBatch),
                        correlation_id: Header("dataos-correlation-id") = str(
                            uuid.uuid4())) -> AuthorizationResponseBatch:
        """
            Perform a batch authorization request using the provided payload and correlation ID.

            Parameters:
                self (object): The current instance of the class.
                payload (AuthorizationRequestBatch): The payload containing the batch authorization request details.
                correlation_id (str, optional): The correlation ID used for tracking and logging the request.
                    It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

            Returns:
                AuthorizationResponseBatch: An object representing the response for the batch authorization request.

            Raises:
                HTTPError: If the HTTP request returns an unsuccessful status code.
            """
        pass
