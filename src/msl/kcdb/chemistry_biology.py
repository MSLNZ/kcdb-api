"""Search the Chemistry and Biology database."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .kcdb import AsyncKCDB, SyncKCDB, check_page_info, to_countries, to_label
from .types import Analyte, Category, Domain, ResultsChemistryBiology, Status

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from .kcdb import Response
    from .types import Country, MetrologyArea
    from .typing import JSON


class ChemistryBiology(SyncKCDB):
    """Chemistry and Biology class."""

    DOMAIN: Domain = Domain(code="CHEM-BIO", name="Chemistry and Biology")
    """The Chemistry and Biology domain."""

    def analytes(self) -> list[Analyte]:
        """Return all Chemistry and Biology analytes.

        Returns:
            A list of [Analyte][msl.kcdb.types.Analyte]s.
        """
        return _analytes(self.get(f"{self.BASE_URL}/referenceData/analyte"))

    def categories(self) -> list[Category]:
        """Return all Chemistry and Biology categories.

        Returns:
            A list of [Category][msl.kcdb.types.Category]'s.
        """
        return _categories(self.get(f"{self.BASE_URL}/referenceData/category"))

    def search(
        self,
        *,
        analyte: str | Analyte | None = None,
        category: str | Category | None = None,
        countries: str | Country | Iterable[str | Country] | None = None,
        keywords: str | None = None,
        metrology_area: str | MetrologyArea = "QM",
        page: int = 0,
        page_size: int = 100,
        public_date_from: str | date | None = None,
        public_date_to: str | date | None = None,
        show_table: bool = False,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsChemistryBiology:
        """Perform a Chemistry and Biology search.

        Args:
            analyte: Analyte label. _Example:_ `"antimony"`
            category: Category label. _Example:_ `"5"`
            countries: Country label(s). _Example:_ `["CH", "FR", "JP"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR multichannel OR water"`
            metrology_area: Metrology area label. _Example:_ `"QM"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            public_date_from: Minimal publication date. _Example:_ `"2005-01-31"`
            public_date_to: Maximal publication date. _Example:_ `"2020-06-30"`
            show_table: Set to `True` to return table data.
            status: CMC status.

        Returns:
            The CMC results for Chemistry and Biology.
        """
        return _search(
            self.post(
                f"{self.BASE_URL}/cmc/searchData/chemistryAndBiology",
                json=_prepare_search(
                    analyte=analyte,
                    category=category,
                    countries=countries,
                    keywords=keywords,
                    metrology_area=metrology_area,
                    page=page,
                    page_size=page_size,
                    public_date_from=public_date_from,
                    public_date_to=public_date_to,
                    show_table=show_table,
                    status=status,
                ),
            )
        )


class AsyncChemistryBiology(AsyncKCDB):
    """Asynchronous Chemistry and Biology class.

    !!! note "Added in version 1.1.0"
    """

    DOMAIN: Domain = Domain(code="CHEM-BIO", name="Chemistry and Biology")
    """The Chemistry and Biology domain."""

    async def analytes(self) -> list[Analyte]:
        """Return all Chemistry and Biology analytes.

        Returns:
            A list of [Analyte][msl.kcdb.types.Analyte]s.
        """
        return _analytes(await self.get(f"{self.BASE_URL}/referenceData/analyte"))

    async def categories(self) -> list[Category]:
        """Return all Chemistry and Biology categories.

        Returns:
            A list of [Category][msl.kcdb.types.Category]'s.
        """
        return _categories(await self.get(f"{self.BASE_URL}/referenceData/category"))

    async def search(
        self,
        *,
        analyte: str | Analyte | None = None,
        category: str | Category | None = None,
        countries: str | Country | Iterable[str | Country] | None = None,
        keywords: str | None = None,
        metrology_area: str | MetrologyArea = "QM",
        page: int = 0,
        page_size: int = 100,
        public_date_from: str | date | None = None,
        public_date_to: str | date | None = None,
        show_table: bool = False,
        status: str | Status = Status.PUBLISHED,
    ) -> ResultsChemistryBiology:
        """Perform a Chemistry and Biology search.

        Args:
            analyte: Analyte label. _Example:_ `"antimony"`
            category: Category label. _Example:_ `"5"`
            countries: Country label(s). _Example:_ `["CH", "FR", "JP"]`
            keywords: Search keywords in elasticsearch format. _Example:_ `"phase OR multichannel OR water"`
            metrology_area: Metrology area label. _Example:_ `"QM"`
            page: Page number requested (0 means first page).
            page_size: Maximum number of elements in a page (maximum value is 10000).
            public_date_from: Minimal publication date. _Example:_ `"2005-01-31"`
            public_date_to: Maximal publication date. _Example:_ `"2020-06-30"`
            show_table: Set to `True` to return table data.
            status: CMC status.

        Returns:
            The CMC results for Chemistry and Biology.
        """
        return _search(
            await self.post(
                f"{self.BASE_URL}/cmc/searchData/chemistryAndBiology",
                json=_prepare_search(
                    analyte=analyte,
                    category=category,
                    countries=countries,
                    keywords=keywords,
                    metrology_area=metrology_area,
                    page=page,
                    page_size=page_size,
                    public_date_from=public_date_from,
                    public_date_to=public_date_to,
                    show_table=show_table,
                    status=status,
                ),
            )
        )


def _analytes(response: Response) -> list[Analyte]:
    response.raise_for_status()
    return [Analyte(**data) for data in response.json()["referenceData"]]


def _categories(response: Response) -> list[Category]:
    response.raise_for_status()
    return [Category(**data) for data in response.json()["referenceData"]]


def _prepare_search(
    *,
    analyte: str | Analyte | None,
    category: str | Category | None,
    countries: str | Country | Iterable[str | Country] | None,
    keywords: str | None,
    metrology_area: str | MetrologyArea,
    page: int,
    page_size: int,
    public_date_from: str | date | None,
    public_date_to: str | date | None,
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

    request["metrologyAreaLabel"] = to_label(metrology_area)

    if analyte is not None:
        request["analyteLabel"] = to_label(analyte)

    if category:
        request["categoryLabel"] = to_label(category)

    if countries:
        request["countries"] = to_countries(countries)

    if keywords:
        request["keywords"] = keywords

    if public_date_from:
        request["publicDateFrom"] = str(public_date_from)

    if public_date_to:
        request["publicDateTo"] = str(public_date_to)

    return request


def _search(response: Response) -> ResultsChemistryBiology:
    response.raise_for_status()
    return ResultsChemistryBiology(response.json())
