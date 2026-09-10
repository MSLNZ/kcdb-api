import asyncio
from datetime import date

import pytest

from msl.kcdb import AsyncChemistryBiology, AsyncPhysics, AsyncRadiation, ChemistryBiology, Physics, Radiation, Status
from msl.kcdb.types import Branch, Country, MetrologyArea


class TestRadiation:
    """Test the Radiation class."""

    def setup_class(self) -> None:
        """Create Radiation instance."""
        self.radiation: Radiation = Radiation()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.metrology_areas: list[MetrologyArea] = self.radiation.metrology_areas()  # pyright: ignore[reportUninitializedInstanceVariable]
        assert len(self.metrology_areas) == 1
        self.branches: list[Branch] = self.radiation.branches(self.metrology_areas[0])  # pyright: ignore[reportUninitializedInstanceVariable]

        p: Physics = Physics()
        self.physics_branches: list[Branch] = [b for a in p.metrology_areas() for b in p.branches(a)]  # pyright: ignore[reportUninitializedInstanceVariable]
        assert len(self.physics_branches) == 32

    def test_branches(self) -> None:
        """Test Radiation.branches()."""
        assert len(self.branches) == 3

        neu, *rest = self.radiation.filter(self.branches, "NEU")
        assert not rest
        assert neu.id == 34
        assert neu.label == "NEU"
        assert neu.value == "Neutron Measurements"
        assert neu.metrology_area.id == 9
        assert neu.metrology_area.label == "RI"
        assert neu.metrology_area.value == "Ionizing Radiation"

    def test_branches_chem_bio_areas(self) -> None:
        """Test Radiation.branches() for Chemistry and Biology areas."""
        chem_bio = ChemistryBiology()
        for area in chem_bio.metrology_areas():
            branches = self.radiation.branches(area)
            assert not branches

    def test_branches_physics_areas(self) -> None:
        """Test Radiation.branches() for General Physics areas."""
        physics = Physics()
        for area in physics.metrology_areas():
            branches = self.radiation.branches(area)
            assert not branches

    def test_domain(self) -> None:
        """Test Radiation.DOMAIN class attribute."""
        _, _, rad = sorted(self.radiation.domains())
        assert rad == self.radiation.DOMAIN
        assert rad.code == "RADIATION"
        assert rad.name == "Ionizing radiation"

    def test_mediums_dosimetry(self) -> None:
        """Test Radiation.mediums() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        mediums = self.radiation.mediums(branches[0])
        assert len(mediums) == 7

        medium, *rest = self.radiation.filter(mediums, "Graphite")
        assert not rest
        assert medium.id == 21
        assert medium.label == "4"
        assert medium.value == "Graphite"

    def test_mediums_neutron(self) -> None:
        """Test Radiation.mediums() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        mediums = self.radiation.mediums(branches[0])
        assert len(mediums) == 4

        medium, *rest = self.radiation.filter(mediums, "Tissue")
        assert not rest
        assert medium.id == 26
        assert medium.label == "3"
        assert medium.value == "Tissue"

    def test_mediums_radioactivity(self) -> None:
        """Test Radiation.mediums() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        mediums = self.radiation.mediums(branches[0])
        assert len(mediums) == 14

        medium, *rest = self.radiation.filter(mediums, "Aerosol")
        assert not rest
        assert medium.id == 5
        assert medium.label == "5"
        assert medium.value == "Aerosol"

    def test_mediums_physics_branches(self) -> None:
        """Test Radiation.mediums() for General Physics branches."""
        for branch in self.physics_branches:
            mediums = self.radiation.mediums(branch)
            assert not mediums

    def test_metrology_area(self) -> None:
        """Test Radiation.metrology_areas()."""
        assert len(self.metrology_areas) == 1
        radiation = self.metrology_areas[0]
        assert radiation.id == 9
        assert radiation.label == "RI"
        assert radiation.value == "Ionizing Radiation"
        assert radiation.domain.code == "RADIATION"
        assert radiation.domain.name == "Ionizing radiation"

    def test_nuclides(self) -> None:
        """Test Radiation.nuclides()."""
        nuclides = self.radiation.nuclides()
        assert len(nuclides) > 100

        nuclide, *rest = self.radiation.filter(nuclides, "^Ce-144$")
        assert not rest
        assert nuclide.id == 3
        assert nuclide.label == "Ce-144"
        assert nuclide.value == "Ce-144"

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.radiation) == "Radiation(code='RADIATION', name='Ionizing radiation')"

    def test_search(self) -> None:  # noqa: PLR0915
        """Test Radiation.search()."""
        radiation = self.radiation.search(
            branch="RAD",
            quantity="1",
            medium="3",
            source="2",
            nuclide="Co-60",
            keywords="phase OR multichannel OR water",
            countries=Country(id=1, label="JP", value="Japan"),
            public_date_from=date(2005, 1, 31),
            public_date_to="2024-06-30",
            status=Status.PUBLISHED,
        )

        assert str(radiation) == (
            "ResultsRadiation(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert radiation.version_api_kcdb == "1.0.13"
        assert radiation.page_number == 0
        assert radiation.page_size == 100
        assert radiation.number_of_elements == 1
        assert radiation.total_elements == 1
        assert radiation.total_pages == 1
        assert len(radiation.data) == 1
        data = radiation.data[0]
        assert str(data) == "ResultRadiation(id=23054, nmi_code='NMIJ AIST', rmo='APMP')"
        assert data.id == 23054
        assert data.status == "Published"
        assert data.status_date == "2005-02-14"
        assert data.kcdb_code == "APMP-RI-JP-00000HSE-1"
        assert data.domain_code == "RADIATION"
        assert data.metrology_area_label == "RI"
        assert data.rmo == "APMP"
        assert data.country_value == "Japan"
        assert data.nmi_code == "NMIJ AIST"
        assert data.nmi_identifier == 129
        assert data.nmi_name == "National Metrology Institute of Japan"
        assert data.nmi_ror_identifier == "01703db54"
        assert data.nmi_service_code == "APM-RAD-NMIJ/AIST-2144"
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q1076542"
        assert data.quantity_value == "Activity"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=2000.0, unit='Bq', upper_limit=200000.0)"
        assert data.cmc.lower_limit == 2000.0
        assert data.cmc.unit == "Bq"
        assert data.cmc.upper_limit == 200000.0
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=4.0, unit='%', upper_limit=4.0)"
        assert data.cmc_uncertainty.lower_limit == 4.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_uncertainty.upper_limit == 4.0
        assert data.cmc_base_unit is not None
        assert str(data.cmc_base_unit) == "ResultUnit(lower_limit=2000.0, unit='Bq', upper_limit=200000.0)"
        assert data.cmc_base_unit.lower_limit == 2000.0
        assert data.cmc_base_unit.unit == "Bq"
        assert data.cmc_base_unit.upper_limit == 200000.0
        assert data.cmc_uncertainty_base_unit is not None
        assert str(data.cmc_uncertainty_base_unit) == "ResultUnit(lower_limit=80.0, unit='Bq', upper_limit=8000.0)"
        assert data.cmc_uncertainty_base_unit.lower_limit == 80.0
        assert data.cmc_uncertainty_base_unit.unit == "Bq"
        assert data.cmc_uncertainty_base_unit.upper_limit == 8000.0
        assert data.confidence_level == 95
        assert data.coverage_factor == 2
        assert data.uncertainty_equation is not None
        assert str(data.uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.uncertainty_equation.equation == ""
        assert data.uncertainty_equation.equation_comment == ""
        assert data.uncertainty_table is not None
        assert str(data.uncertainty_table) == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        assert data.uncertainty_table.table_name == ""
        assert data.uncertainty_table.table_rows == 0
        assert data.uncertainty_table.table_cols == 0
        assert data.uncertainty_table.table_comment == ""
        assert data.uncertainty_table.table_contents == "<masked>"
        assert data.uncertainty_mode is not None
        assert data.uncertainty_mode.name == "RELATIVE"
        assert data.uncertainty_mode.value == "Relative"
        assert data.traceability_source == "NMIJ/AIST"
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2005-02-14"
        assert data.approval_date == "2005-02-14"
        assert data.branch_label == "RAD"
        assert data.branch_value == "Radioactivity"
        assert data.kcdb_service_category == "RI/RAD-1.3.2"
        assert data.instrument == "Multiple nuclide source, solution"
        assert data.instrument_method == "Ge detector, multichannel analyzer"
        assert data.source_value == "Multi-radionuclide source"
        assert data.medium_value == "Liquid"
        assert data.nuclide_value == "Co-60"
        assert data.radiation_specification == "10 ml to 500 ml NMIJ/AIST standard cylindrical plastic bottle"
        assert data.international_standard == ""
        assert data.reference_standard == "Comparison with the NMIJ/AIST standard source"
        assert data.radiation_code == "2.1.3.2"

    def test_sources_dosimetry(self) -> None:
        """Test Radiation.sources() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        sources = self.radiation.sources(branches[0])
        assert len(sources) == 17

        source, *rest = self.radiation.filter(sources, "Photons")
        assert not rest
        assert source.id == 6
        assert source.label == "6"
        assert source.value == "Photons, high energy"

    def test_sources_neutron(self) -> None:
        """Test Radiation.sources() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        sources = self.radiation.sources(branches[0])
        assert len(sources) > 10

        source, *rest = self.radiation.filter(sources, "Mono")
        assert not rest
        assert source.id == 36
        assert source.label == "2"
        assert source.value == "Mono-energetic neutrons"

    def test_sources_radioactivity(self) -> None:
        """Test Radiation.sources() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        sources = self.radiation.sources(branches[0])
        assert len(sources) == 3

        source, *rest = self.radiation.filter(sources, "x-rays")
        assert not rest
        assert source.id == 34
        assert source.label == "3"
        assert source.value == "K x-rays"

    def test_sources_physics_branches(self) -> None:
        """Test Radiation.sources() for General Physics branches."""
        for branch in self.physics_branches:
            sources = self.radiation.sources(branch)
            assert not sources

    def test_quantities_dosimetry(self) -> None:
        """Test Radiation.quantities() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        quantities = self.radiation.quantities(branches[0])
        assert len(quantities) == 16

        quantity, *rest = self.radiation.filter(quantities, "X-ray")
        assert not rest
        assert quantity.id == 14
        assert quantity.label == "14"
        assert quantity.value == "X-ray tube voltage"

    def test_quantities_neutron(self) -> None:
        """Test Radiation.quantities() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        quantities = self.radiation.quantities(branches[0])
        assert len(quantities) == 17

        quantity, *rest = self.radiation.filter(quantities, "^Fluence$")
        assert not rest
        assert quantity.id == 49
        assert quantity.label == "3"
        assert quantity.value == "Fluence"

    def test_quantities_radioactivity(self) -> None:
        """Test Radiation.quantities() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        quantities = self.radiation.quantities(branches[0])
        assert len(quantities) == 12

        quantity, *rest = self.radiation.filter(quantities, "Activity per unit area")
        assert not rest
        assert quantity.id == 34
        assert quantity.label == "3"
        assert quantity.value == "Activity per unit area"

    def test_quantities_physics_branches(self) -> None:
        """Test Radiation.quantities() for General Physics branches."""
        for branch in self.physics_branches:
            quantities = self.radiation.quantities(branch)
            assert not quantities

    def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.radiation.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.radiation.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = self.radiation.search()

        self.radiation.timeout = original


class TestAsyncRadiation:
    """Test the AsyncRadiation class."""

    def setup_class(self) -> None:
        """Create AsyncRadiation instance."""
        self.radiation: AsyncRadiation = AsyncRadiation()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.metrology_areas: list[MetrologyArea] = asyncio.run(self.radiation.metrology_areas())  # pyright: ignore[reportUninitializedInstanceVariable]
        assert len(self.metrology_areas) == 1
        self.branches: list[Branch] = asyncio.run(self.radiation.branches(self.metrology_areas[0]))  # pyright: ignore[reportUninitializedInstanceVariable]

        p: AsyncPhysics = AsyncPhysics()
        self.physics_branches: list[Branch] = [  # pyright: ignore[reportUninitializedInstanceVariable]
            b for a in asyncio.run(p.metrology_areas()) for b in asyncio.run(p.branches(a))
        ]
        assert len(self.physics_branches) == 32

    def test_branches(self) -> None:
        """Test AsyncRadiation.branches()."""
        assert len(self.branches) == 3

        neu, *rest = self.radiation.filter(self.branches, "NEU")
        assert not rest
        assert neu.id == 34
        assert neu.label == "NEU"
        assert neu.value == "Neutron Measurements"
        assert neu.metrology_area.id == 9
        assert neu.metrology_area.label == "RI"
        assert neu.metrology_area.value == "Ionizing Radiation"

    @pytest.mark.asyncio
    async def test_branches_chem_bio_areas(self) -> None:
        """Test AsyncRadiation.branches() for Chemistry and Biology areas."""
        chem_bio = AsyncChemistryBiology()
        for area in await chem_bio.metrology_areas():
            branches = await self.radiation.branches(area)
            assert not branches

    @pytest.mark.asyncio
    async def test_branches_physics_areas(self) -> None:
        """Test AsyncRadiation.branches() for General Physics areas."""
        physics = AsyncPhysics()
        for area in await physics.metrology_areas():
            branches = await self.radiation.branches(area)
            assert not branches

    @pytest.mark.asyncio
    async def test_domain(self) -> None:
        """Test AsyncRadiation.DOMAIN class attribute."""
        _, _, rad = sorted(await self.radiation.domains())
        assert rad == self.radiation.DOMAIN
        assert rad.code == "RADIATION"
        assert rad.name == "Ionizing radiation"

    @pytest.mark.asyncio
    async def test_mediums_dosimetry(self) -> None:
        """Test AsyncRadiation.mediums() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        mediums = await self.radiation.mediums(branches[0])
        assert len(mediums) == 7

        medium, *rest = self.radiation.filter(mediums, "Graphite")
        assert not rest
        assert medium.id == 21
        assert medium.label == "4"
        assert medium.value == "Graphite"

    @pytest.mark.asyncio
    async def test_mediums_neutron(self) -> None:
        """Test AsyncRadiation.mediums() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        mediums = await self.radiation.mediums(branches[0])
        assert len(mediums) == 4

        medium, *rest = self.radiation.filter(mediums, "Tissue")
        assert not rest
        assert medium.id == 26
        assert medium.label == "3"
        assert medium.value == "Tissue"

    @pytest.mark.asyncio
    async def test_mediums_radioactivity(self) -> None:
        """Test AsyncRadiation.mediums() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        mediums = await self.radiation.mediums(branches[0])
        assert len(mediums) == 14

        medium, *rest = self.radiation.filter(mediums, "Aerosol")
        assert not rest
        assert medium.id == 5
        assert medium.label == "5"
        assert medium.value == "Aerosol"

    @pytest.mark.asyncio
    async def test_mediums_physics_branches(self) -> None:
        """Test AsyncRadiation.mediums() for General Physics branches."""
        for branch in self.physics_branches:
            mediums = await self.radiation.mediums(branch)
            assert not mediums

    def test_metrology_area(self) -> None:
        """Test AsyncRadiation.metrology_areas()."""
        assert len(self.metrology_areas) == 1
        radiation = self.metrology_areas[0]
        assert radiation.id == 9
        assert radiation.label == "RI"
        assert radiation.value == "Ionizing Radiation"
        assert radiation.domain.code == "RADIATION"
        assert radiation.domain.name == "Ionizing radiation"

    @pytest.mark.asyncio
    async def test_nuclides(self) -> None:
        """Test AsyncRadiation.nuclides()."""
        nuclides = await self.radiation.nuclides()
        assert len(nuclides) > 100

        nuclide, *rest = self.radiation.filter(nuclides, "^Ce-144$")
        assert not rest
        assert nuclide.id == 3
        assert nuclide.label == "Ce-144"
        assert nuclide.value == "Ce-144"

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.radiation) == "AsyncRadiation(code='RADIATION', name='Ionizing radiation')"

    @pytest.mark.asyncio
    async def test_search(self) -> None:  # noqa: PLR0915
        """Test AsyncRadiation.search()."""
        radiation = await self.radiation.search(
            branch="RAD",
            quantity="1",
            medium="3",
            source="2",
            nuclide="Co-60",
            keywords="phase OR multichannel OR water",
            countries=Country(id=1, label="JP", value="Japan"),
            public_date_from=date(2005, 1, 31),
            public_date_to="2024-06-30",
            status=Status.PUBLISHED,
        )

        assert str(radiation) == (
            "ResultsRadiation(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert radiation.version_api_kcdb == "1.0.13"
        assert radiation.page_number == 0
        assert radiation.page_size == 100
        assert radiation.number_of_elements == 1
        assert radiation.total_elements == 1
        assert radiation.total_pages == 1
        assert len(radiation.data) == 1
        data = radiation.data[0]
        assert str(data) == "ResultRadiation(id=23054, nmi_code='NMIJ AIST', rmo='APMP')"
        assert data.id == 23054
        assert data.status == "Published"
        assert data.status_date == "2005-02-14"
        assert data.kcdb_code == "APMP-RI-JP-00000HSE-1"
        assert data.domain_code == "RADIATION"
        assert data.metrology_area_label == "RI"
        assert data.rmo == "APMP"
        assert data.country_value == "Japan"
        assert data.nmi_code == "NMIJ AIST"
        assert data.nmi_identifier == 129
        assert data.nmi_name == "National Metrology Institute of Japan"
        assert data.nmi_ror_identifier == "01703db54"
        assert data.nmi_service_code == "APM-RAD-NMIJ/AIST-2144"
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q1076542"
        assert data.quantity_value == "Activity"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=2000.0, unit='Bq', upper_limit=200000.0)"
        assert data.cmc.lower_limit == 2000.0
        assert data.cmc.unit == "Bq"
        assert data.cmc.upper_limit == 200000.0
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=4.0, unit='%', upper_limit=4.0)"
        assert data.cmc_uncertainty.lower_limit == 4.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_uncertainty.upper_limit == 4.0
        assert data.cmc_base_unit is not None
        assert str(data.cmc_base_unit) == "ResultUnit(lower_limit=2000.0, unit='Bq', upper_limit=200000.0)"
        assert data.cmc_base_unit.lower_limit == 2000.0
        assert data.cmc_base_unit.unit == "Bq"
        assert data.cmc_base_unit.upper_limit == 200000.0
        assert data.cmc_uncertainty_base_unit is not None
        assert str(data.cmc_uncertainty_base_unit) == "ResultUnit(lower_limit=80.0, unit='Bq', upper_limit=8000.0)"
        assert data.cmc_uncertainty_base_unit.lower_limit == 80.0
        assert data.cmc_uncertainty_base_unit.unit == "Bq"
        assert data.cmc_uncertainty_base_unit.upper_limit == 8000.0
        assert data.confidence_level == 95
        assert data.coverage_factor == 2
        assert data.uncertainty_equation is not None
        assert str(data.uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.uncertainty_equation.equation == ""
        assert data.uncertainty_equation.equation_comment == ""
        assert data.uncertainty_table is not None
        assert str(data.uncertainty_table) == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        assert data.uncertainty_table.table_name == ""
        assert data.uncertainty_table.table_rows == 0
        assert data.uncertainty_table.table_cols == 0
        assert data.uncertainty_table.table_comment == ""
        assert data.uncertainty_table.table_contents == "<masked>"
        assert data.uncertainty_mode is not None
        assert data.uncertainty_mode.name == "RELATIVE"
        assert data.uncertainty_mode.value == "Relative"
        assert data.traceability_source == "NMIJ/AIST"
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2005-02-14"
        assert data.approval_date == "2005-02-14"
        assert data.branch_label == "RAD"
        assert data.branch_value == "Radioactivity"
        assert data.kcdb_service_category == "RI/RAD-1.3.2"
        assert data.instrument == "Multiple nuclide source, solution"
        assert data.instrument_method == "Ge detector, multichannel analyzer"
        assert data.source_value == "Multi-radionuclide source"
        assert data.medium_value == "Liquid"
        assert data.nuclide_value == "Co-60"
        assert data.radiation_specification == "10 ml to 500 ml NMIJ/AIST standard cylindrical plastic bottle"
        assert data.international_standard == ""
        assert data.reference_standard == "Comparison with the NMIJ/AIST standard source"
        assert data.radiation_code == "2.1.3.2"

    @pytest.mark.asyncio
    async def test_sources_dosimetry(self) -> None:
        """Test AsyncRadiation.sources() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        sources = await self.radiation.sources(branches[0])
        assert len(sources) == 17

        source, *rest = self.radiation.filter(sources, "Photons")
        assert not rest
        assert source.id == 6
        assert source.label == "6"
        assert source.value == "Photons, high energy"

    @pytest.mark.asyncio
    async def test_sources_neutron(self) -> None:
        """Test AsyncRadiation.sources() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        sources = await self.radiation.sources(branches[0])
        assert len(sources) > 10

        source, *rest = self.radiation.filter(sources, "Mono")
        assert not rest
        assert source.id == 36
        assert source.label == "2"
        assert source.value == "Mono-energetic neutrons"

    @pytest.mark.asyncio
    async def test_sources_radioactivity(self) -> None:
        """Test AsyncRadiation.sources() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        sources = await self.radiation.sources(branches[0])
        assert len(sources) == 3

        source, *rest = self.radiation.filter(sources, "x-rays")
        assert not rest
        assert source.id == 34
        assert source.label == "3"
        assert source.value == "K x-rays"

    @pytest.mark.asyncio
    async def test_sources_physics_branches(self) -> None:
        """Test AsyncRadiation.sources() for General Physics branches."""
        for branch in self.physics_branches:
            sources = await self.radiation.sources(branch)
            assert not sources

    @pytest.mark.asyncio
    async def test_quantities_dosimetry(self) -> None:
        """Test AsyncRadiation.quantities() for Dosimetry branch."""
        branches = self.radiation.filter(self.branches, "Dosimetry")
        assert len(branches) == 1
        quantities = await self.radiation.quantities(branches[0])
        assert len(quantities) == 16

        quantity, *rest = self.radiation.filter(quantities, "X-ray")
        assert not rest
        assert quantity.id == 14
        assert quantity.label == "14"
        assert quantity.value == "X-ray tube voltage"

    @pytest.mark.asyncio
    async def test_quantities_neutron(self) -> None:
        """Test AsyncRadiation.quantities() for Neutron Measurement branch."""
        branches = self.radiation.filter(self.branches, "Neutron")
        assert len(branches) == 1
        quantities = await self.radiation.quantities(branches[0])
        assert len(quantities) == 17

        quantity, *rest = self.radiation.filter(quantities, "^Fluence$")
        assert not rest
        assert quantity.id == 49
        assert quantity.label == "3"
        assert quantity.value == "Fluence"

    @pytest.mark.asyncio
    async def test_quantities_radioactivity(self) -> None:
        """Test AsyncRadiation.quantities() for Radioactivity branch."""
        branches = self.radiation.filter(self.branches, "Radioactivity")
        assert len(branches) == 1
        quantities = await self.radiation.quantities(branches[0])
        assert len(quantities) == 12

        quantity, *rest = self.radiation.filter(quantities, "Activity per unit area")
        assert not rest
        assert quantity.id == 34
        assert quantity.label == "3"
        assert quantity.value == "Activity per unit area"

    @pytest.mark.asyncio
    async def test_quantities_physics_branches(self) -> None:
        """Test AsyncRadiation.quantities() for General Physics branches."""
        for branch in self.physics_branches:
            quantities = await self.radiation.quantities(branch)
            assert not quantities

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.radiation.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.radiation.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = await self.radiation.search()

        self.radiation.timeout = original
