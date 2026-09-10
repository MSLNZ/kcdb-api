from __future__ import annotations

import json

import pytest

from msl.kcdb.kcdb import AsyncKCDB, SyncKCDB


class TestSyncKCDB:
    """Test the synchronous KCDB base class."""

    def setup_class(self) -> None:
        """Create KCDB instance."""
        self.kcdb: SyncKCDB = SyncKCDB()  # pyright: ignore[reportUninitializedInstanceVariable]

    def test_countries(self) -> None:
        """Test KCDB.countries()."""
        countries = self.kcdb.countries()
        assert len(countries) > 100

        country, *rest = self.kcdb.filter(countries, "NZ")
        assert not rest
        assert country.id == 58
        assert country.label == "NZ"
        assert country.value == "New Zealand"

    def test_domains(self) -> None:
        """Test KCDB.domains()."""
        chem, phys, rad = sorted(self.kcdb.domains())
        assert chem.code == "CHEM-BIO"
        assert chem.name == "Chemistry and Biology"
        assert phys.code == "PHYSICS"
        assert phys.name == "General physics"
        assert rad.code == "RADIATION"
        assert rad.name == "Ionizing radiation"

    def test_domain_response(self) -> None:
        """The the Response object for the 'referenceData/domain' request."""
        response = self.kcdb.get(f"{SyncKCDB.BASE_URL}/referenceData/domain")
        response.raise_for_status()
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "domains": [
                {"code": "CHEM-BIO", "name": "Chemistry and Biology"},
                {"code": "PHYSICS", "name": "General physics"},
                {"code": "RADIATION", "name": "Ionizing radiation"},
            ]
        }

    def test_invalid_page_value(self) -> None:
        """Test page value invalid."""
        with pytest.raises(ValueError, match=r"Must be >= 0"):
            _ = self.kcdb.quick_search(page=-1)

    def test_invalid_page_size_value(self) -> None:
        """Test page_size value invalid."""
        with pytest.raises(ValueError, match=r"Invalid page size"):
            _ = self.kcdb.quick_search(page_size=0)

    def test_non_ionizing_quantities(self) -> None:
        """Test KCDB.non_ionizing_quantities()."""
        quantities = self.kcdb.non_ionizing_quantities()
        assert len(quantities) > 1000

        quantity, *rest = self.kcdb.filter(quantities, "Sound pressure response")
        assert not rest
        assert quantity is not None
        assert quantity.id == 78
        assert quantity.value == "Sound pressure response level"

    def test_quick_search(self) -> None:
        """Test KCDB.quick_search()."""
        quick = self.kcdb.quick_search(
            keywords="phase OR test",
            included_filters=[
                "cmcDomain.CHEM-BIO",
                "cmcBranches.Dimensional metrology",
            ],
            excluded_filters=[
                "cmcServices.AC current",
                "cmcServices.AC power",
            ],
        )

        assert str(quick).startswith("ResultsQuickSearch(")
        assert quick.total_elements > 40

        found_cmc_domain = False
        found_chem_bio = False
        assert len(quick.filters_list) > 3
        for item in quick.filters_list:
            if item.code == "cmcDomain":
                found_cmc_domain = True
                assert (
                    str(item) == "ResultFilter(code='cmcDomain', count=0, name='cmcDomain', order=0, len(children)=3)"
                )
                for child in item.children:
                    if child.name == "CHEM-BIO":
                        found_chem_bio = True
                        assert child.code == "cmcDomain.CHEM-BIO"
                        assert child.name == "CHEM-BIO"
                        assert child.count > 50
                        assert child.order == -1
                        assert child.children == []
                        break
                break
        assert found_cmc_domain
        assert found_chem_bio

        found_cmc_rmo = False
        assert len(quick.aggregations) > 2
        for aggregation in quick.aggregations:
            if aggregation.name == "cmcRmo":
                found_cmc_rmo = True
                assert str(aggregation) == "ResultAggregation(name='cmcRmo', len(values)=3)"
                rmos = aggregation.values
                assert "EURAMET" in rmos
                assert "SIM" in rmos
                assert "APMP" in rmos
        assert found_cmc_rmo

    def test_timeout(self) -> None:
        """Test timeout setter/getter and error message."""
        original = self.kcdb.timeout

        self.kcdb.timeout = 100
        assert isinstance(self.kcdb.timeout, float)
        assert self.kcdb.timeout == 100.0

        self.kcdb.timeout = None
        assert self.kcdb.timeout is None

        # make sure that get(url, timeout=None) is okay
        assert len(self.kcdb.domains()) == 3

        self.kcdb.timeout = -1
        assert self.kcdb.timeout is None

        # Making the timeout value be very small causes a urllib.error.URLError
        # instead of a TimeoutError
        self.kcdb.timeout = 0.01  # type: ignore[unreachable]
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.01 seconds"):
            _ = self.kcdb.quick_search()

        self.kcdb.timeout = original


