from commons.http.client.base_client import BaseHTTPClientBuilder
from commons.utils.helper import normalize_base_url
from heimdall.apis.authorize_api import AuthorizeApi
from heimdall.apis.data_policy_api import DataPolicyApi
from heimdall.apis.secret_api import SecretApi
from heimdall.apis.user_api import UserApi


class HeimdallClientBuilder(BaseHTTPClientBuilder):
    def get_default_user_agent_suffix(self):
        return "HeimdallClient"

    def build(self):
        """
        Build the HeimdallClient instance.

        Returns:
            HeimdallClient: An instance of HeimdallClient with the configured settings.
        """
        return HeimdallClient(self.base_url, self.apikey, self.get_http_client())


class HeimdallClient:
    def __init__(self, base_url, apikey, client=None):
        self.client = client
        self.base_url = base_url
        self.apikey = apikey
        """
        Initialize the HeimdallClient.

        This class provides a client to interact with various API endpoints related to Heimdall.

        Parameters:
            base_url (str): The base URL of the Heimdall API.
            apikey (str): The API key for authentication with the Heimdall API.
            client (object, optional): An instance of the HTTP client to use for making API requests (default is None).

        Attributes:
            secret_api (SecretApi): An instance of SecretApi for interacting with the Secret API endpoints.
            user_api (UserApi): An instance of UserApi for interacting with the User API endpoints.
            data_policy_api (DataPolicyApi): An instance of DataPolicyApi for interacting with the Data Policy API endpoints.
        """
        base_url = normalize_base_url(base_url)
        self.secret_api = SecretApi(base_url, self.apikey, client=self.client)
        self.user_api = UserApi(base_url, self.apikey, client=self.client)
        self.data_policy_api = DataPolicyApi(base_url, self.apikey, client=self.client)
        self.authorize_api = AuthorizeApi(base_url, self.apikey, client=self.client)
