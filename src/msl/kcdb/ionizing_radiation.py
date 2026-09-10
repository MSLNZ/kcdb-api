"""Search the Ionizing Radiation database."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .kcdb import AsyncKCDB, SyncKCDB, check_page_info, to_countries, to_label
from .types import Branch, Domain, Medium, Nuclide, Quantity, ResultsRadiation, Source, Status

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from .kcdb import Response
    from .types import Country, MetrologyArea
    from .typing import JSON

_MetrologyAreaID = 9
_BRANCHES: set[str] = {"RAD", "DOS", "NEU"}


class Radiation(SyncKCDB):
    """Ionizing Radiation class."""

    DOMAIN: Domain = Domain(code="RADIATION", name="Ionizing radiation")
    """The Ionizing Radiation domain."""

    def branches(self, metrology_area: MetrologyArea) -> list[Branch]:
        """Return all Ionizing Radiation branches for the specified metrology area.

        Args:
            metrology_area: The metrology area to return the branches for.

        Returns:
            A list of [Branch][msl.kcdb.types.Branch]es.
        """
        if metrology_area.id < _MetrologyAreaID:  # ignore PHYSICS and CHEM-BIO
            return []

        return _branches(
            self.get(
                f"{self.BASE_URL}/referenceData/branch",
                params={"areaId": metrology_area.id},
            ),
            metrology_area=metrology_area,
        )

    def mediums(self, branch: Branch) -> list[Medium]:
        """Return all Ionizing Radiation mediums for the specified branch.

        Args:
            branch: The branch to return the mediums for.

        Returns:
            A list of [Medium][msl.kcdb.types.Medium]s.
        """
        # The /radiationMedium endpoint does not accept parameters, so we need to filter the mediums
        # based on the Branch that is specified
        if branch.label not in _BRANCHES:
            return []

        return _mediums(
            self.get(f"{self.BASE_URL}/referenceData/radiationMedium"),
            branch=branch,
        )

    def nuclides(self) -> list[Nuclide]:
        """Return all Ionizing Radiation nuclides.

        Returns:
            A list of [Nuclide][msl.kcdb.types.Nuclide]s.
        """
        return _nuclides(self.get(f"{self.BASE_URL}/referenceData/nuclide"))

    def quantities(self, branch: Branch) -> list[Quantity]:
        """Return all Ionizing Radiation quantities for the specified branch.

        Args:
            branch: The branch to return the quantities for.

        Returns:
            A list of [Quantity][msl.kcdb.types.Quantity]'s.
        """
        # The /quantity endpoint does not accept parameters, so we need to filter the quantities
        # based on the Branch that is specified. There are many more quantities after id=78, but
        # these all have "label": null, so we ignore these additional quantities here and
        # provide them in KCDB.non_ionizing_quantities()
        if branch.label not in _BRANCHES:
            return []

        return _quantities(
            self.get(f"{self.BASE_URL}/referenceData/quantity"),
            branch=branch,
        )

    def search(  # noqa: PLR0913
        self,
        *,
        branch: str | Branch | None = None,
        countries: str | Country | Iterable[str | Country] | None = None,
        keywords: str | None = None,
        medium: str | Medium | None = None,
        metrology_area: str | MetrologyArea = "RI",
        nuclide: str | Nuclide | None = None,
        page: int = 0,
        page_size: int = 100,
        public_date_from: str | date | None = None,
        public_date_to: str | date | None = None,
        quantity: str | Quantity | None = None,
        show_table: bool = False,
        source: str | Source | None = None,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsRadiation:
        """Perform an Ionizing Radiation search.

        Args:
            branch: Branch label. _Example:_ `"RAD"`
            countries: Country label(s). _Example:_ `["CH", "FR", "JP"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR multichannel OR water"`
            medium: Medium label. _Example:_ `"3"`
            metrology_area: Metrology area label. _Example:_ `"RI"`
            nuclide: Nuclide label. _Example:_ `"Co-60"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            public_date_from: Minimal publication date. _Example:_ `"2005-01-31"`
            public_date_to: Maximal publication date. _Example:_ `"2020-06-30"`
            quantity: Quantity label. _Example:_ `"1"`
            show_table: Set to `True` to return table data.
            source: Source label. _Example:_ `"2"`
            status: CMC status.

        Returns:
            The CMC results for Ionizing Radiation.
        """
        return _search(
            self.post(
                f"{self.BASE_URL}/cmc/searchData/radiation",
                json=_prepare_search(
                    branch=branch,
                    countries=countries,
                    keywords=keywords,
                    medium=medium,
                    metrology_area=metrology_area,
                    nuclide=nuclide,
                    page=page,
                    page_size=page_size,
                    public_date_from=public_date_from,
                    public_date_to=public_date_to,
                    quantity=quantity,
                    show_table=show_table,
                    source=source,
                    status=status,
                ),
            )
        )

    def sources(self, branch: Branch) -> list[Source]:
        """Return all Ionizing Radiation sources for the specified branch.

        Args:
            branch: The branch to return the mediums for.

        Returns:
            A list of [Source][msl.kcdb.types.Source]s.
        """
        # The /radiationSource endpoint does not accept parameters, so we need to filter the sources
        # based on the Branch that is specified
        if branch.label not in _BRANCHES:
            return []

        return _sources(
            self.get(f"{self.BASE_URL}/referenceData/radiationSource"),
            branch=branch,
        )


class AsyncRadiation(AsyncKCDB):
    """Ionizing Radiation class.

    !!! note "Added in version 1.1.0"
    """

    DOMAIN: Domain = Domain(code="RADIATION", name="Ionizing radiation")
    """The Ionizing Radiation domain."""

    async def branches(self, metrology_area: MetrologyArea) -> list[Branch]:
        """Return all Ionizing Radiation branches for the specified metrology area.

        Args:
            metrology_area: The metrology area to return the branches for.

        Returns:
            A list of [Branch][msl.kcdb.types.Branch]es.
        """
        if metrology_area.id < _MetrologyAreaID:  # ignore PHYSICS and CHEM-BIO
            return []

        return _branches(
            await self.get(
                f"{self.BASE_URL}/referenceData/branch",
                params={"areaId": metrology_area.id},
            ),
            metrology_area=metrology_area,
        )

    async def mediums(self, branch: Branch) -> list[Medium]:
        """Return all Ionizing Radiation mediums for the specified branch.

        Args:
            branch: The branch to return the mediums for.

        Returns:
            A list of [Medium][msl.kcdb.types.Medium]s.
        """
        # The /radiationMedium endpoint does not accept parameters, so we need to filter the mediums
        # based on the Branch that is specified
        if branch.label not in _BRANCHES:
            return []

        return _mediums(
            await self.get(f"{self.BASE_URL}/referenceData/radiationMedium"),
            branch=branch,
        )

    async def nuclides(self) -> list[Nuclide]:
        """Return all Ionizing Radiation nuclides.

        Returns:
            A list of [Nuclide][msl.kcdb.types.Nuclide]s.
        """
        return _nuclides(await self.get(f"{self.BASE_URL}/referenceData/nuclide"))

    async def quantities(self, branch: Branch) -> list[Quantity]:
        """Return all Ionizing Radiation quantities for the specified branch.

        Args:
            branch: The branch to return the quantities for.

        Returns:
            A list of [Quantity][msl.kcdb.types.Quantity]'s.
        """
        # The /quantity endpoint does not accept parameters, so we need to filter the quantities
        # based on the Branch that is specified. There are many more quantities after id=78, but
        # these all have "label": null, so we ignore these additional quantities here and
        # provide them in KCDB.non_ionizing_quantities()
        if branch.label not in _BRANCHES:
            return []

        return _quantities(
            await self.get(f"{self.BASE_URL}/referenceData/quantity"),
            branch=branch,
        )

    async def search(  # noqa: PLR0913
        self,
        *,
        branch: str | Branch | None = None,
        countries: str | Country | Iterable[str | Country] | None = None,
        keywords: str | None = None,
        medium: str | Medium | None = None,
        metrology_area: str | MetrologyArea = "RI",
        nuclide: str | Nuclide | None = None,
        page: int = 0,
        page_size: int = 100,
        public_date_from: str | date | None = None,
        public_date_to: str | date | None = None,
        quantity: str | Quantity | None = None,
        show_table: bool = False,
        source: str | Source | None = None,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsRadiation:
        """Perform an Ionizing Radiation search.

        Args:
            branch: Branch label. _Example:_ `"RAD"`
            countries: Country label(s). _Example:_ `["CH", "FR", "JP"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR multichannel OR water"`
            medium: Medium label. _Example:_ `"3"`
            metrology_area: Metrology area label. _Example:_ `"RI"`
            nuclide: Nuclide label. _Example:_ `"Co-60"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            public_date_from: Minimal publication date. _Example:_ `"2005-01-31"`
            public_date_to: Maximal publication date. _Example:_ `"2020-06-30"`
            quantity: Quantity label. _Example:_ `"1"`
            show_table: Set to `True` to return table data.
            source: Source label. _Example:_ `"2"`
            status: CMC status.

        Returns:
            The CMC results for Ionizing Radiation.
        """
        return _search(
            await self.post(
                f"{self.BASE_URL}/cmc/searchData/radiation",
                json=_prepare_search(
                    branch=branch,
                    countries=countries,
                    keywords=keywords,
                    medium=medium,
                    metrology_area=metrology_area,
                    nuclide=nuclide,
                    page=page,
                    page_size=page_size,
                    public_date_from=public_date_from,
                    public_date_to=public_date_to,
                    quantity=quantity,
                    show_table=show_table,
                    source=source,
                    status=status,
                ),
            )
        )

    async def sources(self, branch: Branch) -> list[Source]:
        """Return all Ionizing Radiation sources for the specified branch.

        Args:
            branch: The branch to return the mediums for.

        Returns:
            A list of [Source][msl.kcdb.types.Source]s.
        """
        # The /radiationSource endpoint does not accept parameters, so we need to filter the sources
        # based on the Branch that is specified
        if branch.label not in _BRANCHES:
            return []

        return _sources(
            await self.get(f"{self.BASE_URL}/referenceData/radiationSource"),
            branch=branch,
        )


def _branches(response: Response, metrology_area: MetrologyArea) -> list[Branch]:
    response.raise_for_status()
    return [Branch(metrology_area=metrology_area, **data) for data in response.json()["referenceData"]]


def _mediums(response: Response, branch: Branch) -> list[Medium]:
    response.raise_for_status()
    data = response.json()["referenceData"]
    if branch.label == "RAD":
        return [Medium(branch=branch, **d) for d in data if d["id"] < 17]  # noqa: PLR2004
    if branch.label == "DOS":
        return [Medium(branch=branch, **d) for d in data if 17 <= d["id"] < 24]  # noqa: PLR2004
    return [Medium(branch=branch, **d) for d in data if d["id"] >= 24]  # noqa: PLR2004


def _nuclides(response: Response) -> list[Nuclide]:
    response.raise_for_status()
    return [Nuclide(**data) for data in response.json()["referenceData"]]


def _quantities(response: Response, branch: Branch) -> list[Quantity]:
    response.raise_for_status()
    data = response.json()["referenceData"]
    if branch.label == "DOS":
        return [Quantity(branch=branch, **d) for d in data if d["id"] < 32]  # noqa: PLR2004
    if branch.label == "RAD":
        return [Quantity(branch=branch, **d) for d in data if 32 <= d["id"] < 47]  # noqa: PLR2004
    return [Quantity(branch=branch, **d) for d in data if 47 <= d["id"] < 78]  # noqa: PLR2004


def _prepare_search(  # noqa: PLR0913
    *,
    branch: str | Branch | None,
    countries: str | Country | Iterable[str | Country] | None,
    keywords: str | None,
    medium: str | Medium | None,
    metrology_area: str | MetrologyArea,
    nuclide: str | Nuclide | None,
    page: int,
    page_size: int,
    public_date_from: str | date | None,
    public_date_to: str | date | None,
    quantity: str | Quantity | None,
    show_table: bool,
    source: str | Source | None,
    status: str | Status,
) -> JSON:
    check_page_info(page, page_size)

    request: JSON = {
        "page": page,
        "pageSize": page_size,
        "showTable": show_table,
        "status": status.value if isinstance(status, Status) else status,
    }

    request["metrologyAreaLabel"] = to_label(metrology_area)

    if branch:
        request["branchLabel"] = to_label(branch)

    if countries:
        request["countries"] = to_countries(countries)

    if keywords:
        request["keywords"] = keywords

    if medium:
        request["mediumLabel"] = to_label(medium)

    if nuclide:
        request["nuclideLabel"] = to_label(nuclide)

    if public_date_from:
        request["publicDateFrom"] = str(public_date_from)

    if public_date_to:
        request["publicDateTo"] = str(public_date_to)

    if quantity:
        request["quantityLabel"] = to_label(quantity)

    if source:
        request["sourceLabel"] = to_label(source)

    return request


def _search(response: Response) -> ResultsRadiation:
    response.raise_for_status()
    return ResultsRadiation(response.json())


def _sources(response: Response, branch: Branch) -> list[Source]:
    response.raise_for_status()
    data = response.json()["referenceData"]
    if branch.label == "DOS":
        return [Source(branch=branch, **d) for d in data if d["id"] < 32]  # noqa: PLR2004
    if branch.label == "RAD":
        return [Source(branch=branch, **d) for d in data if 32 <= d["id"] < 35]  # noqa: PLR2004
    return [Source(branch=branch, **d) for d in data if d["id"] >= 35]  # noqa: PLR2004
