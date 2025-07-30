import uuid
from typing import List

from uplink import Header, get, returns

from commons.http.client.dataos_consumer import DataOSBaseConsumer
from commons.http.client.hadler import raise_for_status_code
from heimdall.models.token import Token
from heimdall.models.user import User


class UserApi(DataOSBaseConsumer):
    @raise_for_status_code
    @returns.json
    @get("api/v1/users")
    def list(self,
             correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> List[User]:
        """
        Retrieve a list of users from the specified API endpoint using the provided correlation ID.

        Parameters:
            self (object): The current instance of the class.
            correlation_id (str, optional): The correlation ID used for tracking and logging the request.
                It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

        Returns:
            List[User]: A list containing User objects representing the users retrieved from the API.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Description:
            This method makes an HTTP GET request to the specified API endpoint ('api/v1/users') to retrieve a list of users.
            The 'correlation_id' parameter is an optional header used for tracking the request and correlating
            logs related to this specific operation. If not provided, a new UUID will be generated automatically.

            The method uses the 'raise_for_status_code' decorator, which checks the response status code
            and raises an 'HTTPError' if the status code indicates an unsuccessful request (e.g., 4xx or 5xx).

            The method also uses the 'returns.json' decorator, which automatically parses the JSON response data
            into a Python object (in this case, a list of 'User' objects).

            Note: The 'returns.json' decorator assumes that the API response returns valid JSON data.
            """
        pass

    @raise_for_status_code
    @returns.json
    @get("api/v1/users/{user_id}")
    def get_user(self, user_id: str,
                 correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> User:
        """
       Retrieve information about a specific user from the API using the provided user ID and correlation ID.

       Parameters:
           self (object): The current instance of the class.
           user_id (str): The unique identifier of the user to retrieve.
           correlation_id (str, optional): The correlation ID used for tracking and logging the request.
               It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

       Returns:
           User: An object representing the user retrieved from the API.

       Raises:
           HTTPError: If the HTTP request returns an unsuccessful status code.

       Description:
           This method makes an HTTP GET request to the specified API endpoint ('api/v1/users/{user_id}')
           to retrieve information about a specific user identified by 'user_id'.

           The 'correlation_id' parameter is an optional header used for tracking the request and correlating
           logs related to this specific operation. If not provided, a new UUID will be generated automatically.

           The method uses the 'raise_for_status_code' decorator, which checks the response status code
           and raises an 'HTTPError' if the status code indicates an unsuccessful request (e.g., 4xx or 5xx).

           The method also uses the 'returns.json' decorator, which automatically parses the JSON response data
           into a Python object ('User' object in this case).

           Note: The 'returns.json' decorator assumes that the API response returns valid JSON data.
           """
        pass

    @raise_for_status_code
    @returns.json
    @get("api/v1/users/{user_id}/tokens")
    def get_user_tokens(self, user_id: str,
                        correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> List[Token]:
        """
        Retrieve a user token from the API for the specified user using the provided user ID and correlation ID.

        Parameters:
            self (object): The current instance of the class.
            user_id (str): The unique identifier of the user for whom to retrieve the token.
            correlation_id (str, optional): The correlation ID used for tracking and logging the request.
                It defaults to a new UUID (Universally Unique Identifier) generated using the uuid.uuid4() method.

        Returns:
            List[Token]: A list of Token objects representing the user tokens retrieved from the API.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Description:
            This method makes an HTTP GET request to the specified API endpoint ('api/v1/users/{user_id}/tokens')
            to retrieve a user token associated with the provided 'user_id'.

            The 'correlation_id' parameter is an optional header used for tracking the request and correlating
            logs related to this specific operation. If not provided, a new UUID will be generated automatically.

            The method uses the 'raise_for_status_code' decorator, which checks the response status code
            and raises an 'HTTPError' if the status code indicates an unsuccessful request (e.g., 4xx or 5xx).

            The method also uses the 'returns.json' decorator, which automatically parses the JSON response data
            into a Python object ('Token' object in this case).

            Note: The 'returns.json' decorator assumes that the API response returns valid JSON data.
            """
        pass
