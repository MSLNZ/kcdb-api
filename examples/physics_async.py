"""Asynchronously search the "General Physics" metrology domain of the KCDB."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from msl.kcdb import AsyncPhysics

if TYPE_CHECKING:
    from msl.kcdb.types import MetrologyArea, ResultsPhysics


async def all_cmc_results(country: str) -> tuple[list[MetrologyArea], list[ResultsPhysics]]:
    """Asynchronously get all CMCs for a country."""
    physics = AsyncPhysics()
    areas = await physics.metrology_areas()
    searches = [physics.search(area, countries=country, page_size=1000) for area in areas]
    results = await asyncio.gather(*searches)
    return areas, results


areas, results = asyncio.run(all_cmc_results("DE"))
for area, result in zip(areas, results):
    print(area.label, result)
