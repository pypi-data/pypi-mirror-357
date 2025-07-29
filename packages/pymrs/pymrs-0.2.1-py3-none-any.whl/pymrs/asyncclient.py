import httpx
import json
import logging
from pydantic import (
    ValidationError,
    BaseModel,
    Field,
    HttpUrl,
    TypeAdapter,
    model_validator,
)
from .exceptions import MRSClientError
from json.decoder import JSONDecodeError
from typing import Callable, Any, Dict
from enum import Enum
from datetime import datetime

class AuthType(Enum):
    PASSWORD = "password"
    TICKET = "ticket"

class _MRSClientConfig(BaseModel):
    """
    Private class used for input validation
    """

    hostname: HttpUrl
    kadme_token: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str | None = Field(default=None, min_length=1)
    ticket: str | None = Field(default=None, min_length=1)
    
    @model_validator(mode='after')
    def validate_auth_method(self):
        if not self.password and not self.ticket:
            raise ValueError("Either 'password' or 'ticket' must be provided")
        return self


class ElasticsearchConfig(BaseModel):
    host: str
    port: int

    @property
    def url(self) -> HttpUrl:
        return TypeAdapter(HttpUrl).validate_strings(f"http://{self.host}:{self.port}")


class AsyncMRSClient:
    """Async HTTP client for interacting with MRS (Memoza Rest Server).
    
    This client provides asynchronous methods for authentication, data retrieval, 
    Elasticsearch queries, file uploads, and other MRS operations. It supports both 
    password-based and ticket-based authentication methods.
    
    The client can be used as an async context manager for automatic session management,
    or methods can be called individually with manual session cleanup.

    Attributes:
        hostname (str): The complete base URL of the MRS server including the rest server path (e.g., 'http://server.com/memoza-rest-server').
        kadme_token (str): The KADME security token.
        username (str): The username for authentication.
        password (str): The password for authentication (when using password auth).
        auth_type (AuthType): The authentication method being used (PASSWORD or TICKET).
        valid_until (str): The ticket expiration timestamp in ISO format.
        client (httpx.AsyncClient): The underlying HTTP client for making requests.
    """

    def __init__(
        self,
        hostname,
        kadme_token: str,
        username: str,
        password: str | None = None,
        ticket: str | None = None,
        valid_until: str | None = None,
        timeout: float = 120,
    ):
        """Initialize the AsyncMRSClient with authentication credentials.

        The client supports two authentication methods:
        1. Password-based: Provide username and password for login authentication
        2. Ticket-based: Provide an existing authentication ticket
        
        At least one authentication method (password or ticket) must be provided.

        Args:
            hostname (str): The complete base URL of the MRS server including the rest server path 
                          (e.g., 'http://server.com/memoza-rest-server' or 'http://server.com/whereoil-rest-server').
            kadme_token (str): The KADME security token required for API access.
            username (str): The username for authentication.
            password (str, optional): The password for password-based authentication. 
                                    Required if ticket is not provided.
            ticket (str, optional): An existing authentication ticket for ticket-based authentication.
                                  Required if password is not provided.
            valid_until (str, optional): The ticket expiration timestamp. Used with ticket authentication.
            timeout (float, optional): Request timeout in seconds. Defaults to 120.

        Raises:
            ValueError: If neither password nor ticket is provided, or if required parameters are invalid.

        Example:
            ```python
            import configparser
            from pymrs import AsyncMRSClient
            
            # Load credentials from config file
            config = configparser.ConfigParser()
            config.read("secrets.ini")
            host = config["API"]["HOSTNAME"]
            kadme_token = config["API"]["KADME_TOKEN"]
            username = config["API"]["USERNAME"]
            password = config["API"]["PASSWORD"]
            
            # Initialize with password authentication
            client = AsyncMRSClient(host, kadme_token, username, password)
            await client._autheticate()
            
            # Initialize with ticket authentication
            # client = AsyncMRSClient(host, kadme_token, username, ticket=existing_ticket)
            await client._autheticate()
            ```
        """
        try:
            _MRSClientConfig(
                hostname=hostname,
                kadme_token=kadme_token,
                username=username,
                password=password,
                ticket=ticket
            )
        except ValidationError as e:
            raise ValueError(e)

        self.hostname = hostname
        self.username = username
        self.kadme_token = kadme_token
        self.auth_type = AuthType.TICKET if ticket is not None else AuthType.PASSWORD
        self.valid_until = valid_until
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "kadme.security.token": self.kadme_token,
            },
            timeout=timeout,
        )
        if self.auth_type == AuthType.PASSWORD:
            self._ticket = ""
            self.password = password
        else:
            self._ticket = ticket
            self.client.headers.update({"ticket": f"{ticket}"})
        # {<namespace>: {"role_service": <role_service_value>, "roles": [<role_name>, ...]}}
        self._roles_cache: Dict[str, Dict[str, list[str]]] = {}

    async def _authenticate(self, oauth_token=None) -> str:
        """Authenticate with the MRS server and obtain an authentication ticket.

        This method handles authentication based on the configured auth_type:
        - For PASSWORD auth: Sends login request with username/password to get a new ticket
        - For TICKET auth: Validates the existing ticket without creating a new session
        
        The method also supports OAuth token authentication when provided.

        Args:
            oauth_token (str, optional): OAuth token from Azure for enhanced authentication.
                                       When provided, it's included in the Authorization header.

        Returns:
            str: The authentication ticket that can be used for subsequent API calls.

        Raises:
            MRSClientError: If authentication fails or ticket validation fails.
            
        Note:
            This method is automatically called when using the client as a context manager
            with password-based authentication. For ticket-based authentication, it validates
            the existing ticket instead of creating a new session.
        """

        if self.auth_type == AuthType.PASSWORD:
            payload = {"userName": self.username, "password": self.password}
            url = f"{self.hostname}/security/auth/login.json"
            logging.debug(f"POST: {url}")
            if oauth_token != None:
                headers = {"Authorization": f"Bearer {oauth_token}"}
                r = await self.client.post(url, headers=headers, json=payload)
            else:
                r = await self.client.post(url, json=payload)
            r_json = r.json()
            if r.status_code != 200:
                await self._handle_error(r)
            ticket = r_json["ticket"]
            self.valid_until = r_json['validUntil']
            self.client.headers.update({"ticket": f"{ticket}"})
            return ticket
        else:
            if not await self.validate_ticket():
                raise MRSClientError(401, f"Ticket validation failed, username: {self.username}, ticket: {self.ticket}, valid_until: {self.valid_until}")
            else:
                return self._ticket

    async def validate_ticket(self):
        """
        Validates the current ticket by calling the validateticket.json endpoint.
        
        Returns:
            bool: True if the ticket is valid, False otherwise.
            
        Raises:
            MRSClientError: If there's an error during the validation process.
        """ 
        try:
            response = await self.client.get(f"{self.hostname}/security/auth/validateticket.json")
            
            if response.status_code == 200:
                # Response is a timestamp in milliseconds since Unix epoch
                timestamp_ms = int(response.text.strip("<p>").strip("</p>"))
                expiration_date = datetime.fromtimestamp(timestamp_ms / 1000)
                # Format to ISO 8601 format like "2021-08-23T17:35:18"
                self.valid_until = expiration_date.strftime("%Y-%m-%dT%H:%M:%S")
                return True
            else:
                return False
        except Exception as e:
            raise MRSClientError(500, f"Error validating ticket: {str(e)}")

    @property
    async def headers(self):
        """
        Property that returns headers stored in current client session after validating them.
        """
        if self.auth_type == AuthType.PASSWORD:
            await self.validate_ticket()
        return self.client.headers

    @property
    async def ticket(self):
        """
        Property that returns currently stored ticket after validating it.
        """
        if self.auth_type == AuthType.PASSWORD:
            await self.validate_ticket()
        return self._ticket

    async def close(self):
        """Close the client session and clean up resources.

        For password-based authentication, this method logs out from the MRS server
        to properly terminate the session. For ticket-based authentication, it only
        closes the HTTP client without affecting the external ticket session.
        
        The HTTP client connection is always closed to free up resources.

        Raises:
            httpx.HTTPStatusError: If an HTTP error occurs during logout.
            
        Warning:
            After calling this method, the client instance should not be used for
            further requests. Create a new instance if additional operations are needed.
            
        Note:
            When using the client as an async context manager, this method is called
            automatically and should not be called manually. Only call this method
            when managing the client lifecycle manually.

        Example:
            ```python
            # Manual session management
            client = AsyncMRSClient(host, kadme_token, username, password)
            await client._authenticate()
            try:
                # Use client for operations
                result = await client.get_all_namespaces()
            finally:
                await client.close()  # Always clean up
            ```
        """

        # ```py
        # import asyncmrs

        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # await client.close() #dangerous call in itself not recommended for usage
        # await client.client.aclose() #close session after usage
        # ```
        headers = {
            "ticket": f"{self._ticket}",
        }
        logout_url = f"{self.hostname}/security/auth/logout.json"
        try:
            if self.auth_type == AuthType.PASSWORD: # не будем убивать TICKET-сессию, так как она пришла вместе с тикетом из Мемозы
                r = await self.client.post(logout_url, headers=headers, timeout=10.0)

                logging.info(f"Logout from MRS successful: {r.text}")
                r.raise_for_status()
        except httpx.HTTPStatusError as e:
            # if e.response.status_code == 401:
            #     logging.warning(
            #         "Received 401 Unauthorized during logout. Assuming the session is deactivated."
            #     )
            # else:
            #     logging.error(f"HTTP error occurred during logout: {e}")
            await self.client.aclose()
            raise e
        finally:
            # Always close the client, even if logout succeeds
            await self.client.aclose()

    async def __aenter__(self):
        """Enter the async context manager and authenticate if needed.
        
        When using password-based authentication, this method automatically calls
        _authenticate() to establish a session. For ticket-based authentication,
        the existing ticket is used without additional authentication.
        
        Returns:
            AsyncMRSClient: The initialized client instance ready for use.
            
        Example:
            ```python
            async with AsyncMRSClient(host, kadme_token, username, password) as client:
                namespaces = await client.get_all_namespaces()
                # Session is automatically managed
            ```
        """
        if self.auth_type == AuthType.PASSWORD:
            await self._authenticate()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the async context manager and clean up resources.
        
        This method ensures proper cleanup by calling close() to logout from the server
        (for password-based auth) and close the HTTP client connection. It's called
        automatically when exiting the async context manager, even if an exception occurs.
        
        Args:
            exc_type: The exception type if an exception was raised in the context.
            exc_value: The exception value if an exception was raised in the context.
            traceback: The traceback if an exception was raised in the context.
            
        Note:
            This method guarantees cleanup regardless of whether the context block
            completed successfully or raised an exception.
        """
        await self.close()

    async def _handle_error(self, response: httpx.Response):
        """
        Handles errors raised during a RESTful request.

        Args:
            response (httpx.Response): The HTTP response object.

        Raises:
            MRSClientError: If the response status code is not 200 (OK). The exception
                            will contain the error code and message returned by the server.
        """
        error_data = response.json()
        logging.error(error_data)

        # Check if the error data contains a code
        if isinstance(error_data.get("error"), dict):
            error_code = error_data["error"].get("code", response.status_code)
            error_message = error_data["error"].get("message", "Unknown Error")
        else:
            error_code = response.status_code
            error_message = error_data.get("error", "Unknown Error")

        raise MRSClientError(error_code, error_message)

    async def request(
        self,
        method: str,
        endpoint: str,
        data=None,
        json=None,
        headers=None,
        enable_validation=True,
    ) -> dict | None:
        """
        Makes a RESTful request to the specified endpoint using the provided HTTP method and JSON data.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): The endpoint path relative to the MRS server base URL.
            json (dict, optional): The JSON data to send with the request (default is None).
            enable_validation (bool, optional): by default this method always validates ticket before sending the request but this field
                        can be set to False to skip tocket validation. For example this can be useful when sending multiple requests knowing that ticket hasn't been expired yet

        Returns:
            dict | None: The JSON response data parsed as a Python dictionary.

        Raises:
            ValueError: If the HTTP method is not one of GET, POST, PUT, or DELETE.
        """

        # ```py
        # import mrs

        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # r = await client.request("POST", "/security/auth/login.json", "{"userName": username, "password": password}")
        # await client.client.aclose() #close session after usage
        # ```

        if hasattr(self, "password") and enable_validation:
            await self.validate_ticket()
        if method not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("The REST method is not supported!")
        url: str = f"{self.hostname}{endpoint}"
        logging.debug(f"HTTP {method}: {url}")
        if data:
            logging.debug(f"BODY: {data}")
        r = await self.client.request(
            method, url, headers=headers, data=data, json=json
        )
        if r.status_code != 200:
            await self._handle_error(r)
        try:
            return r.json()
        except JSONDecodeError:
            return None

    async def get_all_namespaces(self):
        return await self.request("GET", "/schema/nsp.json")

    async def get_namespace(self, namespace: str):
        return await self.request("GET", f"/schema/nsp/{namespace}.json")

    async def get_datatype(self, namespace: str, datatype: str):
        return await self.request("GET", f"/schema/nsp/{namespace}/{datatype}.json")

    async def es_request(
        self,
        es_host: str,
        es_port: int,
        memoza_namespace: str,
        memoza_class: str,
        es_index: str,
        es_query: Callable[[str, bool, list[str]], Dict[str, Any]],
        enable_validation: bool = True,
    ):
        """
        Makes a request to the Elasticsearch "es_index/_search" API endpoint using POST method.
        User roles are used to filter the data returned by Elasticsearch (via "kmeta:Ent" field).
        create_es_query must contain:
            - "terms" with "kmeta:Ent" field to use roles filtering.
            - "term" with "type" field to specify the Memoza class.
        Args:
            es_host (str): The Elasticsearch host.
            es_port (int): The Elasticsearch port.
            memoza_namespace (str): The Memoza namespace.
            memoza_class (str): The Memoza class.
            es_index (str): The Elasticsearch index.
            es_query (Callable[[str], Dict[str, Any]]): The Elasticsearch query function.
            enable_validation (bool, optional): by default this method always validates ticket before sending the request but this field
                can be set to False to skip tocket validation. For example this can be useful when sending multiple requests knowing that ticket
            hasn't been expired yet

        Returns:
            dict: The JSON response data parsed as a Python dictionary.

        Raises:
            PermissionError: If user does not have access to the Memoza namespace or class.
        """

        # ```py
        # Example usage for es_query callable:
        # def create_es_query(mrs_class: str, apply_roles_filter: bool, kmeta_ent: List[str]) -> Dict[str, Any]:
        # if apply_roles_filter:
        #    query = {
        #        "query": {
        #           "bool": {
        #                "must": [
        #                    {"term": {"type": mrs_class}},
        #                    {"match": {"field": "value"}},
        #                ]
        #            }
        #        }
        #    }
        #    if apply_roles_filter:
        #        query["query"]["bool"]["must"].append({
        #            "terms": {
        #                "kmeta:Ent": kmeta_ent
        #            }
        #        })
        # ```

        es_config = ElasticsearchConfig(
            host=es_host,
            port=es_port,
        )

        # Check user permissions
        permissions_url = f"/permissions/permissions.json?object={memoza_namespace}"
        permissions_response = await self.request(
            "GET", permissions_url, enable_validation=enable_validation
        )
        logging.debug(
            f"es_request: Permissions {memoza_namespace} response: {permissions_response}"
        )

        if not permissions_response or not permissions_response["VISIBLE"]:
            raise PermissionError(
                f"User does not have access to namespace: {memoza_namespace}"
            )

        permissions_url = f"/permissions/permissions.json?object={memoza_class}"
        permissions_response = await self.request(
            "GET", permissions_url, enable_validation=enable_validation
        )
        logging.debug(
            f"es_request: Permissions {memoza_class} response: {permissions_response}"
        )

        if not permissions_response or not permissions_response["VISIBLE"]:
            raise PermissionError(
                f"User does not have access to class: {memoza_class} in namespace: {memoza_namespace}"
            )

        apply_roles_filter, user_roles = await self.get_user_roles(memoza_namespace)
        logging.debug(f"User roles for namespace {memoza_namespace}: {user_roles}")
        query = es_query(memoza_class, apply_roles_filter, user_roles)

        # Encode the query to ensure proper handling of non-ASCII characters
        encoded_query = json.dumps(query, ensure_ascii=False).encode("utf-8")

        logging.debug(f"Generated Elasticsearch query: {encoded_query.decode('utf-8')}")

        # Prepare and send request to Elasticsearch
        es_url = f"{es_config.url}{es_index}/_search"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        logging.debug(f"Sending request to Elasticsearch: {es_url}")
        logging.debug(f"Request headers: {headers}")
        logging.debug(f"Request body: {encoded_query.decode('utf-8')}")

        async with httpx.AsyncClient() as es_client:
            response = await es_client.post(es_url, json=query, headers=headers)
            logging.debug(f"es_request: Elasticsearch response: {response}")

        if response.status_code != 200:
            await self._handle_error(response)
        try:
            return response.json()
        except JSONDecodeError:
            return None

    async def get_user_roles(self, namespace: str) -> tuple[bool, list[str]]:
        """
        Get user roles for a specific namespace. Roles are relevant only if role_service is enabled.
        If role_service is not enabled, the method returns an empty list. If role_service is enabled,
        the method returns a list of roles for the user, role "P" (Public) is added automatically.
        Retrieved roles are cached for the namespace.

        Args:
            namespace (str): The namespace to get roles for.

        Returns:
            tuple[bool, list[str]]: A tuple containing:
                - A boolean indicating whether role_service is enabled
                - A list of strings containing the user's roles for the specified namespace.

        Note:
            This method caches the results for each namespace to avoid unnecessary requests.
        """
        logging.debug(f"Getting user roles for namespace: {namespace}")

        if namespace not in self._roles_cache:
            logging.debug(
                f"Roles for namespace {namespace} not found in cache. Fetching from server."
            )
            endpoint = f"/settings/data/{namespace}.json"
            role_service_r = await self.request("GET", endpoint)
            self._roles_cache[namespace] = {}
            self._roles_cache[namespace]["role_service"] = role_service_r.get(
                "role_service"
            )

            if self._roles_cache[namespace]["role_service"]:
                logging.debug(
                    f"Role service enabled for namespace {namespace}. Fetching roles."
                )
                endpoint = f"/security/roles/nsp/{namespace}.json"
                roles = await self.request("GET", endpoint)
                self._roles_cache[namespace]["roles"] = roles + ["P"]
                logging.debug(
                    f"Roles fetched for namespace {namespace}: {self._roles_cache[namespace]['roles']}"
                )
            else:
                logging.debug(
                    f"Role service not enabled for namespace {namespace}. Using empty role list."
                )
                self._roles_cache[namespace]["roles"] = []
        else:
            logging.debug(f"Using cached roles for namespace {namespace}")

        role_service_enabled = bool(self._roles_cache[namespace]["role_service"])
        roles = self._roles_cache[namespace]["roles"]
        logging.debug(
            f"Returning roles for namespace {namespace}: role_service_enabled={role_service_enabled}, roles={roles}"
        )
        return role_service_enabled, roles

    async def upload_file(
        self, domain: dict, destinationPath: str, data: bytes
    ) -> dict | None:
        """
        Upload a file to the server.

        Args:
            domain (dict):  The metaDomain record linked to the file. In JSON format: {"type": "theschemaclass", "uri": "UNIQUEID"}
            destinationPath (str): The desired path to the file in MRS server.
            data (bytes): The actual file to be uploaded in binary format.

        Returns:
            dict | None: The response is a JSON-format of the metaDomain that was submitted,
                with additional properties populated reflecting the stored file in the respective storage.
                None if an error happend during request.
        """
        files = {
            "domain": (json.dumps(domain), "application/json"),
            "destinationPath": (destinationPath, "text/plain"),
            "file": (data, "application/octet-stream"),
        }
        url: str = f"/upload/fileTo.json"
        headers = {"Content-Type": f"multipart/form-data; boundary={domain['uri']}"}

        response = await self.request(
            method="POST", endpoint=url, data=files, headers=headers
        )
        return response
