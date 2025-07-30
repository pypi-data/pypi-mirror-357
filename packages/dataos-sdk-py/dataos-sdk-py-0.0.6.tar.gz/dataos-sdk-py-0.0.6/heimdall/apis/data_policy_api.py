import uuid

from typing import List
from uplink import Header, get, returns, post, put, delete, Body

from commons.http.client.dataos_consumer import DataOSBaseConsumer
from commons.http.client.hadler import raise_for_status_code
from heimdall.models.data_policy import DataPolicy


class DataPolicyApi(DataOSBaseConsumer):
    @raise_for_status_code
    @returns.json
    @get("dp/api/v1/policies")
    def list(self,
             correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> List[DataPolicy]:
        """
        Retrieve a list of data policies from the API.

        This function sends a GET request to fetch a list of data policies from the specified API endpoint.

        Parameters:
            correlation_id (str, optional): A unique identifier for tracking the API request (default is a new UUID).

        Returns:
            List[DataPolicy]: A list of DataPolicy objects representing the data policies retrieved from the API.

        """
        pass

    @raise_for_status_code
    @returns.json
    @post("dp/api/v1/policies")
    def create(self, payload: Body(type=DataPolicy),
               correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> DataPolicy:
        """
        Create a new data policy via the API.

        This function sends a POST request to create a new data policy using the provided payload.

        Parameters:
            payload (DataPolicy): A DataPolicy object representing the details of the data policy to be created.
            correlation_id (str, optional): A unique identifier for tracking the API request (default is a new UUID).

        Returns:
            DataPolicy: A DataPolicy object representing the newly created data policy.
        """
        pass

    @raise_for_status_code
    @returns.json
    @get("dp/api/v1/policies/{name}")
    def get(self, name: str,
            correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> DataPolicy:
        """
        Retrieve a data policy by its name from the API.

        This function sends a GET request to fetch a data policy with the specified name from the API.

        Parameters:
            name (str): The name of the data policy to retrieve.
            correlation_id (str, optional): A unique identifier for tracking the API request (default is a new UUID).

        Returns:
            DataPolicy: A DataPolicy object representing the data policy retrieved from the API.
        """
        pass

    @raise_for_status_code
    @returns.json
    @put("dp/api/v1/policies/{name}")
    def update(self, name: str, payload: Body(type=DataPolicy),
               correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> DataPolicy:
        """
        Update an existing data policy via the API.

        This function sends a PUT request to update an existing data policy with the provided payload.

        Parameters:
            self: The class instance (automatically passed).
            name (str): The name of the data policy to update.
            payload (DataPolicy): A DataPolicy object representing the updated details of the data policy.
            correlation_id (str, optional): A unique identifier for tracking the API request (default is a new UUID).

        Returns:
            DataPolicy: A DataPolicy object representing the updated data policy.
        """
        pass

    @raise_for_status_code
    @delete("dp/api/v1/policies/{name}")
    def delete(self, name: str,
               correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> None:
        """
        Delete a data policy via the API.

        This function sends a DELETE request to remove a data policy with the specified name from the API.

        Parameters:
            name (str): The name of the data policy to delete.
            correlation_id (str, optional): A unique identifier for tracking the API request (default is a new UUID).

        Returns:
            None
        """
        pass

    # @raise_for_status_code
    # @returns.json
    # @post("dp/api/v1/policies/decision")
    # def get_decision(self, payload: Body(type=Dataset),
    #                  correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> Decision:
    #     pass
    #
    # @raise_for_status_code
    # @returns.json
    # @get("dp/api/v1/policies/decision/{depot}/{collection}/{dataset}")
    # def get_decision_without_context(self, depot: str, collection: str, dataset: str,
    #                                  correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> Decision:
    #     pass