class TestAsyncKCDB:
    """Test the asynchronous KCDB base class."""

    def setup_class(self) -> None:
        """Create KCDB instance."""
        self.kcdb: AsyncKCDB = AsyncKCDB()  # pyright: ignore[reportUninitializedInstanceVariable]

    @pytest.mark.asyncio
    async def test_countries(self) -> None:
        """Test AsyncKCDB.countries()."""
        countries = await self.kcdb.countries()
        assert len(countries) > 100

        country, *rest = self.kcdb.filter(countries, "NZ")
        assert not rest
        assert country.id == 58
        assert country.label == "NZ"
        assert country.value == "New Zealand"

    @pytest.mark.asyncio
    async def test_domains(self) -> None:
        """Test AsyncKCDB.domains()."""
        chem, phys, rad = sorted(await self.kcdb.domains())
        assert chem.code == "CHEM-BIO"
        assert chem.name == "Chemistry and Biology"
        assert phys.code == "PHYSICS"
        assert phys.name == "General physics"
        assert rad.code == "RADIATION"
        assert rad.name == "Ionizing radiation"

    @pytest.mark.asyncio
    async def test_domain_response(self) -> None:
        """The the Response object for the 'referenceData/domain' request."""
        response = await self.kcdb.get(f"{AsyncKCDB.BASE_URL}/referenceData/domain")
        response.raise_for_status()
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "domains": [
                {"code": "CHEM-BIO", "name": "Chemistry and Biology"},
                {"code": "PHYSICS", "name": "General physics"},
                {"code": "RADIATION", "name": "Ionizing radiation"},
            ]
        }

    @pytest.mark.asyncio
    async def test_invalid_page_value(self) -> None:
        """Test page value invalid."""
        with pytest.raises(ValueError, match=r"Must be >= 0"):
            _ = await self.kcdb.quick_search(page=-1)

    @pytest.mark.asyncio
    async def test_invalid_page_size_value(self) -> None:
        """Test page_size value invalid."""
        with pytest.raises(ValueError, match=r"Invalid page size"):
            _ = await self.kcdb.quick_search(page_size=0)

    @pytest.mark.asyncio
    async def test_non_ionizing_quantities(self) -> None:
        """Test AsyncKCDB.non_ionizing_quantities()."""
        quantities = await self.kcdb.non_ionizing_quantities()
        assert len(quantities) > 1000

        quantity, *rest = self.kcdb.filter(quantities, "Sound pressure response")
        assert not rest
        assert quantity is not None
        assert quantity.id == 78
        assert quantity.value == "Sound pressure response level"

    @pytest.mark.asyncio
    async def test_quick_search(self) -> None:
        """Test AsyncKCDB.quick_search()."""
        quick = await self.kcdb.quick_search(
            keywords="phase OR test",
            included_filters=[
                "cmcDomain.CHEM-BIO",
                "cmcBranches.Dimensional metrology",
            ],
            excluded_filters=[
                "cmcServices.AC current",
                "cmcServices.AC power",
            ],
        )

        assert str(quick).startswith("ResultsQuickSearch(")
        assert quick.total_elements > 40

        found_cmc_domain = False
        found_chem_bio = False
        assert len(quick.filters_list) > 3
        for item in quick.filters_list:
            if item.code == "cmcDomain":
                found_cmc_domain = True
                assert (
                    str(item) == "ResultFilter(code='cmcDomain', count=0, name='cmcDomain', order=0, len(children)=3)"
                )
                for child in item.children:
                    if child.name == "CHEM-BIO":
                        found_chem_bio = True
                        assert child.code == "cmcDomain.CHEM-BIO"
                        assert child.name == "CHEM-BIO"
                        assert child.count > 50
                        assert child.order == -1
                        assert child.children == []
                        break
                break
        assert found_cmc_domain
        assert found_chem_bio

        found_cmc_rmo = False
        assert len(quick.aggregations) > 2
        for aggregation in quick.aggregations:
            if aggregation.name == "cmcRmo":
                found_cmc_rmo = True
                assert str(aggregation) == "ResultAggregation(name='cmcRmo', len(values)=3)"
                rmos = aggregation.values
                assert "EURAMET" in rmos
                assert "SIM" in rmos
                assert "APMP" in rmos
        assert found_cmc_rmo

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test timeout setter/getter and error message."""
        original = self.kcdb.timeout

        self.kcdb.timeout = 100
        assert isinstance(self.kcdb.timeout, float)
        assert self.kcdb.timeout == 100.0

        self.kcdb.timeout = None
        assert self.kcdb.timeout is None

        # make sure that get(url, timeout=None) is okay
        assert len(await self.kcdb.domains()) == 3

        self.kcdb.timeout = -1
        assert self.kcdb.timeout is None

        # Making the timeout value be very small causes a urllib.error.URLError
        # instead of a TimeoutError
        self.kcdb.timeout = 0.01  # type: ignore[unreachable]
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.01 seconds"):
            _ = await self.kcdb.quick_search()

        self.kcdb.timeout = original
