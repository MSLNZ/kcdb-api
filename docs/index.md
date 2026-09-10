# Overview
Search the key comparison database, [KCDB](https://www.bipm.org/kcdb/cmc/advanced-search){:target="_blank"}, that is provided by the International Bureau of Weights and Measures, [BIPM](https://www.bipm.org/en/){:target="_blank"}.

## Install
`msl-kcdb` is available at the [Python Package Index](https://pypi.org/project/msl-kcdb/){:target="_blank"}. It can be installed using a variety of package managers

=== "pip"
    ```console
    pip install msl-kcdb
    ```

=== "uv"
    ```console
    uv add msl-kcdb
    ```

=== "poetry"
    ```console
    poetry add msl-kcdb
    ```

=== "pdm"
    ```console
    pdm add msl-kcdb
    ```

## User Guide
The following classes are available to (synchronously) search the three metrology domains

* [ChemistryBiology][msl.kcdb.chemistry_biology.ChemistryBiology] &mdash; Search the Chemistry and Biology database
* [Physics][msl.kcdb.general_physics.Physics] &mdash; Search the General Physics database
* [Radiation][msl.kcdb.ionizing_radiation.Radiation] &mdash; Search the Ionizing Radiation database

and there are asynchronous (use of `async`/`await`) alternatives

* [AsyncChemistryBiology][msl.kcdb.chemistry_biology.AsyncChemistryBiology]
* [AsyncPhysics][msl.kcdb.general_physics.AsyncPhysics]
* [AsyncRadiation][msl.kcdb.ionizing_radiation.AsyncRadiation]

See the [examples][] on how to use these classes to get information from the KCDB. Example scripts are also available in the `msl-kcdb` [repository](https://github.com/MSLNZ/msl-kcdb/tree/main/examples){:target="_blank"}.

The classes are based on version `1.0.13` of the [KCDB XSD Schema](https://www.bipm.org/api/kcdb/cmc/searchData/xsdSchema){:target="_blank"}. Should the KCDB API change, please open an [issue](https://github.com/MSLNZ/msl-kcdb/issues){:target="_blank"}.