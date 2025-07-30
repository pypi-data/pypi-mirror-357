import platform
import time

import requests
import json
import jwt
from uuid import uuid4
from IPython import get_ipython
from .client import get_nic_id
from .config.config import config

if get_ipython():
    from .magics.magics import AGMagic


def login_sql(
        api_key: str,
        profile: str = "default",
        params: dict = None
):
    """
    Args:
        profile: The profile to load the configuration from.
        api_key (str): The API key for authentication.
        params (dict): Connection parameters for the connection.

    Returns:

    """
    config.load_config(profile=profile)
    if not params:
        params = {}
    console_url = config.AGENT_CONSOLE_URL
    base_url = config.AGENT_SQL_SERVER_URL
    if not console_url or not base_url:
        raise ValueError("Please load the configuration file using the 'load_config' method before calling this "
                         "function.")
    if not api_key:
        raise ValueError("Please provide the API key.")
    return AGSQLClient(console_url, base_url, api_key, params)


class AGSQLClient:
    _DEFAULT_HEADER = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    _UUID = str(uuid4())
    _os = platform.platform()
    _nic_id = get_nic_id()

    def __init__(self, console_url: str, base_url: str, api_key: str, params):
        """Initialize a new connection.
        Args:
            console_url (str): The URL of the running console server
            base_url (str): The URL of the running SQL server
            api_key (str): The API key for authentication.
            params (dict): Connection parameters for the connection.
        """
        if params is None:
            params = {}
        self.console_url = console_url
        self._base_url = base_url
        self.api_key = api_key
        self._set_tokens()
        self._session_id = str(uuid4())
        if not self._validate_params(params):
            raise ValueError("The parameters keys shouldn't repeat in any case(lower/upper) to avoid ambiguity")

        params = {k.lower(): v for k, v in params.items()}
        self._team_name = params.get("team_name", None)
        if hasattr(self, '_access_token') and self._access_token:
            self._start_sql_session(params)
            if get_ipython():
                AGMagic.load_ag_magic()
                AGMagic.load_oblv_client(sql_server=self)
                print("%%sql magic registered successfully! Use %%sql and write a sql query to execute it on the AGENT "
                    "SQL server")
        else:
            print("Failed to authenticate. Please check your API key and try again.")

    def _start_sql_session(self, params):
        epsilon = params.get("eps", params.get("epsilon", None))
        delta = params.get("del", params.get("delta", None))
        cache_invalidation_interval = params.get("cache_timeout", None)
        skip_cache = params.get("skip_cache", False)
        noise_mechanism = params.get("noise_mechanism", "laplace")

        payload = {
            "connection_id": self._session_id
        }
        if epsilon:
            payload["epsilon"] = epsilon
            if not isinstance(epsilon, float) and not isinstance(epsilon, int):
                raise ValueError("Epsilon should be a number!")
        if delta:
            payload["delta"] = delta
            if not isinstance(delta, float) and not isinstance(delta, int):
                raise ValueError("Delta should be a number!")
        if cache_invalidation_interval:
            payload["cache_invalidation_interval"] = cache_invalidation_interval
            if not isinstance(cache_invalidation_interval, int):
                raise ValueError("Cache invalidation interval should be a non-negative integer!")
        if skip_cache:
            payload["skip_cache"] = skip_cache
            if not isinstance(skip_cache, bool):
                raise ValueError("Skip cache should be a boolean!")
        if noise_mechanism:
            payload["noise_mechanism"] = noise_mechanism
            if not isinstance(noise_mechanism, str) or noise_mechanism.lower() not in ["laplace", "gaussian"]:
                raise ValueError("Noise mechanism should be either laplace or gaussian!")

        response = self._post(endpoint="/start-sql-session", base_url=self._base_url, data=payload,
                              access_token=self._access_token, refresh_token=self._refresh_token)
        if response.get("status") != "Success":
            raise ValueError("Failed to start SQL session. Please check the parameters.")

    @staticmethod
    def _validate_params(params: dict):
        """ Check if there is an ambiguity in the params
        :param params: The dictionary that denotes the connection parameters
        :return: True/False
        """

        for key in params:
            if key != key.lower() and key.lower() in params:
                return False
        return True

    def _set_tokens(self):
        """
        Retrieves and sets access and refresh tokens from the console server.

        This method sends a login request to the console server using the API key,
        machine UUID, and OS information. It then processes the server's response
        to extract and set the access and refresh tokens.

        Raises:
            Exception: If any error occurs during the token retrieval process.
        """
        try:
            payload = {
                "apikey": self.api_key,
                "machine_uuid": self._UUID,
                "os": self._os,
            }
            if self._nic_id:
                payload["nic_id"] = self._nic_id
            print("Please approve the token request from the console", flush=True)
            if get_ipython():
                response = self._post(endpoint="/jupyter/login/request", base_url=self.console_url, data=payload)  
                skipped_first = False
                for line in response.split("\n"):
                    if line.strip().startswith('data: '):
                        json_obj = line.strip()
                        if not skipped_first:
                            skipped_first = True
                            continue
                        try:
                            data = json.loads(json_obj[6:])  # Parse JSON directly from the sliced string
                            self.__process_message(data)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
            else:
                response = self._get(endpoint="/jupyter/login/request", base_url=self.console_url, params=payload)
                self.__process_message(response)

        except Exception as e:
            raise

    def _is_token_expired(self):
        """
        Checks if the access token is expired.

        This method decodes the access token and compares its expiration time
        with the current time to determine if it has expired.

        Returns:
            bool: True if the token is expired, False otherwise.
        """
        try:
            payload = jwt.decode(self._access_token, options={"verify_signature": False})
            current_time = time.time() + 10  # 10 seconds for network latency
            return payload.get('exp', 0) < current_time
        except Exception as e:
            print(f"Error while checking token expiry: {str(e)}")

    def _get_refresh_token(self):
        try:
            if not self._is_token_expired():
                return
            payload = {
                "refresh_token": self._refresh_token
            }
            response = self._post(endpoint="/jupyter/token/refresh", base_url=self.console_url, data=payload)
            self._access_token = response.get("access_token")
            self._refresh_token = response.get("refresh_token")
        except Exception as e:
            raise

    def _make_request(self, method, endpoint, base_url=None, params=None, data=None, headers=None):
        """
        Make a HTTP request to the specified endpoint.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint.
            params (dict, optional): URL parameters. Defaults to None.
            data (dict, optional): Request body for POST/PUT requests. Defaults to None.
            headers (dict, optional): HTTP headers. Defaults to None.

        Returns:
            dict or str: JSON response or text from the API.

        Raises:
            Exception: If the API request fails.
        """
        url = f"{base_url or self._base_url}{endpoint}"
        headers = headers if headers else self._DEFAULT_HEADER

        try:
            response = requests.request(method, url, params=params, data=json.dumps(data), headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            try:
                response_json = response.json()
                return response_json
            except:
                response_text = response.text
                return response_text

        except requests.exceptions.HTTPError as e:
            raise
        except requests.exceptions.ConnectionError as e:
            raise
        except requests.exceptions.Timeout as e:
            raise
        except Exception as e:
            raise

    def _get(self, endpoint, params=None, base_url=None, access_token=None, refresh_token=None):
        """
        Make a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict, optional): URL parameters. Defaults to None.
            base_url (str, optional): Base URL for the request. Defaults to None.
            access_token (str, optional): Access token for authorization. Defaults to None.
            refresh_token (str, optional): Refresh token for authorization. Defaults to None.

        Returns:
            dict: JSON response from the API.

        Raises:
            Exception: If the API request fails.
        """
        headers = self._DEFAULT_HEADER
        if access_token:
            self._get_refresh_token()
            headers['Authorization'] = f'Bearer {access_token}'
        if refresh_token:
            headers['refresh_token'] = f'{refresh_token}'
        return self._make_request('GET', endpoint, base_url, params=params, headers=headers)

    def _post(self, endpoint, data=None, base_url=None, access_token=None, refresh_token=None):
        """
        Make a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            data (dict, optional): Request body. Defaults to None.
            base_url (str, optional): Base URL for the request. Defaults to None.
            access_token (str, optional): Access token for authorization. Defaults to None.
            refresh_token (str, optional): Refresh token for authorization. Defaults to None.

        Returns:
            dict: JSON response from the API.

        Raises:
            Exception: If the API request fails.
        """
        headers = self._DEFAULT_HEADER
        if access_token:
            self._get_refresh_token()
            headers['Authorization'] = f'Bearer {access_token}'
        if refresh_token:
            headers['refresh-token'] = f'{refresh_token}'
        return self._make_request('POST', endpoint, base_url, data=data, headers=headers)

    def __process_message(self, data):
        """
        Processes a message received from the console server.

        This method handles different approval statuses (approved, pending, expired, failed)
        and extracts relevant information such as access tokens and approval URLs.

        Args:
            data (dict): The message data received from the console server.

        Raises:
            ValueError: If the access token cannot be retrieved or the approval status
                is unexpected.
        """
        approval_status = data.get('approval_status')
        if approval_status == 'approved':
            token = data.get('access_token')
            if token:
                self._access_token = token
                self._refresh_token = data.get('refresh_token', None)
                return
            else:
                print("Access token not found in the response")
        elif approval_status == 'pending':
            print("Please approve the token request in the console")
        elif approval_status == 'expired':
            print("The token request has expired. Please try again")
        elif approval_status == 'failed':
            print("Token request failed. Contact support")
        raise ValueError("Failed to get access token")

    def execute(self, sql):
        """Execute an SQL query."""
        # Call /execute_sql endpoint with required payload
        payload = {
            "sql": sql,
            "connection_id": self._session_id,
            "team_name": self._team_name or "",
            "client_name": "AGENT_Client",
        }
        try:
            response = self._post(endpoint="/execute_sql", data=payload)
        except Exception as e:
            raise ValueError(f"Error executing SQL: {sql}. Error: {str(e)}")
        if response.get("status") != "success":
            raise ValueError(f"Error executing SQL: {response.get('error')}")
        # Parse JDBC JSON response
        result_set = []
        result_set.append(response.get("columnInfo", {}).get("names", []))
        for row in response.get("rows", []):
            result_set.append(row)
        return result_set
