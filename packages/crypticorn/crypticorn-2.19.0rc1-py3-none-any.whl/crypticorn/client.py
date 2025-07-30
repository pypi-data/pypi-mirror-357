from typing import Literal, TypeVar, Optional
import warnings
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from crypticorn.hive import HiveClient
from crypticorn.klines import KlinesClient
from crypticorn.pay import PayClient

from crypticorn.trade import TradeClient
from crypticorn.metrics import MetricsClient
from crypticorn.auth import AuthClient
from crypticorn._internal.warnings import CrypticornDeprecatedSince217, CrypticornDeprecatedSince219
from importlib.metadata import version
from typing_extensions import deprecated

ConfigT = TypeVar("ConfigT")
SubClient = TypeVar("SubClient")


class BaseAsyncClient:
    """
    Base class for Crypticorn API clients containing shared functionality.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt: Optional[str] = None,
        base_url: str = None,
        is_sync: bool = False,
        http_client: Optional[ClientSession] = None,
    ):
        """
        :param api_key: The API key to use for authentication (recommended).
        :param jwt: The JWT to use for authentication (not recommended).
        :param base_url: The base URL the client will use to connect to the API.
        :param is_sync: Whether this client should operate in synchronous mode.
        :param http_client: Optional aiohttp ClientSession to use for HTTP requests.
        """
        self._base_url = base_url.rstrip("/") if base_url else "https://api.crypticorn.com"
        self._api_key = api_key
        self._jwt = jwt
        self._is_sync = is_sync
        self._http_client = http_client
        self._owns_http_client = http_client is None  # whether we own the http client

        self._service_classes: dict[str, tuple[type[SubClient], str]] = {
            'hive-v1': (HiveClient, "v1/hive"),
            'trade-v1': (TradeClient, "v1/trade"),
            'klines-v1': (KlinesClient, "v1/klines"),
            'pay-v1': (PayClient, "v1/pay"),
            'metrics-v1': (MetricsClient, "v1/metrics"),
            'auth-v1': (AuthClient, "v1/auth"),
        }

        self._services: dict[str, SubClient] = self._create_services()

    def _create_services(self) -> dict[str, SubClient]:
        """Create services with the appropriate configuration based on sync/async mode."""
        services = {}
        for name, (client_class, path) in self._service_classes.items():
            config = self._get_default_config(client_class, path)
            # For sync clients, don't pass the persistent http_client
            # Let each operation manage its own session
            if self._is_sync:
                services[name] = client_class(
                    config, http_client=None, is_sync=self._is_sync
                )
            else:
                services[name] = client_class(
                    config, http_client=self._http_client, is_sync=self._is_sync
                )
        return services

    @property
    def base_url(self) -> str:
        """
        The base URL the client will use to connect to the API.
        """
        return self._base_url

    @property
    def api_key(self) -> Optional[str]:
        """
        The API key the client will use to connect to the API.
        This is the preferred way to authenticate.
        """
        return self._api_key

    @property
    def jwt(self) -> Optional[str]:
        """
        The JWT the client will use to connect to the API.
        This is the not the preferred way to authenticate.
        """
        return self._jwt

    @property
    def version(self) -> str:
        """
        The version of the client.
        """
        return version("crypticorn")

    @property
    def is_sync(self) -> bool:
        """
        Whether this client operates in synchronous mode.
        """
        return self._is_sync

    @property
    def http_client(self) -> Optional[ClientSession]:
        """
        The HTTP client session being used, if any.
        """
        return self._http_client


    @property
    @deprecated("The `hive` property is deprecated and will become a method in the next major release. Instead of `client.hive` you will need to use `client.hive(version='v1')`.", category=CrypticornDeprecatedSince219)
    def hive(self) -> HiveClient:
        """
        Entry point for the Hive AI API ([Docs](https://docs.crypticorn.com/api/?api=hive-ai-api)).
        """
        return self._services['hive-v1']

    @property
    @deprecated("The `trade` property is deprecated and will become a method in the next major release. Instead of `client.trade` you will need to use `client.trade(version='v1')`.", category=CrypticornDeprecatedSince219)
    def trade(self) -> TradeClient:
        """
        Entry point for the Trading API ([Docs](https://docs.crypticorn.com/api/?api=trading-api)).
        """
        return self._services['trade-v1']

    @property
    @deprecated("The `klines` property is deprecated and will become a method in the next major release. Instead of `client.klines` you will need to use `client.klines(version='v1')`.", category=CrypticornDeprecatedSince219)
    def klines(self) -> KlinesClient:
        """
        Entry point for the Klines API ([Docs](https://docs.crypticorn.com/api/?api=klines-api)).
        """
        return self._services['klines-v1']

    @property
    @deprecated("The `metrics` property is deprecated and will become a method in the next major release. Instead of `client.metrics` you will need to use `client.metrics(version='v1')`.", category=CrypticornDeprecatedSince219)
    def metrics(self) -> MetricsClient:
        """
        Entry point for the Metrics API ([Docs](https://docs.crypticorn.com/api/?api=metrics-api)).
        """
        return self._services['metrics-v1']

    @property
    @deprecated("The `pay` property is deprecated and will become a method in the next major release. Instead of `client.pay` you will need to use `client.pay(version='v1')`.", category=CrypticornDeprecatedSince219)
    def pay(self) -> PayClient:
        """
        Entry point for the Payment API ([Docs](https://docs.crypticorn.com/api/?api=payment-api)).
        """
        return self._services['pay-v1']

    @property
    @deprecated("The `auth` property is deprecated and will become a method in the next major release. Instead of `client.auth` you will need to use `client.auth(version='v1')`.", category=CrypticornDeprecatedSince219)
    def auth(self) -> AuthClient:
        """
        Entry point for the Auth API ([Docs](https://docs.crypticorn.com/api/?api=auth-api)).
        """
        return self._services['auth-v1']
    
    # TODO: add these as methods in the next major release and remove the properties
    # def hive(self, version: Literal["v1"]) -> HiveClient:
    #     """
    #     Entry point for the Hive AI API ([Docs](https://docs.crypticorn.com/api/?api=hive-ai-api)).
    #     """
    #     return self._services[f"hive-{version}"]

    # def trade(self, version: Literal["v1"]) -> TradeClient:
    #     """
    #     Entry point for the Trading API ([Docs](https://docs.crypticorn.com/api/?api=trading-api)).
    #     """
    #     return self._services[f"trade-{version}"]

    # def klines(self, version: Literal["v1"]) -> KlinesClient:
    #     """
    #     Entry point for the Klines API ([Docs](https://docs.crypticorn.com/api/?api=klines-api)).
    #     """
    #     return self._services[f"klines-{version}"]

    # def metrics(self, version: Literal["v1"]) -> MetricsClient:
    #     """
    #     Entry point for the Metrics API ([Docs](https://docs.crypticorn.com/api/?api=metrics-api)).
    #     """
    #     return self._services[f"metrics-{version}"]

    # def pay(self, version: Literal["v1"]) -> PayClient:
    #     """
    #     Entry point for the Payment API ([Docs](https://docs.crypticorn.com/api/?api=payment-api)).
    #     """
    #     return self._services[f"pay-{version}"]

    # def auth(self, version: Literal["v1"]) -> AuthClient:
    #     """
    #     Entry point for the Auth API ([Docs](https://docs.crypticorn.com/api/?api=auth-api)).
    #     """
    #     return self._services[f"auth-{version}"]

    def configure(self, config: ConfigT, service: str) -> None:
        """
        Update a sub-client's configuration by overriding with the values set in the new config.
        Useful for testing a specific service against a local server instead of the default proxy.

        :param config: The new configuration to use for the sub-client.
        :param service: The service to configure.

        Example:
        >>> # For async client
        >>> async with AsyncClient() as client:
        ...     client.configure(config=HiveConfig(host="http://localhost:8000"), service='hive-v1')
        >>>
        >>> # For sync client
        >>> with SyncClient() as client:
        ...     client.configure(config=HiveConfig(host="http://localhost:8000"), service='hive-v1')
        """
        assert service in self._service_classes, f"Invalid service: {service}. Must be one of {list(self._service_classes.keys())}"
        client = self._services[service]
        new_config = client.config
        for attr in vars(config):
            new_value = getattr(config, attr)
            if new_value:
                setattr(new_config, attr, new_value)

        # Recreate service with new config and appropriate parameters
        if self._is_sync:
            self._services[service] = type(client)(
                new_config, is_sync=self._is_sync, http_client=self._http_client
            )
        else:
            self._services[service] = type(client)(
                new_config, http_client=self._http_client
            )

    def _get_default_config(self, client_class: type[SubClient], path: str):
        config_class = client_class.config_class
        return config_class(
            host=f"{self.base_url}/{path.lstrip('/').rstrip('/')}",
            access_token=self.jwt,
            api_key={'APIKeyHeader': self.api_key} if self.api_key else None,
        )

    async def close(self):
        """Close the client and clean up resources."""
        # close each service
        for service in self._services.values():
            if (
                hasattr(service, "base_client")
                and hasattr(service.base_client, "close")
                and self._owns_http_client
            ):
                await service.base_client.close()
        # close shared http client if we own it
        if self._http_client and self._owns_http_client:
            await self._http_client.close()
            self._http_client = None

    def _ensure_session(self) -> None:
        """
        Lazily create the shared HTTP client when first needed and pass it to all subclients.
        """
        if self._http_client is None:
            self._http_client = ClientSession(
                timeout=ClientTimeout(total=30.0),
                connector=TCPConnector(limit=100, limit_per_host=20),
                headers={"User-Agent": f"crypticorn/python/{self.version}"},
            )
            # Update services to use the new session
            self._services = self._create_services()


class AsyncClient(BaseAsyncClient):
    """
    The official async Python client for interacting with the Crypticorn API.
    It is consisting of multiple microservices covering the whole stack of the Crypticorn project.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt: Optional[str] = None,
        base_url: str = None,
        *,
        http_client: Optional[ClientSession] = None,
    ):
        """
        :param api_key: The API key to use for authentication (recommended).
        :param jwt: The JWT to use for authentication (not recommended).
        :param base_url: The base URL the client will use to connect to the API.
        :param http_client: The HTTP client to use for the client.
        """
        # Initialize as async client
        super().__init__(api_key, jwt, base_url, is_sync=False, http_client=http_client)

    async def close(self):
        await super().close()

    async def __aenter__(self):
        self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


@deprecated("Use AsyncClient instead", category=None)
class ApiClient(AsyncClient):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ApiClient is deprecated. Use AsyncClient instead.",
            CrypticornDeprecatedSince217,
        )
        super().__init__(*args, **kwargs)


class SyncClient(BaseAsyncClient):
    """
    The official synchronous Python client for interacting with the Crypticorn API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt: Optional[str] = None,
        base_url: str = None,
        *,
        http_client: Optional[ClientSession] = None,
    ):
        """
        :param http_client: Optional aiohttp ClientSession to use for HTTP requests.
                          Note: For sync client, session management is handled automatically.
        """
        super().__init__(api_key, jwt, base_url, is_sync=True, http_client=http_client)

    def close(self):
        """Close the client and clean up resources."""
        # For sync client, don't maintain persistent sessions
        # Each operation creates its own session within async_to_sync
        self._http_client = None

    def _ensure_session(self) -> None:
        """
        For sync client, don't create persistent sessions.
        Let each async_to_sync call handle its own session.
        """
        # Don't create persistent sessions in sync mode
        # Each API call will handle session creation/cleanup within async_to_sync
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """Automatic cleanup when the object is garbage collected."""
        try:
            self.close()
        except Exception:
            pass
