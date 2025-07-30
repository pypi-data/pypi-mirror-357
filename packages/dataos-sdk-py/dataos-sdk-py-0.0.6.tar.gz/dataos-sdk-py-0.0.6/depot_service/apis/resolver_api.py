from __future__ import absolute_import

import uuid

from uplink import *

from commons.http.client.dataos_consumer import DataOSBaseConsumer
from commons.http.client.hadler import raise_for_status_code
from depot_service.models.ds_models import AddressInfo, ResolverResponse


class ResolveApi(DataOSBaseConsumer):

    @raise_for_status_code
    @returns.json
    @get("api/v2/resolve")
    def resolve(self, address: Query('address'),
                correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> AddressInfo:
        """
        Resolve an address to obtain address information.

        This function sends a GET request to resolve the provided address and retrieve address information.

        Parameters:
            address (str): The address to be resolved.

        Returns:
            AddressInfo: An object representing the address information.
                The object may contain various properties such as street address, city, state, postal code, etc.
        """
        pass

    @raise_for_status_code
    @returns.json
    @get("api/v3/resolve")
    def resolve_v3(self, address: Query('address'),
                   correlation_id: Header("dataos-correlation-id") = str(uuid.uuid4())) -> ResolverResponse:
        """
        Resolve an address to obtain address information.

        This function sends a GET request to resolve the provided address and retrieve address information.

        Parameters:
            address (str): The address to be resolved.

        Returns:
            AddressInfo: An object representing the address information.
                The object may contain various properties such as street address, city, state, postal code, etc.
        """
        pass
