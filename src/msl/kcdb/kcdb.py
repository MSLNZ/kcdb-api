"""Send requests to the KCDB server.

The [ChemistryBiology][msl.kcdb.chemistry_biology.ChemistryBiology],
[Physics][msl.kcdb.general_physics.Physics] and
[Radiation][msl.kcdb.ionizing_radiation.Radiation] classes all
inherit from the [SyncKCDB][msl.kcdb.kcdb.SyncKCDB] class so, typically, there should
be no reason to instantiate the [SyncKCDB][msl.kcdb.kcdb.SyncKCDB] class directly.

The [AsyncChemistryBiology][msl.kcdb.chemistry_biology.AsyncChemistryBiology],
[AsyncPhysics][msl.kcdb.general_physics.AsyncPhysics] and
[AsyncRadiation][msl.kcdb.ionizing_radiation.AsyncRadiation] classes all
inherit from the [AsyncKCDB][msl.kcdb.kcdb.AsyncKCDB] class so, typically, there should
be no reason to instantiate the [AsyncKCDB][msl.kcdb.kcdb.AsyncKCDB] class directly.
"""

# We could use third-party packages like "requests" or "httpx" but since the
# KCDB API is so basic (e.g., no authentication is required, trivial GET parameters),
# the builtin asyncio and urllib modules are sufficient.

from __future__ import annotations

