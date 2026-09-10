from datetime import date
from http.client import HTTPException

import pytest

from msl.kcdb import AsyncChemistryBiology, ChemistryBiology, Status


class TestChemBio:
    """Test the ChemistryBiology class."""

    def setup_class(self) -> None:
        """Create ChemistryBiology instance."""
        self.chem_bio: ChemistryBiology = ChemistryBiology()  # pyright: ignore[reportUninitializedInstanceVariable]

    def test_analytes(self) -> None:
        """Test ChemistryBiology.analytes()."""
        analytes = self.chem_bio.analytes()
        assert len(analytes) > 100

        analyte, *rest = self.chem_bio.filter(analytes, "^nitrogen$")
        assert not rest
        assert analyte.id == 1
        assert analyte.label == "nitrogen"
        assert analyte.value == "nitrogen"

    def test_categories(self) -> None:
        """Test ChemistryBiology.categories()."""
        categories = self.chem_bio.categories()
        assert len(categories) > 10

        category, *rest = self.chem_bio.filter(categories, "^Biological fluids")
        assert not rest
        assert category.id == 2
        assert category.label == "10"
        assert category.value == "Biological fluids and materials"

    def test_domain(self) -> None:
        """Test ChemistryBiology.DOMAIN class attribute."""
        chem_bio, _, _ = sorted(self.chem_bio.domains())
        assert chem_bio == self.chem_bio.DOMAIN
        assert chem_bio.code == "CHEM-BIO"
        assert chem_bio.name == "Chemistry and Biology"

    def test_metrology_area(self) -> None:
        """Test ChemistryBiology.metrology_areas()."""
        chem_bio, *rest = self.chem_bio.metrology_areas()
        assert not rest
        assert chem_bio.id == 8
        assert chem_bio.label == "QM"
        assert chem_bio.value == "Chemistry and Biology"
        assert chem_bio.domain.code == "CHEM-BIO"
        assert chem_bio.domain.name == "Chemistry and Biology"

    def test_raise_for_status(self) -> None:
        """Test _Response.raise_for_status().

        The KCDB returns a generic (and unhelpful) error message in the HTML body

          "Apologies for the inconvenience (500). Please try again later!"

        even though the client request is bad.
        """
        with pytest.raises(HTTPException, match=r"cmc/searchData/chemistryAndBiology"):
            _ = self.chem_bio.search(countries="Invalid")

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.chem_bio) == "ChemistryBiology(code='CHEM-BIO', name='Chemistry and Biology')"

    def test_search(self) -> None:  # noqa: PLR0915
        """Test ChemistryBiology.search()."""
        chem_bio = self.chem_bio.search(
            analyte="antimony",
            category="5",
            keywords="phase OR multichannel OR water",
            countries="JP",
            public_date_from="2005-01-31",
            public_date_to=date(2024, 6, 30),
            status=Status.PUBLISHED,
        )

        assert str(chem_bio) == (
            "ResultsChemistryBiology(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert chem_bio.version_api_kcdb == "1.0.13"
        assert chem_bio.page_number == 0
        assert chem_bio.page_size == 100
        assert chem_bio.number_of_elements == 1
        assert chem_bio.total_elements == 1
        assert chem_bio.total_pages == 1
        assert len(chem_bio.data) == 1
        data = chem_bio.data[0]
        assert str(data) == "ResultChemistryBiology(id=32770, nmi_code='NMIJ AIST', rmo='APMP')"
        assert data.id == 32770
        assert data.status == "Published"
        assert data.status_date == "2021-01-12"
        assert data.kcdb_code == "APMP-QM-JP-000001GZ-2"
        assert data.domain_code == "CHEM-BIO"
        assert data.metrology_area_label == "QM"
        assert data.rmo == "APMP"
        assert data.country_value == "Japan"
        assert data.nmi_code == "NMIJ AIST"
        assert data.nmi_identifier == 129
        assert data.nmi_name == "National Metrology Institute of Japan"
        assert data.nmi_ror_identifier == "01703db54"
        assert data.nmi_service_code == "5-01-02"
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q1076542"
        assert data.quantity_value == "Mass fraction"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=0.001, unit='µg/kg', upper_limit=10.0)"
        assert data.cmc.lower_limit == 0.001
        assert data.cmc.unit == "µg/kg"
        assert data.cmc.upper_limit == 10.0
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=10.0, unit='%', upper_limit=1.0)"
        assert data.cmc_uncertainty.lower_limit == 10.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_uncertainty.upper_limit == 1.0
        assert data.cmc_base_unit is not None
        assert (
            str(data.cmc_base_unit) == "ResultUnit(lower_limit=1.0000000000000002e-12, unit='kg/kg', upper_limit=1e-08)"
        )
        assert data.cmc_base_unit.lower_limit == 1.0000000000000002e-12
        assert data.cmc_base_unit.unit == "kg/kg"
        assert data.cmc_base_unit.upper_limit == 1e-8
        assert data.cmc_uncertainty_base_unit is not None
        assert (
            str(data.cmc_uncertainty_base_unit)
            == "ResultUnit(lower_limit=1.0000000000000003e-13, unit='dimension 1', upper_limit=1e-10)"
        )
        assert data.cmc_uncertainty_base_unit.lower_limit == 1.0000000000000003e-13
        assert data.cmc_uncertainty_base_unit.unit == "dimension 1"
        assert data.cmc_uncertainty_base_unit.upper_limit == 1e-10
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
        assert data.traceability_source == ""
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2021-01-12"
        assert data.approval_date == "2017-08-30"
        assert data.uncertainty_convention is not None
        assert data.uncertainty_convention.name == "TWO"
        assert data.uncertainty_convention.value == "Two"
        assert data.category_label == 5
        assert data.category_value == "Water"
        assert data.sub_category_label == 1
        assert data.sub_category_value == "Fresh water"
        assert data.kcdb_service_category == "QM-5.1"
        assert data.analyte_matrix == "river water and drinking water"
        assert data.analyte_value == "antimony"
        assert data.crm is not None
        assert str(data.crm) == "ResultUnit(lower_limit=0.0103, unit='µg/kg', upper_limit=0.146)"
        assert data.crm.lower_limit == 0.0103
        assert data.crm.unit == "µg/kg"
        assert data.crm.upper_limit == 0.146
        assert data.crm_uncertainty is not None
        assert str(data.crm_uncertainty) == "ResultUnit(lower_limit=0.0004, unit='µg/kg', upper_limit=0.009)"
        assert data.crm_uncertainty.lower_limit == 0.0004
        assert data.crm_uncertainty.unit == "µg/kg"
        assert data.crm_uncertainty.upper_limit == 0.009
        assert data.mechanism == "NMIJ CRM 7202, NMIJ CRM 7203"
        assert data.crm_confidence_level == 95
        assert data.crm_coverage_factor == 2
        assert data.crm_uncertainty_equation is not None
        assert str(data.crm_uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.crm_uncertainty_equation.equation == ""
        assert data.crm_uncertainty_equation.equation_comment == ""
        assert data.crm_uncertainty_table is not None
        assert (
            str(data.crm_uncertainty_table)
            == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        )
        assert data.crm_uncertainty_table.table_name == ""
        assert data.crm_uncertainty_table.table_rows == 0
        assert data.crm_uncertainty_table.table_cols == 0
        assert data.crm_uncertainty_table.table_comment == ""
        assert data.crm_uncertainty_table.table_contents == "<masked>"
        assert data.crm_uncertainty_mode is not None
        assert data.crm_uncertainty_mode.name == "ABSOLUTE"
        assert data.crm_uncertainty_mode.value == "Absolute"
        assert data.measurement_technique == ""

    # cSpell:ignore measurment
    def test_search_measurement_technique(self) -> None:
        """The KCDB has a spelling mistake in the key name "measurmentTechnique".

        This tests that the correct key-value pair gets created in Python.
        This test will fail if the key name has been updated by the KCDB
        developers or if Finland changed the CMC metadata.
        """
        results = self.chem_bio.search(countries="FI", category="5", analyte="lead")
        assert results.number_of_elements == 1
        result = results.data[0]
        assert result.nmi_code == "MIKES-SYKE"
        assert result.measurement_technique == "Double ID-ICP-MS, Pycnometric density measurement"

    def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.chem_bio.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.chem_bio.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = self.chem_bio.search()

        self.chem_bio.timeout = original


class TestAsyncChemBio:
    """Test the AsyncChemistryBiology class."""

    def setup_class(self) -> None:
        """Create AsyncChemistryBiology instance."""
        self.chem_bio: AsyncChemistryBiology = AsyncChemistryBiology()  # pyright: ignore[reportUninitializedInstanceVariable]

    @pytest.mark.asyncio
    async def test_analytes(self) -> None:
        """Test AsyncChemistryBiology.analytes()."""
        analytes = await self.chem_bio.analytes()
        assert len(analytes) > 100

        analyte, *rest = self.chem_bio.filter(analytes, "^nitrogen$")
        assert not rest
        assert analyte.id == 1
        assert analyte.label == "nitrogen"
        assert analyte.value == "nitrogen"

    @pytest.mark.asyncio
    async def test_categories(self) -> None:
        """Test AsyncChemistryBiology.categories()."""
        categories = await self.chem_bio.categories()
        assert len(categories) > 10

        category, *rest = self.chem_bio.filter(categories, "^Biological fluids")
        assert not rest
        assert category.id == 2
        assert category.label == "10"
        assert category.value == "Biological fluids and materials"

    @pytest.mark.asyncio
    async def test_domain(self) -> None:
        """Test AsyncChemistryBiology.DOMAIN class attribute."""
        chem_bio, _, _ = sorted(await self.chem_bio.domains())
        assert chem_bio == self.chem_bio.DOMAIN
        assert chem_bio.code == "CHEM-BIO"
        assert chem_bio.name == "Chemistry and Biology"

    @pytest.mark.asyncio
    async def test_metrology_area(self) -> None:
        """Test AsyncChemistryBiology.metrology_areas()."""
        chem_bio, *rest = await self.chem_bio.metrology_areas()
        assert not rest
        assert chem_bio.id == 8
        assert chem_bio.label == "QM"
        assert chem_bio.value == "Chemistry and Biology"
        assert chem_bio.domain.code == "CHEM-BIO"
        assert chem_bio.domain.name == "Chemistry and Biology"

    @pytest.mark.asyncio
    async def test_raise_for_status(self) -> None:
        """Test _Response.raise_for_status().

        The KCDB returns a generic (and unhelpful) error message in the HTML body

          "Apologies for the inconvenience (500). Please try again later!"

        even though the client request is bad.
        """
        with pytest.raises(HTTPException, match=r"cmc/searchData/chemistryAndBiology"):
            _ = await self.chem_bio.search(countries="Invalid")

    def test_repr(self) -> None:
        """Test string representation."""
        assert str(self.chem_bio) == "AsyncChemistryBiology(code='CHEM-BIO', name='Chemistry and Biology')"

    @pytest.mark.asyncio
    async def test_search(self) -> None:  # noqa: PLR0915
        """Test AsyncChemistryBiology.search()."""
        chem_bio = await self.chem_bio.search(
            analyte="antimony",
            category="5",
            keywords="phase OR multichannel OR water",
            countries="JP",
            public_date_from="2005-01-31",
            public_date_to=date(2024, 6, 30),
            status=Status.PUBLISHED,
        )

        assert str(chem_bio) == (
            "ResultsChemistryBiology(number_of_elements=1, page_number=0, page_size=100, "
            "total_elements=1, total_pages=1, version_api_kcdb='1.0.13')"
        )

        assert chem_bio.version_api_kcdb == "1.0.13"
        assert chem_bio.page_number == 0
        assert chem_bio.page_size == 100
        assert chem_bio.number_of_elements == 1
        assert chem_bio.total_elements == 1
        assert chem_bio.total_pages == 1
        assert len(chem_bio.data) == 1
        data = chem_bio.data[0]
        assert str(data) == "ResultChemistryBiology(id=32770, nmi_code='NMIJ AIST', rmo='APMP')"
        assert data.id == 32770
        assert data.status == "Published"
        assert data.status_date == "2021-01-12"
        assert data.kcdb_code == "APMP-QM-JP-000001GZ-2"
        assert data.domain_code == "CHEM-BIO"
        assert data.metrology_area_label == "QM"
        assert data.rmo == "APMP"
        assert data.country_value == "Japan"
        assert data.nmi_code == "NMIJ AIST"
        assert data.nmi_identifier == 129
        assert data.nmi_name == "National Metrology Institute of Japan"
        assert data.nmi_ror_identifier == "01703db54"
        assert data.nmi_service_code == "5-01-02"
        assert data.nmi_service_link == ""
        assert data.nmi_wiki_data_identifier == "Q1076542"
        assert data.quantity_value == "Mass fraction"
        assert data.cmc is not None
        assert str(data.cmc) == "ResultUnit(lower_limit=0.001, unit='µg/kg', upper_limit=10.0)"
        assert data.cmc.lower_limit == 0.001
        assert data.cmc.unit == "µg/kg"
        assert data.cmc.upper_limit == 10.0
        assert data.cmc_uncertainty is not None
        assert str(data.cmc_uncertainty) == "ResultUnit(lower_limit=10.0, unit='%', upper_limit=1.0)"
        assert data.cmc_uncertainty.lower_limit == 10.0
        assert data.cmc_uncertainty.unit == "%"
        assert data.cmc_uncertainty.upper_limit == 1.0
        assert data.cmc_base_unit is not None
        assert (
            str(data.cmc_base_unit) == "ResultUnit(lower_limit=1.0000000000000002e-12, unit='kg/kg', upper_limit=1e-08)"
        )
        assert data.cmc_base_unit.lower_limit == 1.0000000000000002e-12
        assert data.cmc_base_unit.unit == "kg/kg"
        assert data.cmc_base_unit.upper_limit == 1e-8
        assert data.cmc_uncertainty_base_unit is not None
        assert (
            str(data.cmc_uncertainty_base_unit)
            == "ResultUnit(lower_limit=1.0000000000000003e-13, unit='dimension 1', upper_limit=1e-10)"
        )
        assert data.cmc_uncertainty_base_unit.lower_limit == 1.0000000000000003e-13
        assert data.cmc_uncertainty_base_unit.unit == "dimension 1"
        assert data.cmc_uncertainty_base_unit.upper_limit == 1e-10
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
        assert data.traceability_source == ""
        assert data.comments == ""
        assert data.group_identifier == ""
        assert data.publication_date == "2021-01-12"
        assert data.approval_date == "2017-08-30"
        assert data.uncertainty_convention is not None
        assert data.uncertainty_convention.name == "TWO"
        assert data.uncertainty_convention.value == "Two"
        assert data.category_label == 5
        assert data.category_value == "Water"
        assert data.sub_category_label == 1
        assert data.sub_category_value == "Fresh water"
        assert data.kcdb_service_category == "QM-5.1"
        assert data.analyte_matrix == "river water and drinking water"
        assert data.analyte_value == "antimony"
        assert data.crm is not None
        assert str(data.crm) == "ResultUnit(lower_limit=0.0103, unit='µg/kg', upper_limit=0.146)"
        assert data.crm.lower_limit == 0.0103
        assert data.crm.unit == "µg/kg"
        assert data.crm.upper_limit == 0.146
        assert data.crm_uncertainty is not None
        assert str(data.crm_uncertainty) == "ResultUnit(lower_limit=0.0004, unit='µg/kg', upper_limit=0.009)"
        assert data.crm_uncertainty.lower_limit == 0.0004
        assert data.crm_uncertainty.unit == "µg/kg"
        assert data.crm_uncertainty.upper_limit == 0.009
        assert data.mechanism == "NMIJ CRM 7202, NMIJ CRM 7203"
        assert data.crm_confidence_level == 95
        assert data.crm_coverage_factor == 2
        assert data.crm_uncertainty_equation is not None
        assert str(data.crm_uncertainty_equation) == "ResultEquation(equation='', equation_comment='')"
        assert data.crm_uncertainty_equation.equation == ""
        assert data.crm_uncertainty_equation.equation_comment == ""
        assert data.crm_uncertainty_table is not None
        assert (
            str(data.crm_uncertainty_table)
            == "ResultTable(table_rows=0, table_cols=0, table_name='', table_comment='')"
        )
        assert data.crm_uncertainty_table.table_name == ""
        assert data.crm_uncertainty_table.table_rows == 0
        assert data.crm_uncertainty_table.table_cols == 0
        assert data.crm_uncertainty_table.table_comment == ""
        assert data.crm_uncertainty_table.table_contents == "<masked>"
        assert data.crm_uncertainty_mode is not None
        assert data.crm_uncertainty_mode.name == "ABSOLUTE"
        assert data.crm_uncertainty_mode.value == "Absolute"
        assert data.measurement_technique == ""

    # cSpell:ignore measurment
    @pytest.mark.asyncio
    async def test_search_measurement_technique(self) -> None:
        """The KCDB has a spelling mistake in the key name "measurmentTechnique".

        This tests that the correct key-value pair gets created in Python.
        This test will fail if the key name has been updated by the KCDB
        developers or if Finland changed the CMC metadata.
        """
        results = await self.chem_bio.search(countries="FI", category="5", analyte="lead")
        assert results.number_of_elements == 1
        result = results.data[0]
        assert result.nmi_code == "MIKES-SYKE"
        assert result.measurement_technique == "Double ID-ICP-MS, Pycnometric density measurement"

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test timeout error message."""
        original = self.chem_bio.timeout

        # Making the timeout value be around 1 second causes a TimeoutError
        # instead of a urllib.error.URLError if it is too small
        self.chem_bio.timeout = 0.9
        with pytest.raises(TimeoutError, match=r"No reply from KCDB server after 0.9 seconds"):
            _ = await self.chem_bio.search()

        self.chem_bio.timeout = original
