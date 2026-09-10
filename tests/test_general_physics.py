import asyncio
from datetime import date

import pytest

from msl.kcdb import AsyncChemistryBiology, AsyncPhysics, AsyncRadiation, ChemistryBiology, Physics, Radiation, Status
from msl.kcdb.types import Country, MetrologyArea


class TestPhysics:
    """Test the Physics class."""

    def setup_class(self) -> None:
        """Create Physics instance."""
        self.physics: Physics = Physics()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.metrology_areas: list[MetrologyArea] = self.physics.metrology_areas()  # pyright: ignore[reportUninitializedInstanceVariable]

    def test_branches(self) -> None:
        """Test Physics.branches()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.branches(areas[0])
        assert len(branches) == 3

        t, *rest = self.physics.filter(branches, "interval")
        assert not rest
        assert t.id == 28
        assert t.label == "TF/TI"
        assert t.value == "Time interval"
        assert t.metrology_area.id == 7
        assert t.metrology_area.label == "TF"
        assert t.metrology_area.value == "Time and Frequency"

    def test_branches_chem_bio(self) -> None:
        """Test Physics.branches() for Chemistry and Biology areas."""
        chem_bio = ChemistryBiology()
        for area in chem_bio.metrology_areas():
            branches = self.physics.branches(area)
            assert not branches

    def test_branches_radiation(self) -> None:
        """Test Physics.branches() for Ionizing Radiation areas."""
        rad = Radiation()
        for area in rad.metrology_areas():
            branches = self.physics.branches(area)
            assert not branches

    def test_domain(self) -> None:
        """Test Physics.DOMAIN class attribute."""
        _, phys, _ = sorted(self.physics.domains())
        assert phys == self.physics.DOMAIN
        assert phys.code == "PHYSICS"
        assert phys.name == "General physics"

    def test_individual_services(self) -> None:
        """Test Physics.individual_services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = self.physics.filter(self.physics.services(branches[0]), "Frequency")
        assert len(services) == 1
        sub_services = self.physics.filter(self.physics.sub_services(services[0]), "Frequency meter")
        assert len(sub_services) == 1
        individual_services = self.physics.individual_services(sub_services[0])
        assert len(individual_services) == 2

        counter, *rest = self.physics.filter(individual_services, "counter")
        assert not rest
        assert counter.id == 546
        assert counter.label == "1"
        assert counter.value == "Frequency counter"
        assert counter.physics_code == "2.3.1"
        assert counter.sub_service.id == 218
        assert counter.sub_service.physics_code == "2.3"
        assert counter.sub_service.service.id == 55
        assert counter.sub_service.service.physics_code == "2"
        assert counter.sub_service.service.branch.id == 27
        assert counter.sub_service.service.branch.metrology_area.id == 7

    def test_individual_services_no_http_404_error(self) -> None:
        """Test Physics.individual_services() for HTTP 404 error."""
        areas = self.physics.filter(self.metrology_areas, "L")
        assert len(areas) == 1
        branches = self.physics.filter(self.physics.branches(areas[0]), r"L/DimMet")
        assert len(branches) == 1
        services = self.physics.filter(self.physics.services(branches[0]), "Various dimensional")
        assert len(services) == 1
        sub_services = self.physics.filter(self.physics.sub_services(services[0]), "7")
        assert len(sub_services) == 1

        individual_services = self.physics.individual_services(sub_services[0])
        assert not individual_services

    def test_metrology_area(self) -> None:
        """Test Physics.metrology_areas()."""
        assert len(self.metrology_areas) == 7
        therm, *rest = self.physics.filter(self.metrology_areas, "Thermometry")
        assert not rest
        assert therm.id == 6
        assert therm.label == "T"
        assert therm.value == "Thermometry"
        assert therm.domain.code == "PHYSICS"
        assert therm.domain.name == "General physics"

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.physics) == "Physics(code='PHYSICS', name='General physics')"

    def test_search(self) -> None:  # noqa: PLR0915
        """Test Physics.search()."""
        physics = self.physics.search(
            "PR",
            branch="PR/Photo",
            keywords="Illuminance AND meter",
            countries=["CH", Country(id=29, label="FR", value="France"), "JP", "NZ"],
            public_date_from=date(2002, 1, 31),
            public_date_to="2020-06-30",
            show_table=True,
            status=Status.PUBLISHED,
            physics_code="1.2.1",
            service="1",
            sub_service="2",
            individual_service="1",
        )

        assert str(physics) == (
            "ResultsPhysics(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert physics.version_api_kcdb == "1.0.13"
        assert physics.page_number == 0
        assert physics.page_size == 100
        assert physics.number_of_elements == 1
        assert physics.total_elements == 1
        assert physics.total_pages == 1
        assert len(physics.data) == 1
        data = physics.data[0]
        assert str(data) == "ResultPhysics(id=7852, nmi_code='MSL', rmo='APMP')"
        assert data.id == 7852
        assert data.status == "Published"
        assert data.status_date == "2012-11-29"
        assert data.kcdb_code == "APMP-PR-NZ-00000624-1"
        assert data.domain_code == "PHYSICS"
        assert data.metrology_area_label == "PR"
        assert data.rmo == "APMP"
        assert data.country_value == "New Zealand"
        assert data.nmi_code == "MSL"
        assert data.nmi_identifier == 117
        assert data.nmi_name == "Measurement Standards Laboratory"
        assert data.nmi_ror_identifier == "04022gq47"
        assert data.nmi_service_code == "MSLT.O.001, MSLT.O.016"  # cSpell: disable-line
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q111449920"
        assert data.quantity_value == "Illuminance responsivity, tungsten source"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=None, unit='A/lx, V/lx, reading/lx', upper_limit=None)"
        assert data.cmc.lower_limit is None
        assert data.cmc.upper_limit is None
        assert data.cmc.unit == "A/lx, V/lx, reading/lx"
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=3.0, unit='%', upper_limit=3.0)"
        assert data.cmc_uncertainty.lower_limit == 3.0
        assert data.cmc_uncertainty.upper_limit == 3.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_base_unit is not None
        assert str(data.cmc_base_unit) == "ResultUnit(lower_limit=None, unit='X/lx', upper_limit=None)"
        assert data.cmc_base_unit.lower_limit is None
        assert data.cmc_base_unit.unit == "X/lx"
        assert data.cmc_base_unit.upper_limit is None
        assert data.cmc_uncertainty_base_unit is not None
        assert str(data.cmc_uncertainty_base_unit) == "ResultUnit(lower_limit=None, unit='X/lx', upper_limit=None)"
        assert data.cmc_uncertainty_base_unit.lower_limit is None
        assert data.cmc_uncertainty_base_unit.unit == "X/lx"
        assert data.cmc_uncertainty_base_unit.upper_limit is None
        assert data.confidence_level == 95
        assert data.coverage_factor == 2.3
        assert data.uncertainty_equation is not None
        assert str(data.uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.uncertainty_equation.equation == ""
        assert data.uncertainty_equation.equation_comment == ""
        assert data.uncertainty_table is not None
        assert str(data.uncertainty_table) == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        assert data.uncertainty_mode is not None
        assert data.uncertainty_mode.name == "RELATIVE"
        assert data.uncertainty_mode.value == "Relative"
        assert data.traceability_source == ""
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2012-11-29"
        assert data.approval_date == "2012-11-29"
        assert data.international_standard == ""
        assert data.branch_value == "Photometry"
        assert data.branch_label == "PR/Photo"
        assert data.service_value == "Photometry"
        assert data.sub_service_value == "Illuminance responsivity"
        assert data.individual_service_value == "Tungsten source"
        assert data.physics_code == "1.2.1"
        assert data.kcdb_service_category == "PR/Photo-1.2.1"
        assert data.instrument == "Illuminance meter"
        assert data.instrument_method == "Standard lamp"
        assert len(data.parameters) == 2
        assert str(data.parameters[0]) == (
            "ResultParam(parameter_name='Illuminance', parameter_value='0.005 lx to 10 lx')"
        )
        assert data.parameters[1].parameter_name == "Correlated colour temperature"
        assert data.parameters[1].parameter_value == "2700 K to 3000 K"

    def test_services(self) -> None:
        """Test Physics.services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = self.physics.services(branches[0])
        assert len(services) == 1

        service = services[0]
        assert service.id == 55
        assert service.label == "2"
        assert service.value == "Frequency"
        assert service.physics_code == "2"
        assert service.branch.id == 27
        assert service.branch.metrology_area.id == 7

    def test_services_radiation_branches(self) -> None:
        """Test Physics.services() for Ionizing Radiation branches."""
        radiation = Radiation()
        for area in radiation.metrology_areas():
            for branch in radiation.branches(area):
                assert not self.physics.services(branch)

    def test_sub_services(self) -> None:
        """Test Physics.sub_services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = self.physics.filter(self.physics.services(branches[0]), "Frequency")
        assert len(services) == 1
        sub_services = self.physics.sub_services(services[0])
        assert len(sub_services) == 3

        meter, *rest = self.physics.filter(sub_services, "meter")
        assert not rest
        assert meter.id == 218
        assert meter.label == "3"
        assert meter.value == "Frequency meter"
        assert meter.physics_code == "2.3"
        assert meter.service.id == 55
        assert meter.service.physics_code == "2"
        assert meter.service.branch.id == 27
        assert meter.service.branch.metrology_area.id == 7

    def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.physics.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.physics.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = self.physics.search("M")

        self.physics.timeout = original


class TestAsyncPhysics:
    """Test the AsyncPhysics class."""

    def setup_class(self) -> None:
        """Create AsyncPhysics instance."""
        self.physics: AsyncPhysics = AsyncPhysics()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.metrology_areas: list[MetrologyArea] = asyncio.run(self.physics.metrology_areas())  # pyright: ignore[reportUninitializedInstanceVariable]

    @pytest.mark.asyncio
    async def test_branches(self) -> None:
        """Test AsyncPhysics.branches()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = await self.physics.branches(areas[0])
        assert len(branches) == 3

        t, *rest = self.physics.filter(branches, "interval")
        assert not rest
        assert t.id == 28
        assert t.label == "TF/TI"
        assert t.value == "Time interval"
        assert t.metrology_area.id == 7
        assert t.metrology_area.label == "TF"
        assert t.metrology_area.value == "Time and Frequency"

    @pytest.mark.asyncio
    async def test_branches_chem_bio(self) -> None:
        """Test AsyncPhysics.branches() for Chemistry and Biology areas."""
        chem_bio = AsyncChemistryBiology()
        for area in await chem_bio.metrology_areas():
            branches = await self.physics.branches(area)
            assert not branches

    @pytest.mark.asyncio
    async def test_branches_radiation(self) -> None:
        """Test AsyncPhysics.branches() for Ionizing Radiation areas."""
        rad = AsyncRadiation()
        for area in await rad.metrology_areas():
            branches = await self.physics.branches(area)
            assert not branches

    @pytest.mark.asyncio
    async def test_domain(self) -> None:
        """Test AsyncPhysics.DOMAIN class attribute."""
        _, phys, _ = sorted(await self.physics.domains())
        assert phys == self.physics.DOMAIN
        assert phys.code == "PHYSICS"
        assert phys.name == "General physics"

    @pytest.mark.asyncio
    async def test_individual_services(self) -> None:
        """Test AsyncPhysics.individual_services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(await self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = self.physics.filter(await self.physics.services(branches[0]), "Frequency")
        assert len(services) == 1
        sub_services = self.physics.filter(await self.physics.sub_services(services[0]), "Frequency meter")
        assert len(sub_services) == 1
        individual_services = await self.physics.individual_services(sub_services[0])
        assert len(individual_services) == 2

        counter, *rest = self.physics.filter(individual_services, "counter")
        assert not rest
        assert counter.id == 546
        assert counter.label == "1"
        assert counter.value == "Frequency counter"
        assert counter.physics_code == "2.3.1"
        assert counter.sub_service.id == 218
        assert counter.sub_service.physics_code == "2.3"
        assert counter.sub_service.service.id == 55
        assert counter.sub_service.service.physics_code == "2"
        assert counter.sub_service.service.branch.id == 27
        assert counter.sub_service.service.branch.metrology_area.id == 7

    @pytest.mark.asyncio
    async def test_individual_services_no_http_404_error(self) -> None:
        """Test AsyncPhysics.individual_services() for HTTP 404 error."""
        areas = self.physics.filter(self.metrology_areas, "L")
        assert len(areas) == 1
        branches = self.physics.filter(await self.physics.branches(areas[0]), r"L/DimMet")
        assert len(branches) == 1
        services = self.physics.filter(await self.physics.services(branches[0]), "Various dimensional")
        assert len(services) == 1
        sub_services = self.physics.filter(await self.physics.sub_services(services[0]), "7")
        assert len(sub_services) == 1

        individual_services = await self.physics.individual_services(sub_services[0])
        assert not individual_services

    def test_metrology_area(self) -> None:
        """Test AsyncPhysics.metrology_areas()."""
        assert len(self.metrology_areas) == 7
        therm, *rest = self.physics.filter(self.metrology_areas, "Thermometry")
        assert not rest
        assert therm.id == 6
        assert therm.label == "T"
        assert therm.value == "Thermometry"
        assert therm.domain.code == "PHYSICS"
        assert therm.domain.name == "General physics"

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.physics) == "AsyncPhysics(code='PHYSICS', name='General physics')"

    @pytest.mark.asyncio
    async def test_search(self) -> None:  # noqa: PLR0915
        """Test AsyncPhysics.search()."""
        physics = await self.physics.search(
            "PR",
            branch="PR/Photo",
            keywords="Illuminance AND meter",
            countries=["CH", Country(id=29, label="FR", value="France"), "JP", "NZ"],
            public_date_from=date(2002, 1, 31),
            public_date_to="2020-06-30",
            show_table=True,
            status=Status.PUBLISHED,
            physics_code="1.2.1",
            service="1",
            sub_service="2",
            individual_service="1",
        )

        assert str(physics) == (
            "ResultsPhysics(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert physics.version_api_kcdb == "1.0.13"
        assert physics.page_number == 0
        assert physics.page_size == 100
        assert physics.number_of_elements == 1
        assert physics.total_elements == 1
        assert physics.total_pages == 1
        assert len(physics.data) == 1
        data = physics.data[0]
        assert str(data) == "ResultPhysics(id=7852, nmi_code='MSL', rmo='APMP')"
        assert data.id == 7852
        assert data.status == "Published"
        assert data.status_date == "2012-11-29"
        assert data.kcdb_code == "APMP-PR-NZ-00000624-1"
        assert data.domain_code == "PHYSICS"
        assert data.metrology_area_label == "PR"
        assert data.rmo == "APMP"
        assert data.country_value == "New Zealand"
        assert data.nmi_code == "MSL"
        assert data.nmi_identifier == 117
        assert data.nmi_name == "Measurement Standards Laboratory"
        assert data.nmi_ror_identifier == "04022gq47"
        assert data.nmi_service_code == "MSLT.O.001, MSLT.O.016"  # cSpell: disable-line
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q111449920"
        assert data.quantity_value == "Illuminance responsivity, tungsten source"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=None, unit='A/lx, V/lx, reading/lx', upper_limit=None)"
        assert data.cmc.lower_limit is None
        assert data.cmc.upper_limit is None
        assert data.cmc.unit == "A/lx, V/lx, reading/lx"
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=3.0, unit='%', upper_limit=3.0)"
        assert data.cmc_uncertainty.lower_limit == 3.0
        assert data.cmc_uncertainty.upper_limit == 3.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_base_unit is not None
        assert str(data.cmc_base_unit) == "ResultUnit(lower_limit=None, unit='X/lx', upper_limit=None)"
        assert data.cmc_base_unit.lower_limit is None
        assert data.cmc_base_unit.unit == "X/lx"
        assert data.cmc_base_unit.upper_limit is None
        assert data.cmc_uncertainty_base_unit is not None
        assert str(data.cmc_uncertainty_base_unit) == "ResultUnit(lower_limit=None, unit='X/lx', upper_limit=None)"
        assert data.cmc_uncertainty_base_unit.lower_limit is None
        assert data.cmc_uncertainty_base_unit.unit == "X/lx"
        assert data.cmc_uncertainty_base_unit.upper_limit is None
        assert data.confidence_level == 95
        assert data.coverage_factor == 2.3
        assert data.uncertainty_equation is not None
        assert str(data.uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.uncertainty_equation.equation == ""
        assert data.uncertainty_equation.equation_comment == ""
        assert data.uncertainty_table is not None
        assert str(data.uncertainty_table) == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        assert data.uncertainty_mode is not None
        assert data.uncertainty_mode.name == "RELATIVE"
        assert data.uncertainty_mode.value == "Relative"
        assert data.traceability_source == ""
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2012-11-29"
        assert data.approval_date == "2012-11-29"
        assert data.international_standard == ""
        assert data.branch_value == "Photometry"
        assert data.branch_label == "PR/Photo"
        assert data.service_value == "Photometry"
        assert data.sub_service_value == "Illuminance responsivity"
        assert data.individual_service_value == "Tungsten source"
        assert data.physics_code == "1.2.1"
        assert data.kcdb_service_category == "PR/Photo-1.2.1"
        assert data.instrument == "Illuminance meter"
        assert data.instrument_method == "Standard lamp"
        assert len(data.parameters) == 2
        assert str(data.parameters[0]) == (
            "ResultParam(parameter_name='Illuminance', parameter_value='0.005 lx to 10 lx')"
        )
        assert data.parameters[1].parameter_name == "Correlated colour temperature"
        assert data.parameters[1].parameter_value == "2700 K to 3000 K"

    @pytest.mark.asyncio
    async def test_services(self) -> None:
        """Test AsyncPhysics.services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(await self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = await self.physics.services(branches[0])
        assert len(services) == 1

        service = services[0]
        assert service.id == 55
        assert service.label == "2"
        assert service.value == "Frequency"
        assert service.physics_code == "2"
        assert service.branch.id == 27
        assert service.branch.metrology_area.id == 7

    @pytest.mark.asyncio
    async def test_services_radiation_branches(self) -> None:
        """Test AsyncPhysics.services() for Ionizing Radiation branches."""
        radiation = AsyncRadiation()
        for area in await radiation.metrology_areas():
            for branch in await radiation.branches(area):
                assert not await self.physics.services(branch)

    @pytest.mark.asyncio
    async def test_sub_services(self) -> None:
        """Test AsyncPhysics.sub_services()."""
        areas = self.physics.filter(self.metrology_areas, "TF")
        assert len(areas) == 1
        branches = self.physics.filter(await self.physics.branches(areas[0]), r"TF/F")
        assert len(branches) == 1
        services = self.physics.filter(await self.physics.services(branches[0]), "Frequency")
        assert len(services) == 1
        sub_services = await self.physics.sub_services(services[0])
        assert len(sub_services) == 3

        meter, *rest = self.physics.filter(sub_services, "meter")
        assert not rest
        assert meter.id == 218
        assert meter.label == "3"
        assert meter.value == "Frequency meter"
        assert meter.physics_code == "2.3"
        assert meter.service.id == 55
        assert meter.service.physics_code == "2"
        assert meter.service.branch.id == 27
        assert meter.service.branch.metrology_area.id == 7

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.physics.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.physics.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = await self.physics.search("M")

        self.physics.timeout = original