import asyncio
import json as _json
import logging
import re
import ssl
from http.client import HTTPException, HTTPResponse
from io import BytesIO
from typing import TYPE_CHECKING, TypeVar
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ._version import __version__
from .types import (
    Country,
    Domain,
    IndividualService,
    MetrologyArea,
    NonIonizingQuantity,
    ReferenceData,
    ResultsQuickSearch,
    Service,
    Status,
    SubService,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    from .typing import JSON, PARAMS


HEADERS: dict[str, str] = {
    "User-Agent": f"msl-kcdb/{__version__}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


T = TypeVar("T", bound="ReferenceData")

logger = logging.getLogger("msl.kcdb")

SSL_CONTEXT = ssl.create_default_context()


def check_page_info(page: int, page_size: int) -> None:
    """Check that the page information for a request is valid."""
    if page < 0:
        msg = f"Invalid page value, {page}. Must be >= 0"
        raise ValueError(msg)

    if page_size < 1 or page_size > KCDB.MAX_PAGE_SIZE:
        msg = f"Invalid page size, {page_size}. Must be in the range [1, {KCDB.MAX_PAGE_SIZE}]"
        raise ValueError(msg)


def to_countries(countries: str | Country | Iterable[str | Country]) -> list[str]:
    """Convert the input into a list of countries."""
    if isinstance(countries, str):
        return [countries]
    if isinstance(countries, Country):
        return [countries.label]
    return [c if isinstance(c, str) else c.label for c in countries]


def to_label(obj: str | ReferenceData) -> str:
    """Convert the input into a string."""
    if isinstance(obj, str):
        return obj
    return obj.label


def to_physics_code(obj: str | Service | SubService | IndividualService) -> str:
    """Convert the input into a string."""
    if isinstance(obj, str):
        return obj
    return obj.physics_code


def _prepare_request(
    url: str, method: str, json: JSON | None = None, params: PARAMS | None = None
) -> tuple[str, bytes | None]:
    if params:
        # The KCDB API values are either an integer or a domain-code string
        # (which does not contain spaces and only letters A-Z or a hyphen),
        # so there is no need to convert the key-value pairs to be URL safe,
        # using urllib.parse.quote_plus(), since they already are safe.
        url += "?" + "&".join(f"{key}={value}" for key, value in params.items())

    data = _json.dumps(json, separators=(",", ":"), ensure_ascii=False) if json else None
    logger.debug("%s %s %s", method, url, data or "")
    return url, data.encode("utf-8") if data else None


def _request(
    *,
    url: str,
    method: str,
    json: JSON | None = None,
    params: PARAMS | None = None,
    timeout: float | None = 30,
) -> Response:
    """Send a synchronous request."""
    url, data = _prepare_request(url=url, method=method, json=json, params=params)
    try:
        with urlopen(Request(url, headers=HEADERS, data=data, method=method), timeout=timeout) as response:  # noqa: S310
            return Response(response)
    except HTTPError as e:
        return Response(e)
    except OSError as e:
        if "timed out" not in str(e):
            raise

    msg = f"No reply from KCDB server after {timeout} seconds"
    raise TimeoutError(msg)


async def _async_request(
    *,
    url: str,
    method: str,
    json: JSON | None = None,
    params: PARAMS | None = None,
    timeout: float | None = 30,
) -> Response:
    """Send an asynchronous request."""

    async def send(request: bytes) -> Response:
        reader, writer = await asyncio.open_connection(s.netloc, port, ssl=ctx)
        try:
            writer.write(request)
            await writer.drain()
            response = HTTPResponse(_MockSocket(await reader.read()))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
            response.url = url
            response.begin()
            return Response(response)
        finally:
            writer.close()
            await writer.wait_closed()

    url, data = _prepare_request(url=url, method=method, json=json, params=params)
    s = urlsplit(url, allow_fragments=False)
    port, ctx = (443, SSL_CONTEXT) if s.scheme == "https" else (80, None)
    path = s.path + "?" + s.query if params else s.path
    content = [f"{method} {path} HTTP/1.1", "Accept-Encoding: identity", f"Host: {s.netloc}"]
    content.extend(f"{key}: {value}" for key, value in HEADERS.items())
    if data:
        content.append(f"Content-Length: {len(data)}")
    content.extend(["Connection: close", "", ""])
    request = "\r\n".join(content).encode("utf-8") + (data or b"")

    try:
        return await asyncio.wait_for(send(request), timeout=timeout)
    except (asyncio.TimeoutError, OSError):
        msg = f"No reply from KCDB server after {timeout} seconds"
        raise TimeoutError(msg) from None


class _MockSocket:
    """Mock a socket."""

    def __init__(self, content: bytes) -> None:
        self.content: bytes = content

    def makefile(self, _mode: str) -> BytesIO:
        """Mock the `socket.makefile` method."""
        return BytesIO(self.content)


class Response:
    """A response from the KCDB server."""

    def __init__(self, response: HTTPResponse | HTTPError) -> None:
        """A response from the KCDB server.

        Args:
            response: The server's response to an HTTP request.
        """
        self._url: str = response.url
        self._code: int = 0 if response.status is None else response.status
        self._reason: str = response.reason
        self._data: bytes = response.read()

    @property
    def data(self) -> bytes:
        """The response body from the server."""
        return self._data

    def json(self) -> Any:  # noqa: ANN401
        """The JSON response body from the server."""
        return _json.loads(self._data)

    @property
    def ok(self) -> bool:
        """Whether the status code of the response is `HTTP 200 OK`."""
        return self._code == 200  # noqa: PLR2004

    def raise_for_status(self) -> None:
        """Raise an [HTTPException][http.client.HTTPException] only if the server returned an error."""
        typ: str = ""
        if 400 <= self._code < 500:  # noqa: PLR2004
            typ = "Client"
        elif 500 <= self._code < 600:  # noqa: PLR2004
            typ = "Server"

        if typ:
            msg = f"{typ} Error {self._code}: reason={self._reason!r}, url={self._url!r}"
            raise HTTPException(msg)

    @property
    def status_code(self) -> int:
        """The status code of the response."""
        return self._code


class KCDB:
    """KCDB base class."""

    BASE_URL: str = "https://www.bipm.org/api/kcdb"
    """The base url to the KCDB API."""

    MAX_PAGE_SIZE: int = 10_000
    """The maximum number of elements that can be returned in a single KCDB request."""

    DOMAIN: Domain = Domain(code="UNKNOWN", name="UNKNOWN")

    def __init__(self, timeout: float | None = 30) -> None:
        """Initialise the KCDB base class.

        Args:
            timeout: The maximum number of seconds to wait for a response from the KCDB server.
        """
        self._timeout: float | None
        self.timeout = timeout

    def __repr__(self) -> str:  # pyright: ignore[reportImplicitOverride]
        """Return the object representation."""
        return f"{self.__class__.__name__}(code={self.DOMAIN.code!r}, name={self.DOMAIN.name!r})"

    @staticmethod
    def filter(data: Iterable[T], pattern: str, *, flags: int = 0) -> list[T]:
        """Filter the reference data based on a pattern search.

        Args:
            data: An iterable of a [ReferenceData][msl.kcdb.types.ReferenceData] subclass.
            pattern: A [regular-expression](https://regexone.com/) pattern to use to filter results.
                Uses the `label` and `value` attributes of each item in `data` to perform the filtering.
            flags: Pattern flags passed to [re.compile][].

        Returns:
            The filtered reference data.
        """
        regex = re.compile(pattern, flags=flags)
        return [item for item in data if regex.search(item.value) or regex.search(item.label)]

    @property
    def timeout(self) -> float | None:
        """The timeout value, in seconds, to use for a KCDB request.

        Returns:
            The maximum number of seconds to wait for a response from the KCDB server. If `None`, there is no timeout.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: float | None) -> None:
        if value is None or value < 0:
            self._timeout = None
        else:
            self._timeout = float(value)


class SyncKCDB(KCDB):
    """Synchronous KCDB base class.

    !!! note "Added in version 1.1.0"
    """

    def countries(self) -> list[Country]:
        """Return all countries.

        Returns:
            A list of [Country][msl.kcdb.types.Country]'s.
        """
        return _countries(self.get(f"{self.BASE_URL}/referenceData/country"))

    def domains(self) -> list[Domain]:
        """Return all KCDB domains.

        Returns:
            A list of [Domain][msl.kcdb.types.Domain]s.
        """
        return _domains(self.get(f"{self.BASE_URL}/referenceData/domain"))

    def get(self, url: str, *, json: JSON | None = None, params: PARAMS | None = None) -> Response:
        """Send a GET request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serialisable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return _request(url=url, method="GET", json=json, params=params, timeout=self._timeout)

    def metrology_areas(self) -> list[MetrologyArea]:
        """Return all metrology areas.

        Returns:
            A list of [MetrologyArea][msl.kcdb.types.MetrologyArea]s.
        """
        return _metrology_areas(
            self.get(f"{self.BASE_URL}/referenceData/metrologyArea", params={"domainCode": self.DOMAIN.code}),
            self.DOMAIN,
        )

    def non_ionizing_quantities(self) -> list[NonIonizingQuantity]:
        """Return all non-Ionizing Radiation quantities.

        Returns:
            A list of [NonIonizingQuantity][msl.kcdb.types.NonIonizingQuantity]'s.
        """
        return _non_ionizing_quantities(self.get(f"{self.BASE_URL}/referenceData/quantity"))

    def post(self, url: str, *, json: JSON | None = None, params: PARAMS | None = None) -> Response:
        """Send a POST request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serialisable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return _request(url=url, method="POST", json=json, params=params, timeout=self._timeout)

    def quick_search(
        self,
        *,
        excluded_filters: Iterable[str] | None = None,
        included_filters: Iterable[str] | None = None,
        keywords: str | None = None,
        page: int = 0,
        page_size: int = 100,
        show_table: bool = False,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsQuickSearch:
        """Perform a quick search.

        Args:
            excluded_filters: Excluded filters. _Example:_ `["cmcServices.AC current", "cmcServices.AC power"]`
            included_filters: Included filters. _Example:_ `["cmcDomain.CHEM-BIO", "cmcBranches.Dimensional metrology"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR test"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            show_table: Set to `True` to return table data.
            status: CMC status.

        Returns:
            The CMC quick-search results.
        """
        return _quick_search(
            self.post(
                f"{self.BASE_URL}/cmc/searchData/quickSearch",
                json=_prepare_quick_search(
                    excluded_filters=excluded_filters,
                    included_filters=included_filters,
                    keywords=keywords,
                    page=page,
                    page_size=page_size,
                    show_table=show_table,
                    status=status,
                ),
            )
        )


class AsyncKCDB(KCDB):
    """Asynchronous KCDB base class.

    !!! note "Added in version 1.1.0"
    """

    async def countries(self) -> list[Country]:
        """Return all countries.

        Returns:
            A list of [Country][msl.kcdb.types.Country]'s.
        """
        return _countries(await self.get(f"{self.BASE_URL}/referenceData/country"))

    async def domains(self) -> list[Domain]:
        """Return all KCDB domains.

        Returns:
            A list of [Domain][msl.kcdb.types.Domain]s.
        """
        return _domains(await self.get(f"{self.BASE_URL}/referenceData/domain"))

    async def get(self, url: str, *, json: JSON | None = None, params: PARAMS | None = None) -> Response:
        """Send a GET request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serialisable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return await _async_request(url=url, method="GET", json=json, params=params, timeout=self._timeout)

    async def metrology_areas(self) -> list[MetrologyArea]:
        """Return all metrology areas.

        Returns:
            A list of [MetrologyArea][msl.kcdb.types.MetrologyArea]s.
        """
        return _metrology_areas(
            await self.get(f"{self.BASE_URL}/referenceData/metrologyArea", params={"domainCode": self.DOMAIN.code}),
            self.DOMAIN,
        )

    async def non_ionizing_quantities(self) -> list[NonIonizingQuantity]:
        """Return all non-Ionizing Radiation quantities.

        Returns:
            A list of [NonIonizingQuantity][msl.kcdb.types.NonIonizingQuantity]'s.
        """
        return _non_ionizing_quantities(await self.get(f"{self.BASE_URL}/referenceData/quantity"))

    async def post(self, url: str, *, json: JSON | None = None, params: PARAMS | None = None) -> Response:
        """Send a POST request to the KCDB server.

        Args:
            url: The URL for the request.
            json: A JSON-serialisable object to include in the body of the request.
            params: Query parameters to include in the URL.

        Returns:
            The response.
        """
        return await _async_request(url=url, method="POST", json=json, params=params, timeout=self._timeout)

    async def quick_search(
        self,
        *,
        excluded_filters: Iterable[str] | None = None,
        included_filters: Iterable[str] | None = None,
        keywords: str | None = None,
        page: int = 0,
        page_size: int = 100,
        show_table: bool = False,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsQuickSearch:
        """Perform a quick search.

        Args:
            excluded_filters: Excluded filters. _Example:_ `["cmcServices.AC current", "cmcServices.AC power"]`
            included_filters: Included filters. _Example:_ `["cmcDomain.CHEM-BIO", "cmcBranches.Dimensional metrology"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR test"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            show_table: Set to `True` to return table data.
            status: CMC status.

        Returns:
            The CMC quick-search results.
        """
        return _quick_search(
            await self.post(
                f"{self.BASE_URL}/cmc/searchData/quickSearch",
                json=_prepare_quick_search(
                    excluded_filters=excluded_filters,
                    included_filters=included_filters,
                    keywords=keywords,
                    page=page,
                    page_size=page_size,
                    show_table=show_table,
                    status=status,
                ),
            )
        )


def _countries(response: Response) -> list[Country]:
    response.raise_for_status()
    return [Country(**data) for data in response.json()["referenceData"]]


def _domains(response: Response) -> list[Domain]:
    response.raise_for_status()
    return [Domain(**data) for data in response.json()["domains"]]


def _metrology_areas(response: Response, domain: Domain) -> list[MetrologyArea]:
    response.raise_for_status()
    return [MetrologyArea(domain=domain, **data) for data in response.json()["referenceData"]]


def _non_ionizing_quantities(response: Response) -> list[NonIonizingQuantity]:
    response.raise_for_status()
    return [
        NonIonizingQuantity(id=d["id"], label="", value=d["value"])
        for d in response.json()["referenceData"]
        if d["label"] is None
    ]


def _prepare_quick_search(
    *,
    excluded_filters: Iterable[str] | None,
    included_filters: Iterable[str] | None,
    keywords: str | None,
    page: int,
    page_size: int,
    show_table: bool,
    status: str | Status,
) -> JSON:
    check_page_info(page, page_size)

    request: JSON = {
        "page": page,
        "pageSize": page_size,
        "showTable": show_table,
        "status": status.value if isinstance(status, Status) else status,
    }

    if excluded_filters:
        request["excludedFilters"] = list(excluded_filters)

    if included_filters:
        request["includedFilters"] = list(included_filters)

    if keywords:
        request["keywords"] = keywords

    return request


def _quick_search(response: Response) -> ResultsQuickSearch:
    response.raise_for_status()
    return ResultsQuickSearch(response.json())
